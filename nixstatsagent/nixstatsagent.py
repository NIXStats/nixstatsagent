#!/usr/bin/env python

# by Al Nikolov <root@toor.fi.eu.org>


import bz2
import ConfigParser
import glob
import httplib
import imp
try:
    import json as serialize
except ImportError:
    import simplejson as serialize
import logging
import os
import pickle
import Queue
import signal
import StringIO
import subprocess
import sys
import threading
import time
import types


ini_files = (
    os.path.join('/etc', 'nixstats.ini'),
    os.path.abspath('nixstats.ini'),
)

def run_agent():
    Agent().run()

def _plugin_name(plugin):
    if isinstance(plugin, basestring):
        basename = os.path.basename(plugin)
        return os.path.splitext(basename)[0]
    else:
        return plugin.__name__


class Agent:
    
    execute = Queue.Queue()
    metrics = Queue.Queue()
    data = Queue.Queue()
    shutdown = False

    def __init__(self):
        """
        Initialize internal strictures
        """
        self._config_init()
        self._logging_init()
        self._plugins_init()
        self._data_worker_init()
        self._dump_config()

    def _config_init(self):
        """
        Initialize configuration object
        """
        defaults = {
            'max_data_span': 60,
            'max_data_age': 60 * 10,
            'logging_level': logging.WARNING,
            'threads': 100,
            'ttl': 60,
            'interval': 60,
            'plugins': 'plugins',
            'enabled': 'no',
            'subprocess': 'no',
            'user': '',
            'server': '',
            'api_host': 'api.nixstats.com',
            'api_path': '/v2/server/poll',
        }
        sections = [
            'agent',
            'execution',
            'data',
        ]
        config = ConfigParser.RawConfigParser(defaults)
        config.read(ini_files)
        self.config = config
        for section in sections:
            self._config_section_create(section)

    def _config_section_create(self, section):
        """
        Create an addition section in the configuration object
        """
        if not self.config.has_section(section):
            self.config.add_section(section)

    def _logging_init(self):
        """
        Initialize logging faculty
        """
        level = self.config.getint('agent', 'logging_level')
        logging.basicConfig(level=level)
        logging.info('Agent logging_level %i', level)

    def _plugins_init(self):
        """
        Discover the plugins
        """
        logging.info('_plugins_init')
        path = self.config.get('agent', 'plugins')
        filenames = glob.glob(os.path.join(path, '*.py'))
        sys.path.insert(0, path)
        self.schedule = {}
        for filename in filenames:
            name = _plugin_name(filename)
            if name == 'plugins':
                continue
            self._config_section_create(name)
            if self.config.getboolean(name, 'enabled'):
                if self.config.getboolean(name, 'subprocess'):
                    self.schedule[filename] = 0
                else:
                    fp, pathname, description = \
                        imp.find_module(name)
                    module = None
                    try:
                        module = imp.load_module(
                                    name, fp, pathname, description)
                    finally:
                        # Since we may exit via an exception, close fp explicitly.
                        if fp:
                            fp.close()
                    if module:
                        self.schedule[module] = 0
                    else:
                        logging.error('import_plugin:%s:%s', name, sys.exc_type)

        
    def _subprocess_execution(self, task):
        """
        Execute /task/ in a subprocess
        """
        process = subprocess.Popen((sys.executable, task, ini_file), 
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            universal_newlines=True)
        logging.info('%s:process:%i', threading.currentThread(), process.pid)
        interval = self.config.getint('execution', 'interval')
        name = _plugin_name(task)
        ttl = self.config.getint(name, 'ttl')
        ticks = ttl / interval or 1
        process.poll()
        while process.returncode is None and ticks > 0:
            logging.info('%s:tick:%i', threading.currentThread(), ticks)
            time.sleep(interval)
            ticks -= 1
            process.poll()
        if process.returncode is None:
            logging.error('%s:kill:%i', threading.currentThread(), process.pid)
            os.kill(process.pid, signal.SIGTERM)
        stdout, stderr = process.communicate()
        if process.returncode != 0 or stderr:
            logging.error('%s:%s:%s:%s', threading.currentThread(), task, process.returncode, stderr)
        if stdout:
            ret = pickle.loads(stdout)
        else:
            ret = None
        return ret

    def _execution(self):
        """
        Take queued execution requests, execute plugins and queue the results
        """
        while True:
            if self.shutdown:
                logging.info('%s:shutdown', threading.currentThread())
                break
            logging.info('%s:exec_queue:%i', threading.currentThread(), self.execute.qsize())
            try:
                task = self.execute.get_nowait()
            except Queue.Empty:
                break
            logging.info('%s:task:%s', threading.currentThread(), task)
            name = _plugin_name(task)
            ts = time.time()
            if isinstance(task, basestring):
                payload = self._subprocess_execution(task)
            else:
                try:
                    payload = task.Plugin().run(self.config)
                except:
                    logging.exception('plugin_exception')
                    payload = { 'exception': str(sys.exc_info()[0]) }
            self.metrics.put({
                'ts': ts, 
                'task': task,
                'name': name, 
                'payload': payload,
            })
            self.hire.release()

    def _data(self):
        """
        Take and collect data, send and clean if needed
        """
        logging.info('%s', threading.currentThread())
        collection = []
        while True:
            if self.shutdown:
                logging.info('%s:shutdown', threading.currentThread())
                break
            logging.info('%s:data_queue:%i:collection:%i', threading.currentThread(), self.data.qsize(), len(collection))
            while self.data.qsize():
                collection.append(self.data.get_nowait())
            if collection:
                first_ts = min((e['ts'] for e in collection))
                last_ts = max((e['ts'] for e in collection))
                now = time.time()
                max_age = self.config.getint('agent', 'max_data_age')
                max_span = self.config.getint('agent', 'max_data_span')
                send = False
                server = self.config.get('agent', 'server')
                user = self.config.get('agent', 'user')
                if last_ts - first_ts > max_span:
                    logging.info('Max data span')
                    send = True
                elif now - first_ts > max_age:
                    logging.info('Max data age')
                    send = True
                if send:
                    headers = {
                        "Content-type": "application/json",
                        "Authorization":
                            'ApiKey %s:%s' % (
                                self.config.get('agent', 'user'),
                                self.config.get('agent', 'server')),
                    }
                    clean = False
                    logging.info('collection:%s', collection)
                    if not server and not user:
                        logging.info('Empty server/user, but need to send: %s', serialize.dumps(collection))
                        clean = True
                    else:
                        connection = httplib.HTTPSConnection(self.config.get('data', 'api_host'))
                        connection.request('PUT', self.config.get('data', 'api_path'),
                             bz2.compress(str(serialize.dumps(collection)) + "\n"),
                             headers=headers)
                        response = connection.getresponse()
                        logging.info('%s', response)
                        connection.close()
                        if response.status == 200:
                            clean = True 
                    if clean:
                        collection = []
            time.sleep(self.config.getint('data', 'interval'))
    
    def _data_worker_init(self):
        """
        Initialize data worker thread
        """
        logging.info('_data_worker_init')
        threading.Thread(target=self._data).start()

    def  _dump_config(self):
        """
        Dumps configuration object
        """
        buf = StringIO.StringIO()
        self.config.write(buf)
        logging.info('Config: %s', buf.getvalue())

    def run(self):
        """
        Start all the worker threads
        """
        logging.info('Agent main loop')
        interval = self.config.getint('agent', 'interval')
        self.hire = threading.Semaphore(
            self.config.getint('execution', 'threads'))
        try:
            while True:
                now = time.time()
                logging.info('%i threads', threading.activeCount())
                while self.metrics.qsize():
                    metrics = self.metrics.get_nowait()
                    name = metrics['name']
                    logging.info('metrics:%s', name)
                    plugin = metrics.get('task')
                    if plugin:
                        self.schedule[plugin] = \
                            now + self.config.getint(name, 'interval')
                        if isinstance(plugin, types.ModuleType):
                            metrics['task'] = plugin.__file__
                    self.data.put(metrics)
                execute = [what
                    for what, when in self.schedule.items() 
                        if when <= now
                ]
                for name in execute:
                    logging.info('scheduling:%s', name)
                    del self.schedule[name]
                    self.execute.put(name)
                    if self.hire.acquire(False):
                        thread = threading.Thread(target=self._execution)
                        thread.start()
                        logging.info('new_execution_worker_thread:%s', thread)
                    else:
                        logging.warning('threads_capped')
                        self.metrics.put({
                            'ts': now,
                            'name': 'agent_internal',
                            'payload': {
                                'threads_capping': 
                                    self.config.getint('execution', 'threads')}
                        })
                
                time.sleep(interval)
        except KeyboardInterrupt:
            logging.warning(sys.exc_info()[0])
            while True:
                wait_for = [thread 
                    for thread in threading.enumerate() 
                        if not thread.isDaemon() and 
                           not isinstance(thread, threading._MainThread)]
                logging.info('Shutdown, waiting for %i threads to exit', len(wait_for))
                logging.info('Remaining threads: %s', threading.enumerate())
                if len(wait_for) == 0:
                    sys.exit(0)
                self.shutdown = True
                time.sleep(interval)
            

if __name__ == '__main__':
    run_agent()

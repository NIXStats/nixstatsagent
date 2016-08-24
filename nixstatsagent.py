#!/usr/bin/env python

# by Al Nikolov <root@toor.fi.eu.org>


import bz2
import ConfigParser
import glob
import httplib
import imp
import json
import logging
import os
import pickle
import Queue
import signal
import StringIO
import subprocess
import sys
import time
import threading


def run_agent():
    Agent().run()

def _plugin_name(plugin):
    if isinstance(plugin, basestring):
        basename = os.path.basename(plugin)
        return os.path.splitext(basename)[0]
    else:
        return plugin.__name__


class Agent():
    
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
            'enabled': False,
            'subprocess': False,
            'user': '',
            'server': '',
        }
        sections = [
            'agent',
            'execution',
            'data',
        ]
        config = ConfigParser.RawConfigParser(defaults)
        config.read('nixstats.ini')
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
        self.plugins = []
        for filename in filenames:
            name = _plugin_name(filename)
            self._config_section_create(name)
            if self.config.getboolean(name, 'enabled'):
                if self.config.getboolean(name, 'subprocess'):
                    self.plugins.append(filename)
                else:
                    fp, pathname, description = \
                        imp.find_module(name, [path])
                    if fp:
                        self.plugins.append(
                            imp.load_module(
                                name, fp, pathname, description))
                    else:
                        logging.error('import_plugin:%s:', name)
        
    def _subprocess_execution(self, task):
        """
        Execute /task/ in a subprocess
        """
        process = subprocess.Popen((sys.executable, task), 
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
        return pickle.loads(stdout) if stdout else None

    def _execution(self):
        """
        Take queued execution requests, execute plugins and queue the results
        """
        logging.info('%s', threading.currentThread())
        while True:
            if self.shutdown:
                logging.info('%s:shutdown', threading.currentThread())
                break
            logging.info('%s:queue:%i', threading.currentThread(), self.execute.qsize())
            try:
                task = self.execute.get_nowait()
            except Queue.Empty:
                logging.info('%s:empty', threading.currentThread())
                break
            logging.info('%s:task:%s', threading.currentThread(), task)
            name = _plugin_name(task)
            ts = time.time()
            if isinstance(task, basestring):
                payload = self._subprocess_execution(task)
            else:
                payload = task.run()
            self.metrics.put({
                'ts': ts, 
                'task': task,
                'name': name, 
                'payload': payload,
            })
            self.execute.task_done()

    def _schedule_worker(self, task):
        """
        Add task to the execution queue
        """
        logging.info('%s:scheduling:%s', threading.currentThread(), task)
        self.execute.put(task)
        cap = self.config.getint('execution', 'threads')
        if cap >= threading.activeCount() and  \
                self.execute.qsize() > 0:
            logging.info('%s:new_execution_worker_thread', threading.currentThread())
            thread = threading.Thread(target=self._execution)
            thread.start()
        else:
            logging.warning('%s:threads_capped', threading.currentThread())
            self.metrics.put({
                'ts': time.time(),
                'name': 'agent_internal',
                'payload': {'threads_capping': cap}
            })
       
    def _data(self):
        """
        Take and collect data, send and clean if needed
        """
        logging.info('%s', threading.currentThread())
        while True:
            if self.shutdown:
                logging.info('%s:shutdown', threading.currentThread())
                break
            logging.info('%s:queue:%i', threading.currentThread(), self.data.qsize())
            while self.data.qsize():
                self.collection.append(self.data.get_nowait())
            logging.info('%s:collection:%i', threading.currentThread(), len(self.collection))
            if self.collection:
                first_ts = min((e['ts'] for e in self.collection))
                last_ts = max((e['ts'] for e in self.collection))
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
                    if not server and not user:
                        logging.info('Empty server/user, but need to send: %s', self.collection)
                        clean = True
                    else:
                        connection = httplib.HTTPSConnection('api.nixstats.com')
                        connection.request('PUT', '/v2/server/poll',
                             bz2.compress(str(json.dumps(self.collection)) + "\n"),
                             headers=headers)
                        response = connection.getresponse()
                        logging.info('%s', response)
                        connection.close()
                        if response.status == 200:
                            clean = True 
                    if clean:
                        self.collection = []
            time.sleep(self.config.getint('data', 'interval'))
    
    def _data_worker_init(self):
        """
        Initialize data worker thread
        """
        logging.info('_data_worker_init')
        self.collection = []
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
        for plugin in self.plugins:
            logging.info('%s:initial_execution', plugin)
            self._schedule_worker(plugin)
        try:
            while True:
                logging.info('%i threads', threading.activeCount())
                while self.metrics.qsize():
                    metrics = self.metrics.get_nowait()
                    if metrics:
                        name = metrics['name']
                        logging.info('metrics:%s', name)
                        plugin = metrics.get('task')
                        if plugin:
                            interval = self.config.getint(name, 'interval')
                            timer = threading.Timer(interval=interval, 
                                function=self._schedule_worker, 
                                args=(plugin,))
                            timer.name = plugin
                            timer.daemon = True
                            timer.start()
                        self.data.put(metrics)
                        self.metrics.task_done()
                time.sleep(interval)
        except KeyboardInterrupt:
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

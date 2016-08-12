#!/usr/bin/env python

# by Al Nikolov <root@toor.fi.eu.org>


import bz2
import ConfigParser
import glob
import httplib
import json
import logging
import os
import pickle
import Queue
import signal
import StringIO
import subprocess
import time
import threading


def run_agent():
    Agent().run()


def _plugin_name(filename):
    basename = os.path.basename(filename)
    return os.path.splitext(basename)[0]


class Agent():
    
    def __init__(self):
        """
        Initialize internal strictures
        """
        self._config_init()
        self._logging_init()
        self._plugins_init()
        self._execution_workers_init()
        self._metrics_worker_init()
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
            'threads': 8,
            'ttl': 60,
            'interval': 60,
            'plugins': 'plugins',
            'enabled': False,
            'user': '',
            'server': '',
        }
        sections = [
            'agent',
            'execution',
            'metrics',
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
        plugins = glob.glob(os.path.join(
            self.config.get('agent', 'plugins'), '*.py'))
        self.plugins = []
        for plugin in plugins:
            name = _plugin_name(plugin)
            self._config_section_create(name)
            if self.config.get(name, 'enabled'):
                self.plugins.append(plugin)
        
    def _execution(self):
        """
        Take queued execution requests, execute plugins and queue the results
        """
        logging.info('%s', threading.currentThread())
        while True:
            logging.info('%s:queue:%i', threading.currentThread(), self.execute.qsize())
            task = self.execute.get()
            logging.info('%s:task:%s', threading.currentThread(), task)
            name = _plugin_name(task)
            ts = time.time()
            process = subprocess.Popen((task,), 
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            returncode = None
            interval = self.config.getint('execution', 'interval')
            ttl = self.config.getint(name, 'ttl')
            ticks = ttl / interval or 1
            for _ in range(ticks):
                logging.info('%s:tick', threading.currentThread())
                returncode = process.poll()
                if returncode is not None:
                    break
                time.sleep(interval)
            if returncode is None:
                logging.error('%s:kill:%i', threading.currentThread(), process.pid)
                os.kill(process.pid, signal.SIGKILL)
            stdout, stderr = process.communicate()
            if returncode != 0 or stderr:
                logging.error('%s:%s:%s:%s', threading.currentThread(), task, returncode, stderr)
            payload = pickle.loads(stdout) if stdout else None
            self.metrics.put({
                'ts': ts, 
                'task': task,
                'name': name, 
                'payload': payload,
            })
            self.execute.task_done()

    def _execution_workers_init(self):
        """
        Initialize execution worker threads, their queues and initial tasks
        """
        logging.info('_execution_workers_init')
        self.execute = Queue.Queue()
        self.metrics = Queue.Queue()
        self._execution_worker_threads = []
        for _ in range(self.config.getint('execution', 'threads')):
            thread = threading.Thread(target=self._execution, name='execution')
            thread.daemon = True
            self._execution_worker_threads.append(thread)
        for plugin in self.plugins:
            logging.info('%s:initial', plugin)
            self.execute.put(plugin)
            
    def _schedule_worker(self, task):
        """
        Add task to the execution queue
        """
        logging.info('%s', threading.currentThread())
        self.execute.put(task)
            
    def _metrics(self):
        """
        Take execution results to data collection and reschedule execution
        """
        logging.info('%s', threading.currentThread())
        while True:
            metrics = self.metrics.get()
            logging.info('%s:metrics:%s', threading.currentThread(), metrics)
            plugin = metrics['task']
            name = metrics['name']
            interval = self.config.getint(name, 'interval')
            timer = threading.Timer(interval=interval, 
                function=self._schedule_worker, args=(plugin,))
            timer.name = plugin
            timer.daemon = True
            timer.start()
            self.data.put(metrics)
            self.metrics.task_done()
        
    def _metrics_worker_init(self):
        """
        Initialize metrics worker thread
        """
        logging.info('_metrics_worker_init')
        self.data = Queue.Queue()
        self._metrics_worker_thread = threading.Thread(
            target=self._metrics, name='mertics')
        self._metrics_worker_thread.daemon = True
        
    def _data(self):
        """
        Take and collect data, send and clean if needed
        """
        logging.info('%s', threading.currentThread())
        while True:
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
        self._data_worker_thread = threading.Thread(
            target=self._data, name='data')
        self._data_worker_thread.daemon = True

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
        self._data_worker_thread.start()
        self._metrics_worker_thread.start()
        for thread in self._execution_worker_threads:
            thread.start()
        while True:
            time.sleep(self.config.getint('agent', 'interval'))


if __name__ == '__main__':
    run_agent()

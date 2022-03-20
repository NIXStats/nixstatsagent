#!/usr/bin/env python
# -*- coding: utf-8; tab-width: 4; indent-tabs: nil; -*-
# by Al Nikolov <roottoorfieuorg@gmail.com>
from __future__ import print_function
import bz2
import sys
if sys.version_info >= (3,):
    try:
        from past.builtins import basestring
    except ImportError:
        basestring = str
    import configparser
    import http.client
    from queue import Queue, Empty
    import io
else:
    import ConfigParser
    import httplib
    import StringIO
    from Queue import Queue, Empty

import glob
import imp
try:
    import json
except ImportError:
    import simplejson as json
import logging
import os
import pickle
import signal
import socket
import subprocess
import threading
import time
import types
import urllib

try:
    from urllib.parse import urlparse, urlencode
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError
except ImportError:
    from urlparse import urlparse
    from urllib import urlencode
    from urllib2 import urlopen, Request, HTTPError

__version__ = '1.2.17'
__FILEABSDIRNAME__ = os.path.dirname(os.path.abspath(__file__))

ini_files = (
    os.path.join('/etc', 'nixstats.ini'),
    os.path.join('/etc', 'nixstats-token.ini'),
    os.path.join(os.path.dirname(__FILEABSDIRNAME__), 'nixstats.ini'),
    os.path.join(os.path.dirname(__FILEABSDIRNAME__), 'nixstats-token.ini'),
    os.path.abspath('nixstats.ini'),
    os.path.abspath('nixstats-token.ini'),
)

if sys.platform == 'win32':
    ini_files = (
        os.path.join(__FILEABSDIRNAME__, 'nixstats.ini'),
        os.path.join(__FILEABSDIRNAME__, 'nixstats-token.ini'),
    )

def info():
    '''
    Return string with info about nixstatsagent:
        - version
        - plugins enabled
        - absolute path to plugin directory
        - server id from configuration file
    '''
    agent = Agent(dry_instance=True)
    plugins_path = agent.config.get('agent', 'plugins')

    plugins_enabled = agent._get_plugins(state='enabled')

    return '\n'.join((
        'Version: %s' % __version__,
        'Plugins enabled: %s' % ', '.join(plugins_enabled),
        'Plugins directory: %s' % plugins_path,
        'Server: %s' % agent.config.get('agent', 'server'),
    ))


def hello(proto='https'):
    user_id = sys.argv[1]
    agent = Agent(dry_instance=True)
    if len(sys.argv) > 2:
        token_filename = sys.argv[2]
    else:
        token_filename = os.path.join(__FILEABSDIRNAME__, 'nixstats-token.ini')
    if len(sys.argv) > 3:
        unique_id = sys.argv[3]
    else:
        unique_id = ''
    if '_' in user_id:
        server_id = user_id.split('_')[1]
        user_id = user_id.split('_')[0]
    else:
        try:
            hostname = os.uname()[1]
        except AttributeError:
            hostname = socket.getfqdn()
        server_id = urlopen(
            proto + '://' + agent.config.get('data', 'api_host') + '/hello.php',
            data=urlencode({
                    'user': user_id,
                    'hostname': hostname,
                    'unique_id': unique_id
            }).encode("utf-8")
           ).read().decode()
    if len(server_id) == 24:
        print('Got server_id: %s' % server_id)
        open(token_filename, 'w').\
            write('[DEFAULT]\nuser=%s\nserver=%s\n' % (user_id, server_id))
    else:
        print('Could not retrieve server_id: %s' % server_id)


# def run_agent():
#     Agent().run()


def _plugin_name(plugin):
    if isinstance(plugin, basestring):
        basename = os.path.basename(plugin)
        return os.path.splitext(basename)[0]
    else:
        return plugin.__name__


def test_plugins(plugins=[]):
    '''
    Test specified plugins and print their data output after single check.
    If plugins list is empty test all enabled plugins.
    '''
    agent = Agent(dry_instance=True)
    plugins_path = agent.config.get('agent', 'plugins')
    if plugins_path not in sys.path:
        sys.path.insert(0, plugins_path)

    if not plugins:
        plugins = agent._get_plugins(state='enabled')
        print('Check all enabled plugins: %s' % ', '.join(plugins))

    for plugin_name in plugins:
        print('%s:' % plugin_name)

        try:
            fp, pathname, description = imp.find_module(plugin_name)
        except Exception as e:
            print('Find error:', e)
            continue

        try:
            module = imp.load_module(plugin_name, fp, pathname, description)
        except Exception as e:
            print('Load error:', e)
            continue
        finally:
            # Since we may exit via an exception, close fp explicitly.
            if fp:
                fp.close()

        try:
            payload = module.Plugin().run(agent.config)
            print(json.dumps(payload, indent=4, sort_keys=True))
        except Exception as e:
            print('Execution error:', e)


class Agent:
    execute = Queue()
    metrics = Queue()
    data = Queue()
    cemetery = Queue()
    shutdown = False

    def __init__(self, dry_instance=False):
        '''
        Initialize internal strictures
        '''
        self._config_init()

        # Cache for plugins so they can store values related to previous checks
        self.plugins_cache = {}

        if dry_instance:
            return

        self._logging_init()
        self._plugins_init()
        self._data_worker_init()
        self._dump_config()

    def _config_init(self):
        '''
        Initialize configuration object
        '''
        defaults = {
            'max_data_span': 60,
            'max_data_age': 60 * 10,
            'logging_level': logging.INFO,
            'threads': 100,
            'ttl': 60,
            'interval': 60,
            'plugins': os.path.join(__FILEABSDIRNAME__, 'plugins'),
            'enabled': 'no',
            'subprocess': 'no',
            'user': '',
            'server': '',
            'api_host': 'api.nixstats.com',
            'api_path': '/v2/server/poll',
            'log_file': '/var/log/nixstatsagent.log',
            'log_file_mode': 'a',
            'max_cached_collections': 10,
        }
        sections = [
            'agent',
            'execution',
            'data',
        ]
        if sys.version_info >= (3,):
            config = configparser.RawConfigParser(defaults)
        else:
            config = ConfigParser.RawConfigParser(defaults)
        config.read(ini_files)
        self.config = config
        for section in sections:
            self._config_section_create(section)
            if section == 'data':
                self.config.set(section, 'interval', 1)
            if section == 'agent':
                self.config.set(section, 'interval', .5)

    def _config_section_create(self, section):
        '''
        Create an addition section in the configuration object
        if it's not exists
        '''
        if not self.config.has_section(section):
            self.config.add_section(section)

    def _logging_init(self):
        '''
        Initialize logging faculty
        '''
        level = self.config.getint('agent', 'logging_level')

        log_file = self.config.get('agent', 'log_file')

        log_file_mode = self.config.get('agent', 'log_file_mode')
        if log_file_mode in ('w', 'a'):
            pass
        elif log_file_mode == 'truncate':
            log_file_mode = 'w'
        elif log_file_mode == 'append':
            log_file_mode = 'a'
        else:
            log_file_mode = 'a'

        if log_file == '-':
            logging.basicConfig(level=level)  # Log to sys.stderr by default
        else:
            try:
                logging.basicConfig(filename=log_file, filemode=log_file_mode, level=level, format="%(asctime)-15s  %(levelname)s    %(message)s")
            except IOError as e:
                logging.basicConfig(level=level)
                logging.info('IOError: %s', e)
                logging.info('Drop logging to stderr')

        logging.info('Agent logging_level %i', level)

    def _plugins_init(self):
        '''
        Discover the plugins
        '''
        logging.info('_plugins_init')
        plugins_path = self.config.get('agent', 'plugins')
        filenames = glob.glob(os.path.join(plugins_path, '*.py'))
        if plugins_path not in sys.path:
            sys.path.insert(0, plugins_path)
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
                    fp, pathname, description = imp.find_module(name)
                    try:
                        module = imp.load_module(name, fp, pathname, description)
                    except Exception:
                        module = None
                        logging.error('import_plugin_exception:%s', str(sys.exc_info()[0]))
                    finally:
                        # Since we may exit via an exception, close fp explicitly.
                        if fp:
                            fp.close()
                    if module:
                        self.schedule[module] = 0
                    else:
                        logging.error('import_plugin:%s', name)

    def _subprocess_execution(self, task):
        '''
        Execute /task/ in a subprocess
        '''
        process = subprocess.Popen((sys.executable, task),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            universal_newlines=True)
        logging.debug('%s:process:%i', threading.currentThread(), process.pid)
        interval = self.config.getint('execution', 'interval')
        name = _plugin_name(task)
        ttl = self.config.getint(name, 'ttl')
        ticks = ttl / interval or 1
        process.poll()
        while process.returncode is None and ticks > 0:
            logging.debug('%s:tick:%i', threading.currentThread(), ticks)
            time.sleep(interval)
            ticks -= 1
            process.poll()
        if process.returncode is None:
            logging.error('%s:kill:%i', threading.currentThread(), process.pid)
            os.kill(process.pid, signal.SIGTERM)
        stdout, stderr = process.communicate()
        if process.returncode != 0 or stderr:
            logging.error('%s:%s:%s:%s', threading.currentThread(),
                task, process.returncode, stderr)
        if stdout:
            ret = pickle.loads(stdout)
        else:
            ret = None
        return ret

    def _execution(self):
        '''
        Take queued execution requests, execute plugins and queue the results
        '''
        while True:
            if self.shutdown:
                logging.info('%s:shutdown', threading.currentThread())
                break
            logging.debug('%s:exec_queue:%i', threading.currentThread(), self.execute.qsize())
            try:
                task = self.execute.get_nowait()
            except Empty:
                break
            logging.debug('%s:task:%s', threading.currentThread(), task)
            name = _plugin_name(task)
            try:
                interval = self.config.get(name, 'interval')
            except:
                interval = 60
            ts = time.time()
            if isinstance(task, basestring):
                payload = self._subprocess_execution(task)
            else:
                try:
                    # Setup cache for plugin instance
                    # if name not in self.plugins_cache.iterkeys():
                    #     self.plugins_cache[name] = []
                    self.plugins_cache.update({
                        name: self.plugins_cache.get(name, [])
                    })

                    plugin = task.Plugin(agent_cache=self.plugins_cache[name])
                    payload = plugin.run(self.config)
                except Exception:
                    logging.exception('plugin_exception')
                    payload = {'exception': str(sys.exc_info()[0])}
            self.metrics.put({
                'ts': ts,
                'task': task,
                'name': name,
                'interval': interval,
                'payload': payload,
            })
        self.cemetery.put(threading.currentThread())
        self.hire.release()


    def _data(self):
        '''
        Take and collect data, send and clean if needed
        '''
        logging.info('%s', threading.currentThread())
        api_host = self.config.get('data', 'api_host')
        api_path = self.config.get('data', 'api_path')
        max_age = self.config.getint('agent', 'max_data_age')
        max_span = self.config.getint('agent', 'max_data_span')
        server = self.config.get('agent', 'server')
        user = self.config.get('agent', 'user')
        interval = self.config.getint('data', 'interval')
        max_cached_collections = self.config.get('agent', 'max_cached_collections')
        cached_collections = []
        collection = []
        while True:
            loop_ts = time.time()
            if self.shutdown:
                logging.info('%s:shutdown', threading.currentThread())
                break
            logging.debug('%s:data_queue:%i:collection:%i',
                threading.currentThread(), self.data.qsize(), len(collection))
            while self.data.qsize():
                try:
                    collection.append(self.data.get_nowait())
                except Exception as e:
                    logging.error('Data queue error: %s' % e)
            if collection:
                first_ts = min((e['ts'] for e in collection))
                last_ts = max((e['ts'] for e in collection))
                now = time.time()
                send = False
                if last_ts - first_ts >= max_span:
                    logging.debug('Max data span')
                    send = True
                    clean = False
                elif now - first_ts >= max_age:
                    logging.warning('Max data age')
                    send = True
                    clean = True
                if send:
                    headers = {
                        "Content-type": "application/json",
                        "Authorization": "ApiKey %s:%s" % (user, server),
                    }
                    logging.debug('collection: %s',
                        json.dumps(collection, indent=2, sort_keys=True))
                    if not (server and user):
                        logging.warning('Empty server or user, nowhere to send.')
                        clean = True
                    else:

                        try:
                            if sys.version_info >= (3,):
                                connection = http.client.HTTPSConnection(api_host, timeout=15)
                            else:
                                connection = httplib.HTTPSConnection(api_host, timeout=15)

                            # Trying to send cached collections if any
                            if cached_collections:
                                logging.info('Sending cached collections: %i', len(cached_collections))
                                while cached_collections:
                                    connection.request('PUT', '%s?version=%s' % (api_path, __version__),
                                            cached_collections[0],
                                            headers=headers)
                                    response = connection.getresponse()
                                    response.read()
                                    if response.status == 200:
                                        del cached_collections[0]  # Remove just sent collection
                                        logging.debug('Successful response: %s', response.status)
                                    else:
                                        raise ValueError('Unsuccessful response: %s' % response.status)
                                logging.info('All cached collections sent')

                            # Send recent collection (reuse existing connection)
                            connection.request('PUT', '%s?version=%s' % (api_path, __version__),
                                    bz2.compress(str(json.dumps(collection)+"\n").encode()),
                                    headers=headers)
                            response = connection.getresponse()
                            response.read()

                            if response.status == 200:
                                logging.debug('Successful response: %s', response.status)
                                clean = True
                            else:
                                raise ValueError('Unsuccessful response: %s' % response.status)
                        except Exception as e:
                            logging.error('Failed to submit collection: %s' % e)

                            # Store recent collection in cached_collections if send failed
                            if max_cached_collections > 0:
                                if len(cached_collections) >= max_cached_collections:
                                    del cached_collections[0]  # Remove oldest collection
                                    logging.info('Reach max_cached_collections (%s): oldest cached collection dropped',
                                        max_cached_collections)
                                logging.info('Cache current collection to resend next time')
                                cached_collections.append(bz2.compress(str(json.dumps(collection)+"\n").encode()))
                                collection = []
                        finally:
                            connection.close()
                    if clean:
                        collection = []
            sleep_interval = interval - (time.time() - loop_ts)
            if sleep_interval > 0:
                time.sleep(sleep_interval)

    def _data_worker_init(self):
        '''
        Initialize data worker thread
        '''
        logging.info('_data_worker_init')
        threading.Thread(target=self._data).start()

    def _dump_config(self):
        '''
        Dumps configuration object
        '''
        if sys.version_info >= (3,):
            buf = io.StringIO()
        else:
            buf = StringIO.StringIO()

        self.config.write(buf)
        logging.info('Config: %s', buf.getvalue())

    def _get_plugins(self, state='enabled'):
        '''
        Return list with plugins names
        '''
        plugins_path = self.config.get('agent', 'plugins')
        plugins = []
        for filename in glob.glob(os.path.join(plugins_path, '*.py')):
            plugin_name = _plugin_name(filename)
            if plugin_name == 'plugins':
                continue
            self._config_section_create(plugin_name)

            if state == 'enabled':
                if self.config.getboolean(plugin_name, 'enabled'):
                    plugins.append(plugin_name)
            elif state == 'disabled':
                if not self.config.getboolean(plugin_name, 'enabled'):
                    plugins.append(plugin_name)

        return plugins


    def _rip(self):
        '''
        Join with dead workers
        Workaround for https://bugs.python.org/issue37788
        '''
        logging.debug('cemetery:%i', self.cemetery.qsize())
        while True:
            try:
                thread = self.cemetery.get_nowait()
            except Empty:
                break
            logging.debug('joining:%s', thread)
            thread.join()


    def run(self):
        '''
        Start all the worker threads
        '''
        logging.info('Agent main loop')
        interval = self.config.getfloat('agent', 'interval')
        self.hire = threading.Semaphore(
            self.config.getint('execution', 'threads'))
        try:
            while True:
                self._rip()
                now = time.time()
                logging.debug('%i threads', threading.activeCount())
                while self.metrics.qsize():
                    metrics = self.metrics.get_nowait()
                    name = metrics['name']
                    logging.debug('metrics:%s', name)
                    plugin = metrics.get('task')
                    if plugin:
                        self.schedule[plugin] = \
                            int(now) + self.config.getint(name, 'interval')
                        if isinstance(plugin, types.ModuleType):
                            metrics['task'] = plugin.__file__
                    self.data.put(metrics)
                execute = [
                    what
                    for what, when in self.schedule.items()
                    if when <= now
                ]
                for name in execute:
                    logging.debug('scheduling:%s', name)
                    del self.schedule[name]
                    self.execute.put(name)
                    if self.hire.acquire(False):
                        try:
                            thread = threading.Thread(target=self._execution)
                            thread.start()
                            logging.debug('new_execution_worker_thread:%s', thread)
                        except Exception as e:
                            logging.warning('Can not start new thread: %s', e)
                    else:
                        logging.warning('threads_capped')
                        self.metrics.put({
                            'ts': now,
                            'name': 'agent_internal',
                            'payload': {
                                'threads_capping':
                                    self.config.getint('execution', 'threads')}
                        })
                sleep_interval = .5-(time.time()-now)
                if sleep_interval > 0:
                    time.sleep(sleep_interval)
                else:
                    logging.warning('not enough time to start worker threads')
                    time.sleep(.1)

        except KeyboardInterrupt:
            logging.warning(sys.exc_info()[0])
            logging.info('Shutting down')
            self._rip()
            wait_for = True
            while wait_for:
                all_threads = threading.enumerate()
                logging.info('Remaining threads: %s', all_threads)
                wait_for = [
                    thread for thread in all_threads
                    if not thread.isDaemon() and
                    not isinstance(thread, threading._MainThread)
                ]
                if not wait_for:
                    logging.info('Bye!')
                    sys.exit(0)
                self.shutdown = True
                logging.info('Waiting for %i threads to exit', len(wait_for))
                for thread in wait_for:
                    logging.info('Joining with %s/%f', thread, interval)
                    thread.join(interval)
        except Exception as e:
            logging.error('Worker error: %s' % e)


def main():
    if len(sys.argv) > 1:
        if sys.argv[1].startswith('--'):
            sys.argv[1] = sys.argv[1][2:]

        if sys.argv[1] == 'help':
            print('\n'.join((
                'Run without options to run agent.',
                'Acceptable options (leading -- is optional):',
                '    help, info, version, hello, insecure-hello, test',
            )))
            sys.exit()
        elif sys.argv[1] == 'info':
            print(info())
            sys.exit()
        elif sys.argv[1] == 'version':
            print(__version__)
            sys.exit()
        elif sys.argv[1] == 'hello':
            del sys.argv[1]
            sys.exit(hello())
        elif sys.argv[1] == 'insecure-hello':
            del sys.argv[1]
            sys.exit(hello(proto='http'))
        elif sys.argv[1] == 'test':
            sys.exit(test_plugins(sys.argv[2:]))
        else:

            print('Invalid option:', sys.argv[1], file=sys.stderr)
            sys.exit(1)
    else:
        Agent().run()


if __name__ == '__main__':
    main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ConfigParser
import pickle
import time
import sys
# import os


class BasePlugin:
    '''
    Abstract class for plugins
    '''
    __name__ = ''

    def __init__(self, agent_cache=[]):
        if isinstance(agent_cache, list):
            self.agent_cache = agent_cache
        else:
            raise TypeError('Type of agent_cache have to be list')

        # if not self.__name__:
        #     self.__name__ = os.path.splitext(os.path.basename(__file__))[0]

    def run(self, config=None):
        '''
        Virtual method for running the plugin
        '''
        pass

    def execute(self):
        '''
        Execution wrapper for the plugin
        argv[1]: ini_file
        '''
        config = None
        if len(sys.argv) > 1:
            config = ConfigParser.RawConfigParser()
            config.read(sys.argv[1])
        pickle.dump(self.run(config), sys.stdout)

    def get_agent_cache(self):
        '''
        Return agent cached value for this specific plugin.
        '''
        try:
            return self.agent_cache[0]
        except Exception:
            return {}

    def set_agent_cache(self, cache):
        '''
        Set agent cache value previously passed to this plugin instance.
        To enable caching existing agent_cache list have to be passed
        to Plugin on initialization.
        Minimally it should be list().
        Agent will be able to see only changes in zero element of agent_cache, so
        do not manually override self.agent_cache, othervice cache will not be saved!

        If self.agent_cache is not a list appropriate exception will be raised.
        '''
        try:
            self.agent_cache[0] = cache
        except IndexError:
            self.agent_cache.append(cache)

    def absolute_to_per_second(self, key, val, prev_cache):
        try:
            if val >= prev_cache[key]:
                value = \
                    (val - prev_cache[key]) / \
                    (time.time() - prev_cache['ts'])
            else:  # previous cached value should not be higher than current value (service was restarted?)
                value = val / \
                    (time.time() - prev_cache['ts'])
        except Exception:  # No cache yet, can't calculate
            value = 0
        return value

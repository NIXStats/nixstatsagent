#!/usr/bin/env python
# -*- coding: utf-8 -*-
# import psutil
import urllib2
import time
import plugins


class Plugin(plugins.BasePlugin):
    __name__ = 'nginx'

    def run(self, config):
        '''
        Provides the following metrics (example):
            "accepts": 588462,
            "accepts_per_second": 0.0,
            "active_connections": 192,
            "handled": 588462,
            "handled_per_second": 0.0,
            "reading": 0,
            "requests": 9637106,
            "requests_per_second": 0.0,
            "waiting": 189,
            "writing": 3

        requests, accepts, handled are values since the start of nginx.
        *_per_second values calculated from them using cached values from previous call.
        '''

        try:
            results = dict()
            next_cache = dict()
            request = urllib2.Request(config.get('nginx', 'status_page_url'))
            raw_response = urllib2.urlopen(request)
            next_cache['ts'] = time.time()
            prev_cache = self.get_agent_cache()  # Get absolute values from previous check
            response = raw_response.readlines()

            # Active connections: N
            # active_connections = response[0].split(':')[1].strip()
            active_connections = response[0].split()[-1]
            results['active_connections'] = int(active_connections)

            # server accepts handled requests
            keys = response[1].split()[1:]
            values = response[2].split()
            for key, value in zip(keys, values):
                next_cache[key] = int(value)
                results[key] = next_cache[key]  # Keep absolute values in results
                try:
                    if next_cache[key] >= prev_cache[key]:
                        results['%s_per_second' % key] = \
                            (next_cache[key] - prev_cache[key]) / \
                            (next_cache['ts'] - prev_cache['ts'])
                    else:  # Nginx was restarted after previous caching
                        results['%s_per_second' % key] = \
                            next_cache[key] / \
                            (next_cache['ts'] - prev_cache['ts'])
                except KeyError:  # No cache yet, can't calculate
                    results['%s_per_second' % key] = 0.0

            # Reading: X Writing: Y Waiting: Z
            keys = response[3].split()[0::2]
            keys = [entry.strip(':').lower() for entry in keys]
            values = response[3].split()[1::2]
            for key, value in zip(keys, values):
                results[key] = int(value)

            # Cache absolute values for next check calculations
            self.set_agent_cache(next_cache)

            return results
        except Exception:
            return False


if __name__ == '__main__':
    Plugin().execute()

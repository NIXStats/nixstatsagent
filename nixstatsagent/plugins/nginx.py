#!/usr/bin/env python

import psutil
import urllib2
import plugins


class Plugin(plugins.BasePlugin):


    def run(self, config):
        """
        Provides the following metrics:
        'handled': '389',
        'accepts': '389',
        'writing': '2',
        'waiting': '199',
        'active_connections': '201',
        'requests': '3809',
        'reading': '0'

        requests, accepts and handled are values since the start of nginx
        """

        try:
            results = dict()
            request = urllib2.Request(config.get('nginx', 'status_page_url'))
            raw_response = urllib2.urlopen(request)
            response = raw_response.readlines()

            # Active connections
            active_connections = response[0].split(':')[1].strip()
            results['active_connections'] = active_connections

            # server accespts  handled requests
            keys = response[1].split()[1:]
            values = response[2].split()
            for key, value in zip(keys, values):
                results[key] = value

            # Reading: N Writing: N Waiting: N
            keys = response[3].split()[0::2]
            keys = [entry.strip(':').lower() for entry in keys]
            values = response[3].split()[1::2]
            for key, value in zip(keys, values):
                results[key] = value

            return results
        except:
            return False


if __name__ == '__main__':
    Plugin().execute()

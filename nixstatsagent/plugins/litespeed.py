#!/usr/bin/env python
# -*- coding: utf-8 -*-
import plugins
import os
import time
import re
import urllib2
import base64
import requests

class Plugin(plugins.BasePlugin):
    __name__ = 'litespeed'

    '''
    This plugin needs requests (pip install requests)
    Litespeed monitoring plugin. Add the following section to /etc/nixstats.ini

    [litespeed]
    enabled=yes
    host=localhost
    port=7080
    username=admin
    password=pass
    '''

    def run(self, config):
        result = {}
        results = {}
        data = False
        prev_cache = self.get_agent_cache()  # Get absolute values from previous check
        response = requests.get("http://%s:%s/status?rpt=summary" % (config.get('litespeed', 'host'),config.get('litespeed', 'port')), auth=(config.get('litespeed', 'username'), config.get('litespeed', 'password')), verify=False)

        for line in response.text.split('\n'):
            test = re.search('REQ_RATE \[(.*)\]', line)
            if test is not None and test.group(1):
                data = True
                try:
                    result[test.group(1)]
                except KeyError:
                    result[test.group(1)] = {}
                lines = line.replace('\n', '').replace(test.group(0), '').split(', ')
                for line in lines:
                    keyval = line.strip(':').strip().split(':')
                    try:
                        result[test.group(1)][keyval[0]] += float(keyval[1])
                    except KeyError:
                        result[test.group(1)][keyval[0]] = float(keyval[1])

        metrics = (
                'SSL_BPS_IN',
                'BPS_OUT',
                'MAXSSL_CONN',
                'PLAINCONN',
                'BPS_IN',
                'SSLCONN',
                'AVAILSSL',
                'IDLECONN',
                'SSL_BPS_OUT',
                'AVAILCONN',
                'MAXCONN',
                'REQ_PROCESSING'
        )

        if data is True:
            for vhost, statistics in result.items():
                try:
                    prev_cache[vhost]['ts'] = prev_cache['ts']
                except KeyError:
                    prev_cache[vhost] = {}
                results[vhost] = {}
                for key, value in statistics.items():
                    if key == 'TOT_REQS':
                        results[vhost]['RPS'] = self.absolute_to_per_second(key, value, prev_cache[vhost])
                    if key == 'TOTAL_STATIC_HITS':
                        results[vhost]['STATIC_RPS'] = self.absolute_to_per_second(key, value, prev_cache[vhost])
                    if key == 'TOTAL_PUB_CACHE_HITS':
                        results[vhost]['PUB_CACHE_RPS'] = self.absolute_to_per_second(key, value, prev_cache[vhost])
                    if key == 'TOTAL_PRIVATE_CACHE_HITS':
                        results[vhost]['PRIVATE_CACHE_RPS'] = self.absolute_to_per_second(key, value, prev_cache[vhost])
                    if key in metrics:
                        results[vhost][key] = value

        result['ts'] = time.time()
        self.set_agent_cache(result)
        return results

if __name__ == '__main__':
    Plugin().execute()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
    from urllib.parse import urlparse, urlencode
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError
except ImportError:
    from urlparse import urlparse
    from urllib import urlencode
    from urllib2 import urlopen, Request, HTTPError
import time
import plugins
import json
import requests
from requests.auth import HTTPBasicAuth
import sys


class Plugin(plugins.BasePlugin):
    __name__ = 'rabbitmq'

    def run(self, config):
        '''
        rabbitmq status page metrics
        '''
        def ascii_encode_dict(data):
            ascii_encode = lambda x: x.encode('ascii') if isinstance(x, unicode) else x
            return dict(map(ascii_encode, pair) for pair in data.items())

        results = dict()
        next_cache = dict()

        try:
            username = config.get('rabbitmq', 'username')
            password = config.get('rabbitmq', 'password')
            user_pass = (username, password)
        except:
            user_pass = False

        request = requests.get(config.get('rabbitmq', 'status_page_url'), auth=user_pass)

        if request.status_code == 401:
            request = requests.get(config.get('rabbitmq', 'status_page_url'), auth=HTTPBasicAuth(username, password))

        if request.status_code is 200:
            try:
                j = request.json()
            except Exception as e:
                return e
        else:
            return "Could not load status page: {}".format(request.text)

        next_cache['ts'] = time.time()
        prev_cache = self.get_agent_cache()  # Get absolute values from previous check
        try:
            prev_cache['message_stats']
        except:
            prev_cache['message_stats'] = {}
        next_cache['message_stats'] = j
        next_cache['message_stats']['ts'] = time.time();
        results['published'] = self.absolute_to_per_second('published', j['message_stats']['publish'], prev_cache['message_stats'])
        results['published_total'] = j['message_stats']['publish']
        results['ack'] = self.absolute_to_per_second('ack', j['message_stats']['ack'], prev_cache['message_stats'])
        results['ack_total'] = j['message_stats']['ack']
        results['deliver_get'] = self.absolute_to_per_second('deliver_get', j['message_stats']['deliver_get'], prev_cache['message_stats'])
        results['deliver_get_total'] = j['message_stats']['deliver_get']
        results['redeliver'] = self.absolute_to_per_second('redeliver', j['message_stats']['redeliver'], prev_cache['message_stats'])
        results['redeliver_total'] = j['message_stats']['redeliver']
        results['deliver'] = self.absolute_to_per_second('deliver', j['message_stats']['deliver'], prev_cache['message_stats'])
        results['deliver_total'] = j['message_stats']['deliver']

        results['messages'] = j['queue_totals']['messages']
        results['messages_ready'] = j['queue_totals']['messages_ready']
        results['messages_unacknowledged'] = j['queue_totals']['messages_unacknowledged']

        results['listeners'] = len(j['listeners'])

        results['consumers'] = j['object_totals']['consumers']
        results['queues'] = j['object_totals']['queues']
        results['exchanges'] = j['object_totals']['exchanges']
        results['connections'] = j['object_totals']['connections']
        results['channels'] = j['object_totals']['channels']

        self.set_agent_cache(next_cache)

        return results


if __name__ == '__main__':
    Plugin().execute()

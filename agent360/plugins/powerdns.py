#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
    from urllib.request import urlopen, Request
except ImportError:
    from urllib2 import urlopen, Request
import time
import plugins
import urllib2
import json

class Plugin(plugins.BasePlugin):
    __name__ = 'powerdns'

    def run(self, config):
        '''
        Experimental plugin for PowerDNS authoritative server. Might also work with PowerDNS recursor,
        but it may need extra delta_keys / absolute_keys.
        Add to /etc/agent360.ini:
        [powerdns]
        enabled=yes
        statistics_url=http://localhost:8081/api/v1/servers/localhost/statistics
        api_key=changeme
        ;ca_file=
        ;ca_path=
        ;timeout=10
        '''
        # Create request to configured URL
        request = urllib2.Request(config.get(__name__, 'statistics_url'), headers={'X-API-Key': '%s' % config.get(__name__, 'api_key')})
        # defaults
        timeout = 10
        results = dict()
        raw_response = None
        # next / previous cached metrics (for calculating deltas)
        next_cache = dict()
        prev_cache = self.get_agent_cache()
        # use timeout from config if specified
        if config.has_option(__name__, 'timeout'):
            timeout = int(config.get(__name__, 'timeout'))
        # create response based on configuration
        if config.has_option(__name__, 'ca_file'):
            raw_response = urllib2.urlopen(request, timeout=timeout, cafile=config.get(__name__, 'ca_file'))
        elif config.has_option(__name__, 'ca_path'):
            raw_response = urllib2.urlopen(request, timeout=timeout, capath=config.get(__name__, 'ca_path'))
        else:
            raw_response = urllib2.urlopen(request, timeout=timeout)
        # set next_cache timestamp
        next_cache['ts'] = time.time()
        # parse raw response as JSON
        try:
            stats = json.loads(raw_response.read())
        except Exception:
            return False
        # keys for which we should calculate the delta
        delta_keys = (
            'corrupt-packets',
            'deferred-cache-inserts',
            'deferred-cache-lookup',
            'deferred-packetcache-inserts',
            'deferred-packetcache-lookup',
            'dnsupdate-answers',
            'dnsupdate-changes',
            'dnsupdate-queries',
            'dnsupdate-refused',
            'incoming-notifications',
            'overload-drops',
            'packetcache-hit',
            'packetcache-miss',
            'query-cache-hit',
            'query-cache-miss',
            'rd-queries',
            'recursing-answers',
            'recursing-questions',
            'recursion-unanswered',
            'servfail-packets',
            'signatures',
            'sys-msec',
            'tcp-answers',
            'tcp-answers-bytes',
            'tcp-queries',
            'tcp4-answers',
            'tcp4-answers-bytes',
            'tcp4-queries',
            'tcp6-answers',
            'tcp6-answers-bytes',
            'tcp6-queries',
            'timedout-packets',
            'udp-answers',
            'udp-answers-bytes',
            'udp-do-queries',
            'udp-in-errors',
            'udp-noport-errors',
            'udp-queries',
            'udp-recvbuf-errors',
            'udp-sndbuf-errors',
            'udp4-answers',
            'udp4-answers-bytes',
            'udp4-queries',
            'udp6-answers',
            'udp6-answers-bytes',
            'udp6-queries',
            'user-msec'
        )

        # keys for which we should store the absolute value:
        absolute_keys = (
            'key-cache-size',
            'latency',
            'fd-usage',
            'meta-cache-size',
            'open-tcp-connections',
            'packetcache-size',
            'qsize-q',
            'query-cache-size',
            'real-memory-usage',
            'security-status',
            'signature-cache-size',
            'uptime'
        )
        data = dict()
        for stat in stats:
            if 'name' in stat and 'value' in stat and 'type' in stat:
                if stat['type'] == 'StatisticItem':
                    if stat['name'] in delta_keys:
                        results[stat['name']] = self.absolute_to_per_second(stat['name'], float(stat['value']), prev_cache)
                        data[stat['name']] = float(stat['value'])
                    elif stat['name'] in absolute_keys:
                        results[stat['name']] = float(stat['value'])
        data['ts'] = time.time()
        self.set_agent_cache(data)
        return results

if __name__ == '__main__':
    Plugin().execute()

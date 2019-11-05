#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib2
import time
import plugins
import json


class Plugin(plugins.BasePlugin):
    __name__ = 'phpfpm'

    def run(self, config):
        '''
        php-fpm status page metrics
        '''
        def ascii_encode_dict(data):
            ascii_encode = lambda x: x.encode('ascii') if isinstance(x, unicode) else x
            return dict(map(ascii_encode, pair) for pair in data.items())

        results = dict()
        next_cache = dict()
        my_pools = config.get(__name__, 'status_page_url').split(',')
        prev_cache = self.get_agent_cache()  # Get absolute values from previous check
        for pool in my_pools:
            request = urllib2.Request(pool)
            raw_response = urllib2.urlopen(request)

            try:
                j = json.loads(raw_response.read(), object_hook=ascii_encode_dict)
                results[j['pool']] = {}
                next_cache['%s_ts' % j['pool']] = time.time()
                for k, v in j.items():
                    results[j['pool']][k.replace(" ", "_")] = v

                next_cache['%s_accepted_conn' % j['pool']] = int(results[j['pool']]['accepted_conn'])
            except Exception:
                return False

            try:
                if next_cache['%s_accepted_conn' % j['pool']] >= prev_cache['%s_accepted_conn' % j['pool']]:
                    results[j['pool']]['accepted_conn_per_second'] = \
                        (next_cache['%s_accepted_conn' % j['pool']] - prev_cache['%s_accepted_conn' % j['pool']]) / \
                        (next_cache['%s_ts' % j['pool']] - prev_cache['%s_ts' % j['pool']])
                else:  # Was restarted after previous caching
                    results[j['pool']]['accepted_conn_per_second'] = \
                        next_cache['%s_accepted_conn' % j['pool']] / \
                        (next_cache['%s_ts' % j['pool']] - prev_cache['%s_ts' % j['pool']])
            except KeyError:  # No cache yet, can't calculate
                results[j['pool']]['accepted_conn_per_second'] = 0.0

        # Cache absolute values for next check calculations
        self.set_agent_cache(next_cache)

        return results


if __name__ == '__main__':
    Plugin().execute()

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
        request = urllib2.Request(config.get('phpfpm', 'status_page_url'))
        raw_response = urllib2.urlopen(request)
        next_cache['ts'] = time.time()
        prev_cache = self.get_agent_cache()  # Get absolute values from previous check

        try:
            j = json.loads(raw_response.read(), object_hook=ascii_encode_dict)

            for k, v in j.items():
                results[k.replace(" ", "_")] = v

            next_cache['accepted_conn'] = int(results['accepted_conn'])
        except Exception:
            return False

        try:
            if next_cache['accepted_conn'] >= prev_cache['accepted_conn']:
                results['accepted_conn_per_second'] = \
                    (next_cache['accepted_conn'] - prev_cache['accepted_conn']) / \
                    (next_cache['ts'] - prev_cache['ts'])
            else:  # Was restarted after previous caching
                results['accepted_conn_per_second'] = \
                    next_cache['accepted_conn'] / \
                    (next_cache['ts'] - prev_cache['ts'])
        except KeyError:  # No cache yet, can't calculate
            results['accepted_conn_per_second'] = 0.0

        # Cache absolute values for next check calculations
        self.set_agent_cache(next_cache)

        return results


if __name__ == '__main__':
    Plugin().execute()

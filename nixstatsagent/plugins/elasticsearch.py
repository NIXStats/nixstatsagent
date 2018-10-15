#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib2
import time
import plugins
import json
import collections


class Plugin(plugins.BasePlugin):
    __name__ = 'elasticsearch'

    def run(self, config):
        '''
        experimental monitoring plugin for elasticsearch
        Add to /etc/nixstats.ini:
        [elasticsearch]
        enabled = yes
        status_page_url = http://127.0.0.1:9200/_stats
        '''

        def ascii_encode_dict(data):
            ascii_encode = lambda x: x.encode('ascii') if isinstance(x, unicode) else x
            return dict(map(ascii_encode, pair) for pair in data.items())

        results = dict()
        next_cache = dict()
        request = urllib2.Request(config.get('elasticsearch', 'status_page_url'))
        raw_response = urllib2.urlopen(request)
        next_cache['ts'] = time.time()
        prev_cache = self.get_agent_cache()  # Get absolute values from previous check
        def flatten(d, parent_key='', sep='_'):
            items = []
            for k, v in d.items():
                new_key = parent_key + sep + k if parent_key else k
                if isinstance(v, collections.MutableMapping):
                    items.extend(flatten(v, new_key, sep=sep).items())
                else:
                    items.append((new_key, v))
            return dict(items)
        try:
            j = flatten(json.loads(raw_response.read(), object_hook=ascii_encode_dict)['_all']['total'])
        except Exception:
            return False


        delta_keys = (
            'get_time_in_millis',
            'indexing_index_time_in_millis',
            'flush_total_time_in_millis',
            'indexing_delete_time_in_millis',
            'indexing_index_time_in_millis',
            'indexing_throttle_time_in_millis',
            'merges_total_stopped_time_in_millis',
            'merges_total_throttled_time_in_millis',
            'merges_total_time_in_millis',
            'recovery_throttle_time_in_millis',
            'refresh_total_time_in_millis',
            'search_fetch_time_in_millis',
            'search_query_time_in_millis',
            'search_scroll_time_in_millis',
            'search_suggest_time_in_millis',
            'warmer_total_time_in_millis',
            'docs_count',
            'docs_deleted',
            'flush_total',
            'get_exists_total',
            'get_missing_total',
            'get_total',
            'indexing_delete_total',
            'indexing_index_total',
            'indexing_noop_update_total',
            'merges_total',
            'merges_total_docs',
            'merges_total_auto_throttle_in_bytes',
            'query_cache_cache_count',
            'query_cache_cache_size',
            'query_cache_evictions',
            'query_cache_hit_count',
            'query_cache_miss_count',
            'query_cache_total_count',
            'refresh_total',
            'request_cache_hit_count',
            'request_cache_miss_count',
            'search_fetch_total',
            'search_open_contexts',
            'search_query_total',
            'search_scroll_total',
            'search_suggest_total',
            'segments_count',
            'segments_max_unsafe_auto_id_timestamp',
            'warmer_total',
            'get_exists_time_in_millis',
            'get_missing_time_in_millis'
        )

        data = {}
        constructors = [str, float]
        for key, value in j.items():
            key = key.lower().strip()
            for c in constructors:
                try:
                    value = c(value)
                except ValueError:
                    pass
            if key in delta_keys and type(value) is not str:
                j[key] = self.absolute_to_per_second(key, float(value), prev_cache)
                data[key] = float(value)
            else:
                pass

        data['ts'] = time.time()
        # Cache absolute values for next check calculations
        self.set_agent_cache(data)

        return j


if __name__ == '__main__':
    Plugin().execute()

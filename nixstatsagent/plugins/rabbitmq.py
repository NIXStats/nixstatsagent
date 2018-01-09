#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib
import time
import plugins
import json


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
        raw_response = urllib.urlopen(config.get('rabbitmq', 'status_page_url')).fp
        next_cache['ts'] = time.time()
        prev_cache = self.get_agent_cache()  # Get absolute values from previous check

        try:
            j = json.loads(raw_response.read(), object_hook=ascii_encode_dict)
        except Exception:
            return False

        results['published'] = self.absolute_to_per_second('published', j['message_stats']['publish'], prev_cache)
        results['ack'] = self.absolute_to_per_second('ack', j['message_stats']['ack'], prev_cache)
        results['deliver_get'] = self.absolute_to_per_second('ack', j['message_stats']['deliver_get'], prev_cache)
        results['redeliver'] = self.absolute_to_per_second('ack', j['message_stats']['redeliver'], prev_cache)
        results['deliver'] = self.absolute_to_per_second('ack', j['message_stats']['deliver'], prev_cache)

        results['messages'] = self.absolute_to_per_second('ack', j['queue_totals']['messages'], prev_cache)
        results['messages_ready'] = self.absolute_to_per_second('ack', j['queue_totals']['messages_ready'], prev_cache)
        results['messages_unacknowledged'] = self.absolute_to_per_second('ack', j['queue_totals']['messages_unacknowledged'], prev_cache)

        results['listeners'] = len(j['listeners'])

        results['consumers'] = j['object_totals']['consumers']
        results['queues'] = j['object_totals']['queues']
        results['exchanges'] = j['object_totals']['exchanges']
        results['connections'] = j['object_totals']['connections']
        results['channels'] = j['object_totals']['channels']

        next_cache = j
        next_cache['ts'] = time.time()
        self.set_agent_cache(next_cache)

        return results


if __name__ == '__main__':
    Plugin().execute()

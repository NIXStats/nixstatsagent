#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import plugins
import time


class Plugin(plugins.BasePlugin):
    __name__ = 'docker'

    def run(self, config):
        '''
        Docker monitoring, needs sudo access!
        Instructions at:
        https://help.nixstats.com/en/article/monitoring-docker-9st778/
        '''
        containers = {}
        last_value = {}
        prev_cache = self.get_agent_cache()  # Get absolute values from previous check
        try:
            lines = [s.split(' / ') for s in os.popen('sudo docker stats --no-stream --no-trunc --format "{{.CPUPerc}} / {{.Name}} / {{.ID}} / {{.MemUsage}} / {{.NetIO}} / {{.BlockIO}} / {{.MemPerc}}"').read().splitlines()]
            for row in lines:
                container = {}
                container['cpu'] = row[0].strip('%')
                name = row[1]
                container_id = row[2]
                container['mem_usage_bytes'] = self.computerReadable(row[3])
                container['mem_total_bytes'] = self.computerReadable(row[4])
                container['net_in_bytes'] = self.absolute_to_per_second('%s_%s' % (name, 'net_in_bytes'), self.computerReadable(row[5]), prev_cache)
                container['net_out_bytes'] = self.absolute_to_per_second('%s_%s' % (name, 'net_out_bytes'), self.computerReadable(row[6]), prev_cache)
                container['disk_in_bytes'] = self.absolute_to_per_second('%s_%s' % (name, 'disk_in_bytes'), self.computerReadable(row[7]), prev_cache)
                container['disk_out_bytes'] = self.absolute_to_per_second('%s_%s' % (name, 'disk_out_bytes'), self.computerReadable(row[8]), prev_cache)
                container['mem_pct'] = row[9].strip('%')

                last_value['%s_%s' % (name, 'mem_usage_bytes')] = self.computerReadable(row[3])
                last_value['%s_%s' % (name, 'net_in_bytes')] = self.computerReadable(row[5])
                last_value['%s_%s' % (name, 'net_out_bytes')] = self.computerReadable(row[6])
                last_value['%s_%s' % (name, 'disk_in_bytes')] = self.computerReadable(row[7])
                last_value['%s_%s' % (name, 'disk_out_bytes')] = self.computerReadable(row[8])
                containers[name] = container
        except Exception as e:
            return e.message
        containers['containers'] = len(containers)
        last_value['ts'] = time.time()
        self.set_agent_cache(last_value)

        return containers

    def computerReadable(self, value):
        if value[-3:] == 'KiB':
            return float(value[:-3])*1024
        elif value[-3:] == 'MiB':
            return float(value[:-3])*1024*1024
        elif value[-3:] == 'GiB':
            return float(value[:-3])*1024*1024*1024
        elif value[-3:] == 'TiB':
            return float(value[:-3])*1024*1024*1024*1024
        elif value[-3:] == 'PiB':
            return float(value[:-3])*1024*1024*1024*1024*1024
        elif value[-2:] == 'kB':
            return float(value[:-2])*1024
        elif value[-2:] == 'MB':
            return float(value[:-2])*1024*1024
        elif value[-2:] == 'GB':
            return float(value[:-2])*1024*1024*1024
        elif value[-2:] == 'TB':
            return float(value[:-2])*1024*1024*1024*1024
        elif value[-2:] == 'PB':
            return float(value[:-2])*1024*1024*1024*1024*1024
        elif value[-1:] == 'B':
            return float(value[:-1])

if __name__ == '__main__':
    Plugin().execute()

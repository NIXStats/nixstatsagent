#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import os
import signal
import subprocess
import sys
import psutil
import plugins
import time

def diskstats_parse(dev=None):
    file_path = '/proc/diskstats'
    result = {}

    if not os.path.isfile("/proc/diskstats"):
        return False

    # ref: http://lxr.osuosl.org/source/Documentation/iostats.txt
    columns_disk = ['m', 'mm', 'dev', 'reads', 'rd_mrg', 'rd_sectors',
                    'ms_reading', 'writes', 'wr_mrg', 'wr_sectors',
                    'ms_writing', 'cur_ios', 'ms_doing_io', 'ms_weighted']
    # For kernel 4.18+
    columns_disk_418 = ['m', 'mm', 'dev', 'reads', 'rd_mrg', 'rd_sectors',
                    'ms_reading', 'writes', 'wr_mrg', 'wr_sectors',
                    'ms_writing', 'cur_ios', 'ms_doing_io', 'ms_weighted',
                    'discards', 'discards_merged', 'discarded_sectors',
                    'discarded_time']
    # for kernel 5.5+
    columns_disk_55 = ['m', 'mm', 'dev', 'reads', 'rd_mrg', 'rd_sectors',
                    'ms_reading', 'writes', 'wr_mrg', 'wr_sectors',
                    'ms_writing', 'cur_ios', 'ms_doing_io', 'ms_weighted',
                    'discards', 'discards_merged', 'discarded_sectors',
                    'discarded_time', 'flush', 'flush_time']

    columns_partition = ['m', 'mm', 'dev', 'reads', 'rd_sectors', 'writes', 'wr_sectors']

    lines = open(file_path, 'r').readlines()
    for line in lines:
        if line == '':
            continue
        split = line.split()
        if len(split) == len(columns_disk_55):
            columns = columns_disk_55
        elif len(split) == len(columns_disk_418):
            columns = columns_disk_418
        elif len(split) == len(columns_disk):
            columns = columns_disk
        elif len(split) == len(columns_partition):
            columns = columns_partition
        else:
            # No match
            continue

        data = dict(zip(columns, split))

        if data['dev'][:3] == 'nvm' and data['dev'][-2:-1] == 'n':
            pass
        elif data['dev'][-1:].isdigit() is True:
            continue

        if "loop" in data['dev'] or "ram" in data['dev']:
            continue

        if dev is not None and dev != data['dev']:
            continue
        for key in data:
            if key != 'dev':
                data[key] = int(data[key])
        result[data['dev']] = data

    return result


class Plugin(plugins.BasePlugin):
    __name__ = 'iostat'

    def run(self, *unused):
        delta_keys = (
            'reads',
            'writes',
            'wr_sectors',
            'rd_sectors',
            'ms_reading',
            'rd_mrg',
            'wr_mrg',
            'ms_weighted',
            'ms_doing_io',
            'ms_writing',
            'discarded_sectors',
            'discarded_time',
            'flush',
            'flush_time',
            'discards'
        )
        next_cache = {}
        next_cache['ts'] = time.time()
        prev_cache = self.get_agent_cache()  # Get absolute values from previous check
        disks = diskstats_parse()
        if not disks  or disks is False:
            results = {}
            try:
                diskdata = psutil.disk_io_counters(perdisk=True)
                for device, values in diskdata.items():
                    device_stats = {}
                    for key_value in values._fields:
                        device_stats[key_value] = getattr(values, key_value)
                    results[device] = device_stats
            except Exception as e:
                results = e.message
        else:
            results = {}
            for device, values in disks.items():
                device_stats = {}
                next_cache[device] = {}
                next_cache[device]['ts'] = time.time()
                try:
                    prev_cache[device]
                except:
                    prev_cache[device] = {}
                for key_value, value in values.items():
                    if key_value in delta_keys:
                        try:
                            device_stats[key_value] = self.absolute_to_per_second(key_value, value, prev_cache[device])
                        except:
                            pass
                        next_cache[device][key_value] = value
                    else:
                        device_stats[key_value] = value
                try:
                    device_stats['avgrq-sz'] = (device_stats['wr_sectors']+device_stats['rd_sectors']) / (device_stats['reads']+device_stats['writes'])
                except:
                    device_stats['avgrq-sz'] = 0
                try:
                    device_stats['tps'] = device_stats['reads']+device_stats['writes']
                except:
                    device_stats['tps'] = 0
                try:
                    device_stats['usage'] = (100 * device_stats['ms_doing_io']) / (1000 * (next_cache['ts'] - prev_cache['ts']))
                except:
                    device_stats['usage'] = 0

                results[device] = device_stats

        self.set_agent_cache(next_cache)
        return results


if __name__ == '__main__':
    Plugin().execute()

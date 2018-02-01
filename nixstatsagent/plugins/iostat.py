#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import os
import signal
import subprocess
import sys
import psutil
import plugins

def diskstats_parse(dev=None):
    file_path = '/proc/diskstats'
    result = {}

    if not os.path.isfile("/proc/diskstats"):
        return False

    # ref: http://lxr.osuosl.org/source/Documentation/iostats.txt
    columns_disk = ['m', 'mm', 'dev', 'reads', 'rd_mrg', 'rd_sectors',
                    'ms_reading', 'writes', 'wr_mrg', 'wr_sectors',
                    'ms_writing', 'cur_ios', 'ms_doing_io', 'ms_weighted']

    columns_partition = ['m', 'mm', 'dev', 'reads', 'rd_sectors', 'writes', 'wr_sectors']

    lines = open(file_path, 'r').readlines()
    for line in lines:
        if line == '':
            continue
        split = line.split()
        if len(split) == len(columns_disk):
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
        results = diskstats_parse()
        if not results  or results is False:
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
        return results


if __name__ == '__main__':
    Plugin().execute()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import plugins
import json


class Plugin(plugins.BasePlugin):
    __name__ = 'megacli'

    def run(self, config):
        disk = {}
        try:
            df_output_lines = os.popen("megacli -LDInfo -Lall -aALL").read().splitlines()
            data = {}
            for line in df_output_lines:

                if line.startswith('Virtual Drive'):
                    delim = line.find('(')
                    offset = line.find(':')
                    data['virtualdisk_id'] = int(line[offset+1:delim].strip())
                if line.startswith('Name'):
                    offset = line.find(':')
                    data['name'] = line[offset+1:].strip()
                elif line.startswith('RAID Level'):
                    offset = line.find(':')
                    data['raid_level'] = line[offset+1:].strip()
                elif line.startswith('Size'):
                    offset = line.find(':')
                    data['size'] = line[offset+1:].strip()
                elif line.startswith('State'):
                    offset = line.find(':')
                    data['state'] = line[offset+1:].strip()
                elif line.startswith('Strip Size'):
                    delim = line.find(' KB')
                    offset = line.find(':')
                    data['stripe_size'] = line[offset+1:delim].strip()
                elif line.startswith('Number Of Drives'):
                    offset = line.find(':')
                    data['number_of_drives'] = int(line[offset+1:].strip())
                elif line.startswith('Span Depth'):
                    offset = line.find(':')
                    data['span_depth'] = int(line[offset+1:].strip())
                elif line.startswith('Default Cache Policy'):
                    offset = line.find(':')
                    data['default_cache_policy'] = line[offset+1:].strip()
                elif line.startswith('Current Cache Policy'):
                    offset = line.find(':')
                    data['current_cache_policy'] = line[offset+1:].strip()
                elif line.startswith('Current Access Policy'):
                    offset = line.find(':')
                    data['access_policy'] = line[offset+1:].strip()
                elif line.startswith('Disk Cache Policy'):
                    offset = line.find(':')
                    data['disk_cache_policy'] = line[offset+1:].strip()
                elif line.startswith('Encryption'):
                    offset = line.find(':')
                    data['encryption'] = line[offset+1:].strip()

            disk[data['virtualdisk_id']] = data
        except Exception as e:
            return e

        return disk


if __name__ == '__main__':
    Plugin().execute()

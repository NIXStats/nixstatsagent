#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import subprocess
import plugins
import json
import re

class Plugin(plugins.BasePlugin):
    __name__ = 'diskstatus'

    def run(self, config):
        '''
        Monitor nvme or smart disk status.
        For NVME drives install nvme-cli (https://github.com/linux-nvme/nvme-cli#distro-support)
        for smart status install smartmontools (apt-get/yum install smartmontools)
        This plugin requires the agent to be run under the root user.
        '''
        results = {}
        try:
            data = subprocess.Popen('nvme --list --output-format=json', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()[0]
            data = json.loads(data)
            data['Devices']
            nvme = True
        except Exception:
            nvme = False
            pass

        if nvme is True:
            for value in data['Devices']:
                device = {}
                disk_data = os.popen('nvme smart-log {} --output-format=json'.format(value['DevicePath'])).read()
                try:
                    data_disk = json.loads(disk_data)
                except Exception:
                    pass

                for disk_key, disk_value in data_disk.items():
                    if disk_key.startswith('temperature'):
                        device[disk_key] = round(disk_value-273.15, 0) # kelvin to celsius
                    else:
                        device[disk_key] = disk_value
                results[value['DevicePath'].replace('/dev/', '')] = device

        try:
            devlist = subprocess.Popen('smartctl --scan', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()[0].splitlines()
            smartctl = True
        except Exception:
            smartctl = False
            pass

        if smartctl is True:
            for row in devlist:
                try:
                    disk_id = row.split(' ')[0].split('/')[2]
                    disk_stats = os.popen('smartctl -A -H {}'.format(row.split(' ')[0])).read().splitlines()
                    smart_status = 0
                    if disk_stats[4].split(': ')[1] == 'PASSED':
                        smart_status = 1
                    del disk_stats[:9]
                    results[disk_id] = {}
                    for stats in disk_stats:
                        stats = re.sub(' +', ' ', stats).strip()
                        stats = stats.split(' ')
                        if len(stats) > 9:
                            results[disk_id][stats[1].lower().replace('_celsius','')] = stats[9]
                    results[disk_id]["status"] = smart_status
                except Exception:
                    pass
        return results


if __name__ == '__main__':
    Plugin().execute()

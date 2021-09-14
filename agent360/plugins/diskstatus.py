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
        For NVME drives use the diskstatus-nvme plugin
        for smart status install smartmontools (apt-get/yum install smartmontools)
        This plugin requires the agent to be run under the root user.
        '''
        results = {}

        try:
            devlist = subprocess.Popen('smartctl --scan', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()[0].decode().splitlines()
            smartctl = True
        except Exception as e:
            smartctl = False
            return "Could not fetch smartctl status information"

        if smartctl is True:
            for row in devlist:
                try:
                    disk_id = row.split(' ')[0].split('/')[2]
                    disk_stats = os.popen('smartctl -A -H {}'.format(row.split(' ')[0])).read().splitlines()
                    smart_status = 0
                    if disk_stats[4].split(': ')[1] == 'PASSED':
                        smart_status = 1
                    results[disk_id] = {}
                    start = False
                    for stats in disk_stats:
                        if stats[0:3] == 'ID#':
                            start = True
                            continue
                        if start is False:
                            continue
                        stats = re.sub(' +', ' ', stats).strip()
                        stats = stats.split(' ')
                        if len(stats) > 9:
                            results[disk_id][stats[1].lower().replace('_celsius','')] = stats[9]
                    results[disk_id]["status"] = smart_status
                except Exception as e:
                    print(e)
        return results


if __name__ == '__main__':
    Plugin().execute()

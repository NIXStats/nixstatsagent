#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import subprocess
import plugins
import json
import re

class Plugin(plugins.BasePlugin):
    __name__ = 'diskstatus-nvme'

    def run(self, config):
        '''
        Monitor nvme disk status
        For NVME drives install nvme-cli (https://github.com/linux-nvme/nvme-cli#distro-support)
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
            return "Could not fetch nvme status information"

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
        return results


if __name__ == '__main__':
    Plugin().execute()

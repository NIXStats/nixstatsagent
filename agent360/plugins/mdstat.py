#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import plugins
import json


class Plugin(plugins.BasePlugin):
    __name__ = 'mdstat'

    def run(self, config):
        '''
        Monitor software raid status using mdadm
        pip install mdstat
        '''
        data = os.popen('sudo mdjson').read()
        results = {}

        try:
            data = json.loads(data)
        except Exception:
            return "Could not load mdstat data"

        for key, value in data['devices'].items():
            device = {}
            if(value['active'] is not True):
                device['active'] = 0
            else:
                device['active'] = 1
            if(value['read_only'] is not False):
                device['read_only'] = 1
            else:
                device['read_only'] = 0
            if(value['resync'] is not None):
                device['resync'] = 1
            else:
                device['resync'] = 0
            device['faulty'] = 0
            for disk, diskvalue in value['disks'].items():
                if diskvalue['faulty'] is not False:
                    device['faulty'] = device['faulty'] + 1
            results[key] = device
        return results

if __name__ == '__main__':
    Plugin().execute()

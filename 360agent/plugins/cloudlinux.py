#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import plugins
import json


class Plugin(plugins.BasePlugin):
    __name__ = 'cloudlinux'

    def run(self, config):
        '''
        Beta plugin to monitor cloudlinux users
        Requires sudo access to lveinfo (whereis lveinfo) add to /etc/sudoers:
        nixstats ALL=(ALL) NOPASSWD: /REPLACE/PATH/TO/lveinfo

        To enable add to /etc/nixstats.ini:
        [cloudlinux]
        enabled = yes
        '''
        data = os.popen('sudo lveinfo -d --period 5m -o cpu_avg -l 20 --json').read()
        results = {}

        try:
            data = json.loads(data)
        except Exception:
            return "Could not load lveinfo data"

        if data['success'] is not 1:
            return "Failed to load lveinfo"

        results = {}

        for line in data['data']:
            username = line['ID']
            del line['ID']
            results[username] = line

        return results

if __name__ == '__main__':
    Plugin().execute()

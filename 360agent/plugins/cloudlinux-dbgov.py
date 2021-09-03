#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import plugins
import json


class Plugin(plugins.BasePlugin):
    __name__ = 'cloudlinux-dbgov'

    def run(self, config):
        '''
        Beta plugin to monitor cloudlinux db governor users
        Requires sudo access to lveinfo (whereis lveinfo) add to /etc/sudoers:
        nixstats ALL=(ALL) NOPASSWD: /REPLACE/PATH/TO/lveinfo

        To enable add to /etc/nixstats.ini:
        [cloudlinux-dbgov]
        enabled = yes
        '''
        data = os.popen('sudo lveinfo --dbgov --period 5m -o cpu --limit 20 --json').read()
        results = {}

        try:
            data = json.loads(data)
        except Exception:
            return "Could not load lveinfo dbgov data"

        if data['success'] is not 1:
            return "Failed to load lveinfo dbgov"

        results = {}

        for line in data['data']:
            username = line['USER']
            del line['USER']
            results[username] = line

        return results

if __name__ == '__main__':
    Plugin().execute()

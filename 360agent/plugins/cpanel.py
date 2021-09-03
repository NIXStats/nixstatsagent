#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import plugins

class Plugin(plugins.BasePlugin):
    __name__ = 'cpanel'

    def run(self, config):
        '''
        Plugin to measure disk usage of cpanel users
        To enable add to /etc/nixstats.ini:
        [cpanel]
        enabled = yes
        '''
        if os.path.isdir("/var/cpanel/users/") is False:
            return "/var/cpanel/users does not exist"
        data = os.popen('for user in `/bin/ls -A /var/cpanel/users/` ; do du -sc /home/$user ;done | grep -v \'total\|system\|nobody\' | cut -d"/" -f1,3 | sort -nrk 1,1').read()
        results = {}
        i=0
        try:
            for line in data.splitlines():
                i = i + 1
                if i > 50:
                    break
                results[line.split("\t")[1].strip("/")] = {"bytes": int(line.split("\t")[0])}
        except Exception:
            return "Could not fetch cpanel users"

        return results

if __name__ == '__main__':
    Plugin().execute()

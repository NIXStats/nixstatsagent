#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import plugins
import subprocess

### You need to add `nixstats ALL=(ALL) NOPASSWD: /usr/sbin/kamctl` to /etc/sudoers in order for this to work
class Plugin(plugins.BasePlugin):
    __name__ = 'asterisk'

    def run(self, *unused):
        p = subprocess.Popen("sudo kamctl ul show | grep AOR | wc -l", stdout=subprocess.PIPE, shell=True)
        p = p.communicate()[0].decode('utf-8').replace("\n", "")
        p = { "devices_online": p }
        return p

if __name__ == '__main__':
    Plugin().execute()

#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import plugins
import subprocess

### You need to add `nixstats ALL=(ALL) NOPASSWD: /usr/sbin/asterisk` to /etc/sudoers in order for this to work
class Plugin(plugins.BasePlugin):
    __name__ = 'asterisk'

    def run(self, *unused):
        p = subprocess.Popen("sudo asterisk -rx 'core show calls' | grep 'active' | cut -f1 -d ' '", stdout=subprocess.PIPE, shell=True)
        p, err = p.communicate()[0].decode('utf-8')
        p = { "calls": p }
        return p

if __name__ == '__main__':
    Plugin().execute()

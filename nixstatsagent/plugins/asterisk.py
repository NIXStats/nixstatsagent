#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import plugins
import subprocess


class Plugin(plugins.BasePlugin):
    __name__ = 'asterisk'

    def run(self, *unused):
        p = subprocess.Popen("sudo asterisk -rx 'core show calls' | grep 'active' | cut -f1 -d ' '", stdout=subprocess.PIPE, shell=True)
        p = p.communicate()[0].decode('utf-8').replace("\n", "")
        incoming = subprocess.Popen("sudo asterisk -rx 'core show channels verbose' | cut -c1-15 | grep 'pstn_' | wc -l", stdout=subprocess.PIPE, shell=True)
        incoming = incoming.communicate()[0].decode('utf-8').replace("\n", "")
        res = { "calls": p, "incomingcalls": incoming }
        return res

if __name__ == '__main__':
    Plugin().execute()

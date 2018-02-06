#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import plugins
import subprocess


class Plugin(plugins.BasePlugin):
    __name__ = 'asterisk'

    def run(self, *unused):
        p = subprocess.Popen("sudo asterisk -rx 'core show calls' | grep 'active' | cut -f1 -d ' '", stdout=subprocess.PIPE, shell=True)
        p = p.communicate()[0].decode('utf-8').replace("\n", "")
        p = { "calls": p }
        return p

if __name__ == '__main__':
    Plugin().execute()

#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import plugins
import subprocess


class Plugin(plugins.BasePlugin):
    __name__ = 'janus'

    def run(self, config):
        adminpw = config.get('janus', 'adminpw')
        p = subprocess.Popen("curl -s -H \"Accept: application/json\" -H \"Content-type: application/json\" -X POST -d '{ \"janus\": \"list_sessions\", \"transaction\": \"324\", \"admin_secret\": \""+adminpw+"\" }' http://localhost:7088/admin | awk 'NR>=5' | head -n -2 | wc -l", stdout=subprocess.PIPE, shell=True)
        p = p.communicate()[0].decode('utf-8').replace("\n", "")
        res = { "janus_sessions": p }
        return res

if __name__ == '__main__':
    Plugin().execute()

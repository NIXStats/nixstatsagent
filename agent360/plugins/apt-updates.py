#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import plugins

class Plugin(plugins.BasePlugin):
    __name__ = 'apt-updates'

    def run(self, config):
        '''
        ubuntu/debian updates available from apt-get
        add to /etc/sudoers the following line:
        agent360 ALL=(ALL) NOPASSWD: /usr/bin/apt-get

        test by running:
        sudo -u agent360 agent360 test apt-updates

        Add to /etc/agent360.ini:
        [apt-updates]
        enabled = yes
        interval = 3600
        '''
        data = {}
        data['security'] = int(os.popen('sudo -n apt-get upgrade -s | grep Inst | grep security | wc -l').read())
        data['other'] = int(os.popen('sudo -n apt-get upgrade -s | grep Inst | grep -v security | wc -l').read())
        return data

if __name__ == '__main__':
    Plugin().execute()

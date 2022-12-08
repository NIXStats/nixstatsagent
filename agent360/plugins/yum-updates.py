#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import plugins

class Plugin(plugins.BasePlugin):
    __name__ = 'yum-updates'

    def run(self, config):
        '''
        updates for RHEL-based OS available from yum
        add to /etc/sudoers the following line:
        agent360 ALL=(ALL) NOPASSWD: /usr/bin/yum

        test by running:
        sudo -u agent360 agent360 test yum-updates

        Add to /etc/agent360.ini:
        [yum-updates]
        enabled = yes
        interval = 3600
        '''
        data = {}
        data['security'] = int(os.popen('yum -q list updates --security | grep -v Available | wc -l').read())
        data['all'] = int(os.popen('yum -q list updates | grep -v Available | wc -l').read())
        return data

if __name__ == '__main__':
    Plugin().execute()
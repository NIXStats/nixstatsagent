#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import plugins

class Plugin(plugins.BasePlugin):
    __name__ = 'plesk-wpt'

    def run(self, config):
        '''
        Grabbing some basic information from the plesk server
        add to /etc/sudoers the following line:
        agent360 ALL=(ALL) NOPASSWD: /usr/sbin/plesk

        test by running:
        sudo -u agent360 agent360 test plesk-wpt

        Add to /etc/agent360.ini:
        [plesk-wpt]
        enabled = yes
        interval = 3600
        '''
        data = {}
        data['wpsites'] = int(os.popen('sudo -n plesk ext wp-toolkit --list | grep -v "Main Domain ID" | wc -l').read())-1
        data['wpsites-live'] = int(os.popen('sudo -n plesk ext wp-toolkit --list | grep "Working" | wc -l').read())
        data['wpsites-outdated'] = int(os.popen('sudo -n plesk ext wp-toolkit --list | grep "Outdated WP" |  wc -l').read())
        data['wpsites-outdated-php'] = int(os.popen('sudo -n plesk ext wp-toolkit --list | grep "Outdated PHP" |  wc -l').read())
        data['wpsites-broken'] = int(os.popen('sudo -n plesk ext wp-toolkit --list | grep "Broken" | wc -l').read())
        return data

if __name__ == '__main__':
    Plugin().execute()

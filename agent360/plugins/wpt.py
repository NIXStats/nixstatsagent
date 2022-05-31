#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import plugins

class Plugin(plugins.BasePlugin):
    __name__ = 'WP Toolkit'

    def run(self, config):
        '''
        Grabbing some basic information from the your cPanel or Plesk server
        If you are using Plesk:
        add to /etc/sudoers the following line:
        agent360 ALL=(ALL) NOPASSWD: /usr/sbin/plesk

        For cPanel:
        agent360 ALL=(ALL) NOPASSWD: /usr/local/bin/wp-toolkit



        test by running:
        sudo -u agent360 agent360 test wpt
        Add to /etc/agent360.ini:
        [wpt]
        enabled = yes
        interval = 3600
        '''
        data = {}
        if os.path.isdir("/var/cpanel/users") is True:
            data['WordPress Websites'] = int(os.popen('sudo -n wp-toolkit --list | grep -v "Main Domain ID" | wc -l').read())-1
            data['WordPress Websites - Alive'] = int(os.popen('sudo -n wp-toolkit --list | grep "Working" | wc -l').read())
            data['WordPress Websites - Outdated'] = int(os.popen('sudo -n wp-toolkit --list | grep "Outdated WP" |  wc -l').read())
            data['WordPress Websites - Outdated PHP'] = int(os.popen('sudo -n wp-toolkit --list | grep "Outdated PHP" |  wc -l').read())
            data['WordPress Websites - Broken'] = int(os.popen('sudo -m wp-toolkit --list | grep "Broken" | wc -l').read())
            return data
        elif os.path.isdir("/opt/plesk") is True:
            data['WordPress Websites'] = int(os.popen('sudo -n plesk ext wp-toolkit --list | grep -v "Main Domain ID" | wc -l').read())-1
            data['WordPress Websites - Alive'] = int(os.popen('sudo -n plesk ext wp-toolkit --list | grep "Working" | wc -l').read())
            data['WordPress Websites - Outdated'] = int(os.popen('sudo -n plesk ext wp-toolkit --list | grep "Outdated WP" |  wc -l').read())
            data['WordPress Websites - Outdated PHP'] = int(os.popen('sudo -n plesk ext wp-toolkit --list | grep "Outdated PHP" |  wc -l').read())
            data['WordPress Websites - Broken'] = int(os.popen('sudo -n plesk ext wp-toolkit --list | grep "Broken" | wc -l').read())
            return data
        else:
            return "Wether cPanel nor Plesk detected"


if __name__ == '__main__':
    Plugin().execute()

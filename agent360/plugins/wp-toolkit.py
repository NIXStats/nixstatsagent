#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import plugins

class Plugin(plugins.BasePlugin):
    __name__ = 'wp-toolkit'
    __title__ = 'WP Toolkit'
    __description__ = 'Unified plugin for gathering metrics for WP Toolkit servers on cPanel and Plesk.'

    def run(self, config):
        '''
        Grabbing some basic information from your cPanel or Plesk server
        If you are using Plesk:
        add to /etc/sudoers the following line:
        agent360 ALL=(ALL) NOPASSWD: /usr/sbin/plesk

        For cPanel:
        agent360 ALL=(ALL) NOPASSWD: /usr/local/bin/wp-toolkit



        test by running:
        sudo -u agent360 agent360 test wp-toolkit
        Add to /etc/agent360.ini:
        [wp-toolkit]
        enabled = yes
        interval = 3600
        '''
        command = ''
        if os.path.isdir("/var/cpanel/users"):
            command = 'wp-toolkit'
        elif os.path.isdir("/opt/plesk"):
            command = 'plesk ext wp-toolkit'
        data = {}
        if command != '':
            data['WordPress Websites'] = int(os.popen('sudo -n ' + command + ' --list | grep -v "Main Domain ID" | grep . | wc -l').read())
            data['WordPress Websites - Alive'] = int(os.popen('sudo -n ' + command + ' --list | grep "Working" | wc -l').read())
            data['WordPress Websites - Outdated'] = int(os.popen('sudo -n ' + command + ' --list | grep "Outdated WP" |  wc -l').read())
            data['WordPress Websites - Outdated PHP'] = int(os.popen('sudo -n ' + command + ' --list | grep "Outdated PHP" |  wc -l').read())
            data['WordPress Websites - Broken'] = int(os.popen('sudo -n ' + command + ' --list | grep "Broken" | wc -l').read())
            return data
        else:
            return "Neither cPanel nor Plesk detected"


if __name__ == '__main__':
    Plugin().execute()

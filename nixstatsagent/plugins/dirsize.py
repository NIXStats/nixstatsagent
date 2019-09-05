#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import subprocess
import plugins
import json

class Plugin(plugins.BasePlugin):
    __name__ = 'dirsize'

    def run(self, config):
        '''
        Monitor total directory sizes, specify the directories you want to monitor in /etc/nixstats.ini
        '''

        data = {}
        my_dirs = config.get('dirsize', 'dirs').split(',')

        for dir in my_dirs:
            data[dir] = {'bytes': os.popen('du -c {} | grep total'.format(dir)).read().replace('total', '').rstrip()}

        return data


if __name__ == '__main__':
    Plugin().execute()

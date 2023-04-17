#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import plugins

class Plugin(plugins.BasePlugin):
    __name__ = 'loggedin'

    def run(self, config):
        '''
        Returns the number of users currently logged in.
        '''
        data = {}
        data['sessions'] = int(os.popen('/bin/users | wc -w').read())
        return data

if __name__ == '__main__':
    Plugin().execute()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import plugins

class Plugin(plugins.BasePlugin):
    __name__ = 'bird'

    def run(self, config):
        '''
        Monitor status of bgp sessions using bird
        '''
        data = {}
        data['established'] = int(os.popen('sudo birdc show proto | /bin/grep -c Established').read())
        data['connect'] = int(os.popen('sudo birdc show proto | /bin/grep -c Connect').read())
        data['active'] = int(os.popen('sudo birdc show proto | /bin/grep -c Active').read())
        data['conn_reset_bp'] = int(os.popen('sudo birdc show proto | /bin/grep -c "Connection reset by peer"').read())
        data['hold_timer'] = int(os.popen('sudo birdc show proto | /bin/grep -c "Hold timer expired"').read())
        return data

if __name__ == '__main__':
    Plugin().execute()

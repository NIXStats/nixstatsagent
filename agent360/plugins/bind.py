#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import plugins
import json

class Plugin(plugins.BasePlugin):
    __name__ = 'bind'

    def run(self, config):
        '''
        Monitoring bind nameserver

        You must have the bind statistics-channels configured
        and you must have jq installed for json processing.
        
        Usage for /etc/agent360.ini:
        [bind]
        enabled = yes
        port = 8053
        '''
        bport = config.get('bind', 'port')
        result = os.popen('curl -j http://localhost:' + str(bport) + '/json 2>/dev/null | jq ".qtypes * .rcodes * .nsstats"').read()
        data=json.loads(result)
        return data

if __name__ == '__main__':
    Plugin().execute()

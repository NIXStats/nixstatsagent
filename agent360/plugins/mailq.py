#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import plugins

class Plugin(plugins.BasePlugin):
    __name__ = 'mailq'
    def run(self, *unused):
        import os
        stream = os.popen("sudo /usr/bin/mailq | /usr/bin/tail -n1 | /usr/bin/gawk '{print $5}'")
        retval = stream.read()
        results = {}
        if len(retval) == 1:
            results['queue_size'] = 0
        else:
            results['queue_size'] = int(retval)
        return results

if __name__ == '__main__':
    Plugin().execute()

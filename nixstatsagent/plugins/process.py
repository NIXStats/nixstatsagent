#!/usr/bin/env python
# -*- coding: utf-8 -*-
import psutil
import plugins
import sys

class Plugin(plugins.BasePlugin):
    __name__ = 'process'

    def run(self, *unused):
        process = []
        for proc in psutil.process_iter():
            try:
                pinfo = proc.as_dict(attrs=[
                    'pid', 'name', 'ppid', 'exe', 'cmdline', 'username',
                    'cpu_percent', 'memory_percent', 'io_counters'
                ])
                pinfo['name'].encode('utf-8')
                if sys.platform != 'win32':
                    pinfo['username'].encode('utf-8')
                    pinfo['cmdline'] = ' '.join(pinfo['cmdline']).encode('utf-8').strip()
            except psutil.NoSuchProcess:
                pass
            except psutil.AccessDenied:
                pass
            else:
                process.append(pinfo)
        return process


if __name__ == '__main__':
    Plugin().execute()

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

                try:
                    pinfo['cmdline'] = ' '.join(pinfo['cmdline']).strip()
                except:
                    pass
                pinfo['cmdline'] = unicode(pinfo['cmdline'], sys.getdefaultencoding(), errors="replace").strip()
                pinfo['name'] = unicode(pinfo['name'], sys.getdefaultencoding(), errors="replace")
                pinfo['username'] = unicode(pinfo['username'], sys.getdefaultencoding(), errors="replace")
                try:
                    pinfo['exe'] = unicode(pinfo['exe'], sys.getdefaultencoding(), errors="replace")
                except:
                    pass
            except psutil.NoSuchProcess:
                pass
            except psutil.AccessDenied:
                pass
            except:
                pass
            else:
                process.append(pinfo)
        return process


if __name__ == '__main__':
    Plugin().execute()

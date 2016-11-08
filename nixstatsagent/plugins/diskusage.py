#!/usr/bin/env python


import os
import sys

import psutil

import plugins


class Plugin(plugins.BasePlugin):


    def run(self, *unused):
        disk = {}
        if sys.platform == "linux" or sys.platform == "linux2" or sys.platform == "darwin":
            disk['df'] = [s.split() for s in os.popen("df -Pl").read().splitlines()]
            disk['di'] = [s.split() for s in os.popen("df -iPl").read().splitlines()]
        elif sys.platform == "win32":
            disk = {}
            disk['df-windows'] = []
            for part in psutil.disk_partitions(all=False):
                if os.name == 'nt':
                    if 'cdrom' in part.opts or part.fstype == '':
                        # skip cd-rom drives with no disk in it; they may raise
                        # ENOENT, pop-up a Windows GUI error for a non-ready
                        # partition or just hang.
                        continue
                usage = psutil.disk_usage(part.mountpoint)
                diskdata = {}
                diskdata['info'] = part
                for key in usage._fields:
                    diskdata[key] = getattr(usage, key)
                disk['df-windows'].append(diskdata)
        return disk


if __name__ == '__main__':
    Plugin().execute()

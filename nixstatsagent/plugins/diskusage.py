#!/usr/bin/env python


import os
import psutil
import plugins


class Plugin(plugins.BasePlugin):


    def run(self, *unused):
        disk = {}
        disk['df-psutil'] = []
        for part in psutil.disk_partitions(True):
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
            disk['df-psutil'].append(diskdata)
        return disk


if __name__ == '__main__':
    Plugin().execute()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import psutil
import plugins


class Plugin(plugins.BasePlugin):
    __name__ = 'diskusage'

    def run(self, config):
        disk = {}
        disk['df-psutil'] = []
        for part in psutil.disk_partitions(False):
            if os.name == 'nt':
                if 'cdrom' in part.opts or part.fstype == '':
                    # skip cd-rom drives with no disk in it; they may raise
                    # ENOENT, pop-up a Windows GUI error for a non-ready
                    # partition or just hang.
                    continue
            try:
                usage = psutil.disk_usage(part.mountpoint)
                diskdata = {}
                diskdata['info'] = part
                for key in usage._fields:
                    diskdata[key] = getattr(usage, key)
                disk['df-psutil'].append(diskdata)
            except:
                pass

        try:
                force_df = config.get('diskusage', 'force_df')
        except:
                force_df = 'no'

        if len(disk['df-psutil']) == 0 or force_df == 'yes': 
            try:
                df_output_lines = [s.split() for s in os.popen("df -Pl").read().splitlines()] 
                del df_output_lines[0]
                for row in df_output_lines:
                    if row[0] == 'tmpfs':
                        continue
                    disk['df-psutil'].append({'info': [row[0], row[5],'',''], 'total': int(row[1])*1024, 'used': int(row[2])*1024, 'free': int(row[3])*1024, 'percent': row[4][:-1]}) 
            except:
                pass

        return disk


if __name__ == '__main__':
    Plugin().execute()
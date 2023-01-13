#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import plugins

class Plugin(plugins.BasePlugin):
    __name__ = 'diskinodes'

    def run(self, config):
        disk = {}
        try:
            df_output_lines = [s.split() for s in os.popen("df -Pli").read().splitlines()]
            del df_output_lines[0]
            for row in df_output_lines:
                if row[0] == 'tmpfs':
                    continue
                disk[row[0]] = {'total': int(row[1]), 'used': int(row[2]), 'free': int(row[3]), 'percent': row[4][:-1]}
        except:
            pass

        return disk


if __name__ == '__main__':
    Plugin().execute()

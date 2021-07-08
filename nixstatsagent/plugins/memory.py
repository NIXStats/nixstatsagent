#!/usr/bin/env python
# -*- coding: utf-8 -*-
import psutil
import plugins
import os

class Plugin(plugins.BasePlugin):
    __name__ = 'memory'

    def run(self, *unused):
        memory = {}
        mem = psutil.virtual_memory()
        for name in mem._fields:
            memory[name] = getattr(mem, name)

        if (memory['available'] == 0 or memory['buffers'] == 0) and os.name != 'nt':
            tot_m, used_m, free_m, sha_m, buf_m, cac_m, ava_m = map(int, os.popen('free -b -w').readlines()[1].split()[1:])
            memory['percent'] = 100-(((free_m+buf_m+cac_m)*100)/tot_m)
            memory['available'] = ava_m
            memory['buffers'] = buf_m
            memory['cached'] = cac_m
            memory['total'] = tot_m
            memory['used'] = used_m
            memory['shared'] = sha_m

        return memory

if __name__ == '__main__':
    Plugin().execute()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import psutil
import plugins

class Plugin(plugins.BasePlugin):
    __name__ = 'cpu_freq'

    def run(self, *unused):
        results = {}
        data = psutil.cpu_freq(percpu=True)
        cpu_number = -1
        for cpu in data:
            core = {}
            cpu_number = cpu_number+1
            results[cpu_number] = {}
            for key in cpu._fields:
                core[key] = getattr(cpu, key)
            results[cpu_number] = core['current']
        return results


if __name__ == '__main__':
    Plugin().execute()

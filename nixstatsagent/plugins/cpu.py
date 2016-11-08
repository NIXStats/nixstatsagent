#!/usr/bin/env python

import psutil

import plugins


class Plugin(plugins.BasePlugin):


    def run(self, *unused):
        name = 'cpu'
        results = {}
        data = psutil.cpu_times_percent(interval=1, percpu=True)
        cpu_number = -1
        for cpu in data:
            core = {}
            cpu_number = cpu_number+1
            results[cpu_number] = {}
            for key in cpu._fields:
                core[key] = getattr(cpu, key)
            results[cpu_number] = core
        return results
    
    
if __name__ == '__main__':
    Plugin().execute()

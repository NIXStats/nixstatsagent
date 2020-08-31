#!/usr/bin/env python
# -*- coding: utf-8 -*-
import psutil
import plugins
import time

class Plugin(plugins.BasePlugin):
    __name__ = 'cpu'

    def run(self, *unused):
        prev_cache = self.get_agent_cache()  # Get absolute values from previous check
        next_cache = {}
        next_cache['ts'] = time.time()
        results = {}
        data_stats = psutil.cpu_stats()

        # if there's no previous cache, build the first baseline value
        # so we don't have all 0% values, should happen only the first time
        try:
           prev_cache['ts']
        except KeyError:
           data = psutil.cpu_times(percpu=True)
           cpu_number = -1
           prev_cache['ts'] = time.time()
           for cpu in data:
              cpu_number = cpu_number+1
              prev_cache[cpu_number] = {}
              for key in cpu._fields:
                  prev_cache[cpu_number][key] = getattr(cpu, key)
           time.sleep(0.5)

        data = psutil.cpu_times(percpu=True)
        cpu_number = -1
        for cpu in data:
            cpu_number = cpu_number+1
            results[cpu_number] = {}
            next_cache[cpu_number] = {}
            for key in cpu._fields:
                next_cache[cpu_number][key] = getattr(cpu, key)
                try:
                    time_delta = time.time() - prev_cache['ts']
                except:
                    continue
                if time_delta <= 0:
                    continue
                cpu_time_delta = getattr(cpu, key) - prev_cache[cpu_number][key]
                if cpu_time_delta < 0:
                    cpu_time_delta = 0
                results[cpu_number][key] = cpu_time_delta / time_delta * 100
                if results[cpu_number][key] > 100:
                    results[cpu_number][key] = 100
                if results[cpu_number][key] < 0:
                    results[cpu_number][key] = 0
        self.set_agent_cache(next_cache)
        return results


if __name__ == '__main__':
    Plugin().execute()

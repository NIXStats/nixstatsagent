#!/usr/bin/env python

import psutil


import plugins


class Plugin(plugins.BasePlugin):


    def run(self, *unused):
        memory = {}
        mem = psutil.virtual_memory()
        for name in mem._fields:
            memory[name] = getattr(mem, name)
        return memory


if __name__ == '__main__':
    Plugin().execute()

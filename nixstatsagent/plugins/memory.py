#!/usr/bin/env python
# -*- coding: utf-8 -*-
import psutil
import plugins


class Plugin(plugins.BasePlugin):
    __name__ = 'memory'

    def run(self, *unused):
        memory = {}
        mem = psutil.virtual_memory()
        for name in mem._fields:
            memory[name] = getattr(mem, name)
        return memory


if __name__ == '__main__':
    Plugin().execute()

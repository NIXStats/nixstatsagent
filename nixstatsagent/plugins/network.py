#!/usr/bin/env python
# -*- coding: utf-8 -*-
import psutil
import plugins


class Plugin(plugins.BasePlugin):
    __name__ = 'network'

    def run(self, *unused):
        return psutil.net_io_counters(pernic=True)


if __name__ == '__main__':
    Plugin().execute()

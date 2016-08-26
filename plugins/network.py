#!/usr/bin/env python


import psutil


import plugins


class Plugin(plugins.BasePlugin):


    def run(self, *unused):
        return psutil.net_io_counters(pernic=True)


if __name__ == '__main__':
    Plugin().execute()


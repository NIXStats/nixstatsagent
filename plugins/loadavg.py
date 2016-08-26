#!/usr/bin/env python

import os

import plugins


class Plugin(plugins.BasePlugin):


    def run(self, *unused):
        return os.getloadavg()


if __name__ == '__main__':
    Plugin().execute()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import plugins
import sys

class Plugin(plugins.BasePlugin):
    __name__ = 'loadavg'

    def run(self, *unused):
        if sys.platform == 'win32':
            return None
        else:
            return os.getloadavg()


if __name__ == '__main__':
    Plugin().execute()

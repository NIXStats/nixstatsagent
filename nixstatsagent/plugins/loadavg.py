#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import plugins


class Plugin(plugins.BasePlugin):
    __name__ = 'loadavg'

    def run(self, *unused):
        return os.getloadavg()


if __name__ == '__main__':
    Plugin().execute()

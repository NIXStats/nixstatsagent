#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import plugins


class Plugin(plugins.BasePlugin):
    __name__ = 'sleeper'

    def run(self, *unused):
        time.sleep(60 * 60 * 24)


if __name__ == '__main__':
    Plugin().run()

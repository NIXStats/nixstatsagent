#!/usr/bin/env python


import time

import plugins


class Plugin(plugins.BasePlugin):

    
    def run(self, *unused):
        time.sleep(60 * 60 * 24)


if __name__ == '__main__':
    Plugin().run()

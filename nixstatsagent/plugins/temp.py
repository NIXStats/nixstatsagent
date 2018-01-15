#!/usr/bin/env python
# -*- coding: utf-8 -*-
import plugins
import psutil

class Plugin(plugins.BasePlugin):
    __name__ = 'temp'

    def run(self, *unused):
        '''
        expirimental plugin used to collect temperature from system sensors
        plugin can be tested by running nixstatsagent test temp
        '''
        data = {}

        if not hasattr(psutil, "sensors_temperatures"):
            return "platform not supported"

        try:
                temps = psutil.sensors_temperatures()
        except:
                return "can't read any temperature"

        for device, temp in temps.items():
            for value in temp:
                type = value[0]
                if value[0] == '':
                    type = device
                data[type] = value[1]
        return data


if __name__ == '__main__':
    Plugin().execute()

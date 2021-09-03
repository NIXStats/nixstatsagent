#!/usr/bin/env python
# -*- coding: utf-8 -*-
import plugins
import psutil
import sys

class Plugin(plugins.BasePlugin):
    __name__ = 'temp'

    def run(self, *unused):
        '''
        expirimental plugin used to collect temperature from system sensors
        plugin can be tested by running nixstatsagent test temp
        '''
        data = {}

        if sys.platform == "win32":
            try:
                import wmi
            except:
                return 'wmi module not installed.'

            try:
                w = wmi.WMI(namespace="root\OpenHardwareMonitor")
                temperature_infos = w.Sensor()
                for sensor in temperature_infos:
                    if sensor.SensorType==u'Temperature':
                        data[sensor.Parent.replace('/','-').strip('-')] = sensor.Value
                return data
            except:
                return 'Could not fetch temperature data from OpenHardwareMonitor.'
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

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import plugins
import sys

class Plugin(plugins.BasePlugin):
    __name__ = 'gpu'

    def run(self, *unused):
        '''
        expirimental plugin used to collect GPU load from OpenHardWareMonitor (Windows)
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
                    if sensor.SensorType==u'Load' and sensor.Name==u'GPU Core':
                        data[sensor.Parent.replace('/','-').strip('-')] = sensor.Value
            except:
                return 'Could not fetch GPU Load data from OpenHardwareMonitor.'

        return data


if __name__ == '__main__':
    Plugin().execute()

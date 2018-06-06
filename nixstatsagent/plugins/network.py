#!/usr/bin/env python
# -*- coding: utf-8 -*-
import psutil
import plugins


class Plugin(plugins.BasePlugin):
    __name__ = 'network'

    def run(self, config):
        '''
        Network monitoring plugin.
        To only enable certain interfaces add below [network]:
        interfaces = eth1,eth3,...
        '''

        try:
            enabled_interfaces = config.get('network', 'interfaces').split(',')
        except:
            enabled_interfaces = False

        if enabled_interfaces is False:
            return psutil.net_io_counters(pernic=True)
        else:
	    returndata = {}
	    interfaces = psutil.net_io_counters(pernic=True)
            for interface in interfaces:
		if interface in enabled_interfaces:
		    returndata[interface] = interfaces[interface]
            return returndata
        return None


if __name__ == '__main__':
    Plugin().execute()

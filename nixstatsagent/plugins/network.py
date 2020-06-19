#!/usr/bin/env python
# -*- coding: utf-8 -*-
import psutil
import plugins
import time

class Plugin(plugins.BasePlugin):
    __name__ = 'network'

    def run(self, config):
        '''
        Network monitoring plugin.
        To only enable certain interfaces add below [network]:
        interfaces = eth1,eth3,...
        '''

        absolute = dict()
        absolute['ts'] = time.time()
        prev_cache = self.get_agent_cache()  # Get absolute values from previous check

        try:
            enabled_interfaces = config.get('network', 'interfaces').split(',')
        except:
            enabled_interfaces = False

        returndata = {}
        interfaces = psutil.net_io_counters(pernic=True)
        for interface, stats in interfaces.items():
            if enabled_interfaces is not False:
                if interface not in enabled_interfaces:
                    continue
            try:
                prev_cache[interface]
            except:
                prev_cache[interface] = {}
            absolute[interface] = {}
            absolute[interface]['ts'] = time.time()
            absolute[interface]['bytes_sent'] = stats.bytes_sent
            absolute[interface]['bytes_recv'] = stats.bytes_recv
            absolute[interface]['packets_sent'] = stats.packets_sent
            absolute[interface]['packets_recv'] = stats.packets_recv
            absolute[interface]['errin'] = stats.errin
            absolute[interface]['errout'] = stats.errout
            absolute[interface]['dropin'] = stats.dropin
            absolute[interface]['dropout'] = stats.dropout
            returndata[interface] = {}
            returndata[interface]['bytes_sent'] = self.absolute_to_per_second('bytes_sent', stats.bytes_sent, prev_cache[interface])
            returndata[interface]['bytes_recv'] = self.absolute_to_per_second('bytes_recv', stats.bytes_recv, prev_cache[interface])
            returndata[interface]['packets_sent'] = self.absolute_to_per_second('packets_sent', stats.packets_sent, prev_cache[interface])
            returndata[interface]['packets_recv'] = self.absolute_to_per_second('packets_recv', stats.packets_recv, prev_cache[interface])
            returndata[interface]['errin'] = self.absolute_to_per_second('errin', stats.errin, prev_cache[interface])
            returndata[interface]['errout'] = self.absolute_to_per_second('errout', stats.errout, prev_cache[interface])
            returndata[interface]['dropin'] = self.absolute_to_per_second('dropin', stats.dropin, prev_cache[interface])
            returndata[interface]['dropout'] = self.absolute_to_per_second('dropout', stats.dropout, prev_cache[interface])
        self.set_agent_cache(absolute)
        return returndata


if __name__ == '__main__':
    Plugin().execute()

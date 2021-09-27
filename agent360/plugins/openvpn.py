#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import plugins
import time
from openvpn_status import parse_status


class Plugin(plugins.BasePlugin):
    __name__ = 'openvpn'

    def run(self, config):
        '''
        OpenVPN monitoring, needs access to openvpn-status.log file.
        pip install openvpn-status
        or
        pip3 install openvpn-status

        In /etc/agent360.ini to enable put:
        [openvpn]
        enabled = yes
        status_path = /etc/openvpn/openvpn-status.log

        test the plugin by running: sudo -u agent360 agent360 test OpenVPN

        If you are having permission issues try to run the agent as root user:
        https://docs.platform360.io/monitoring360/development/run-the-monitoring-agent-as-the-root-user/
        '''
        openvpn_clients = {}
        last_value = {}
        prev_cache = self.get_agent_cache()  # Get absolute values from previous check

        try:
            with open(config.get('openvpn', 'status_path')) as logfile:
                status = parse_status(logfile.read())
        except Exception as e:
            return e

        try:
            openvpn_clients['containers'] = len(status.client_list.items())
            for key, client in status.client_list.items():
                 client.common_name = client.common_name.replace('.', '-')
                 openvpn_clients[client.common_name] = {}
                 bytes_out = int(client.bytes_sent)
                 bytes_in = int(client.bytes_received)
                 openvpn_clients[client.common_name]['net_out_bytes'] = self.absolute_to_per_second('%s_%s' % (client.common_name, 'net_out_bytes'), bytes_out, prev_cache)
                 openvpn_clients[client.common_name]['net_in_bytes'] = self.absolute_to_per_second('%s_%s' % (client.common_name, 'net_in_bytes'), bytes_in, prev_cache)

                 last_value['%s_%s' % (client.common_name, 'net_in_bytes')] = bytes_in
                 last_value['%s_%s' % (client.common_name, 'net_out_bytes')] = bytes_out
        except Exception as e:
            return e

        last_value['ts'] = time.time()
        self.set_agent_cache(last_value)

        return openvpn_clients

if __name__ == '__main__':
    Plugin().execute()

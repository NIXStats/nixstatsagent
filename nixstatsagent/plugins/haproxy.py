#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import plugins
import csv
import requests


class Plugin(plugins.BasePlugin):
    __name__ = 'haproxy'

    def run(self, config):
            results = dict()
            next_cache = dict()
            try:
                username = config.get('haproxy', 'username')
                password = config.get('haproxy', 'password')
                user_pass = (username, password)
            except:
                user_pass = False
            request = requests.get(config.get('haproxy', 'status_page_url'), auth=user_pass)
            next_cache['ts'] = time.time()
            prev_cache = self.get_agent_cache()  # Get absolute values from previous check
            if request.status_code is 200:
                response = request.text.split("\n")
            else:
                return "Could not load haproxy status page: {}".format(request.text)

            non_delta = (
            'qcur',
            'qmax',
            'scur',
            'smax',
            'slim',
            'stot',
            'weight',
            # 'act',
            # 'bck',
            # 'chkfail',
            # 'chkdown',
            # 'lastchg',
            # 'downtime',
            'qlimit',
            # 'pid',
            # 'iid',
            # 'sid',
            'throttle',
            'lbtot',
            'tracked',
            # 'type',
            'rate',
            'rate_lim',
            'rate_max',
            # 'check_status',
            # 'check_code',
            # 'check_duration',
            'hanafail',
            'req_rate',
            'req_rate_max',
            'req_tot',
            # 'lastsess',
            # 'last_chk',
            # 'last_agt',
            # 'qtime',
            # 'ctime',
            # 'rtime',
            # 'ttime',
            # 'agent_status',
            # 'agent_code',
            # 'agent_duration',
            # 'agent_health',
            'conn_rate',
            'conn_rate_max',
            'conn_tot',
            # 'intercepted'
            )

            delta = (
            'bin',
            'bout',
            'cli_abrt',
            'srv_abrt',
            'intercepted',
            'hrsp_1xx',
            'hrsp_2xx',
            'hrsp_3xx',
            'hrsp_4xx',
            'check_rise',
            'check_fall',
            'check_health',
            'agent_rise',
            'agent_fall',
            'hrsp_5xx',
            'comp_in',
            'comp_out',
            'comp_byp',
            'comp_rsp',
            'hrsp_other',
            'dcon',
            'dreq',
            'dresp',
            'ereq',
            'econ',
            'eresp',
            'wretr',
            'wredis',
            'dses'
            )
            csv_reader = csv.DictReader(response)
            data = dict()
            constructors = [str, float]
            for row in csv_reader:
                results[row["# pxname"]+"/"+row["svname"]] = {}
                data[row["# pxname"]+"/"+row["svname"]] = {}
                try:
                    prev_cache[row["# pxname"]+"/"+row["svname"]]['ts'] = prev_cache['ts']
                except KeyError:
                    prev_cache[row["# pxname"]+"/"+row["svname"]] = {}

                for k, v in row.items():
                    for c in constructors:
                        try:
                            v = c(v)
                        except ValueError:
                            pass
                    if k in non_delta:
                        results[row["# pxname"]+"/"+row["svname"]][k] = v
                    elif k in delta and type(v) is not str:
                        results[row["# pxname"]+"/"+row["svname"]][k] = self.absolute_to_per_second(k, float(v), prev_cache[row["# pxname"]+"/"+row["svname"]])
                        data[row["# pxname"]+"/"+row["svname"]][k] = float(v)
                    else:
                        pass

            data['ts'] = time.time()
            self.set_agent_cache(data)

            return results


if __name__ == '__main__':
    Plugin().execute()

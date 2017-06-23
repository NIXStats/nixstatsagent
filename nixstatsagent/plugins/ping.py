#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
from subprocess import Popen, PIPE, CalledProcessError
import sys
import plugins


def _get_match_groups(ping_output, regex):
    match = regex.search(ping_output)
    if not match:
        return False
    else:
        return match.groups()


def system_command(Command, newlines=True):
    Output = ""
    Error = ""
    try:
        proc = Popen(Command.split(), stdout=PIPE)
        Output = proc.communicate()[0]
    except Exception:
        pass

    if Output:
        if newlines is True:
            Stdout = Output.split("\\n")
        else:
            Stdout = Output
    else:
        Stdout = []
    if Error:
        Stderr = Error.split("\n")
    else:
        Stderr = []

    return (Stdout, Stderr)


def collect_ping(hostname):
    if sys.platform.startswith('linux') or sys.platform.startswith('freebsd'):
    #if sys.platform == "linux" or sys.platform == "linux2":
        response = str(system_command("ping -W 5 -c 1 " + hostname, False)[0])
        try:
            matcher = re.compile(r'(\d+.\d+)/(\d+.\d+)/(\d+.\d+)/(\d+.\d+)')
            minping, avgping, maxping, jitter = _get_match_groups(response, matcher)
            response = avgping
        except Exception:
            #response = 9999
            response = -1
    elif sys.platform == "darwin":
        response = str(system_command("ping -c 1 " + hostname, False)[0])
        # matcher = re.compile(r'min/avg/max/stddev = (\d+)/(\d+)/(\d+)/(\d+) ms')
        # min, avg, max, stddev = _get_match_groups(response, matcher)
        matcher = re.compile(r'(\d+.\d+)/(\d+.\d+)/(\d+.\d+)/(\d+.\d+)')
        matched = _get_match_groups(response, matcher)
        if matched is False:
            #response = 0
            response = -1
        else:
            minping, avgping, maxping, jitter = matched
            response = avgping
    elif sys.platform == "win32":
        #response = 0
        response = -1
        try:
            ping = Popen(["ping", "-n", "1 ", hostname], stdout=PIPE, stderr=PIPE)
            out, error = ping.communicate()
            if out:
                try:
                    response = int(re.findall(r"Average = (\d+)", out)[0])
                except Exception:
                    pass
            else:
                #response = 0
                response = -1
        except CalledProcessError:
            pass
    else:
        #response = float(system_command("ping -W -c 1 " + hostname))
        response = -1
    return {'avgping': response, 'host': hostname}


class Plugin(plugins.BasePlugin):
    __name__ = 'ping'

    def run(self, config):
        data = {}
        my_hosts = config.get('ping', 'hosts').split(',')
        data['ping'] = []
        for host in my_hosts:
            data['ping'].append(collect_ping(host))
        return data['ping']


if __name__ == '__main__':
    Plugin().execute()

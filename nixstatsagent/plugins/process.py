#!/usr/bin/env python

import netifaces
import os
import platform
from subprocess import Popen, PIPE
import sys


try:
    import pwd
except ImportError:
    pass

import psutil

import plugins

def procStats(pid):
    process = {}
    process['pid'] = int(pid)

    if os.path.exists('/proc/%s/cmdline' % pid):
        with open(os.path.join('/proc/', pid, 'cmdline'), 'r') as file:
            process['cmdline'] = file.readline().replace('\x00', ' ')
        if process['cmdline'].strip() == '':
            return False
        else:
            if os.path.exists('/proc/%s/stat' % pid):
                pidfile = open(os.path.join('/proc/', pid, 'stat'))
                if pidfile:
                    proctimes = pidfile.readline()
                    process['name'] = proctimes.split(' ')[1].strip(')').strip('(')
                    # count total process used time
                    process['ctime'] = float(int(proctimes.split(' ')[13]) + int(proctimes.split(' ')[14]))

                if os.path.exists('/proc/%s/io' % pid):
                    process['io'] = {}
                    f = open(os.path.join('/proc/', pid, 'io'))
                    if f:
                        for line in f:
                            process['io'][line.strip().split(': ')[0]] = line.strip().split(': ')[1]
                if os.path.exists('/proc/%s/status' % pid):
                    f = open(os.path.join('/proc/', pid, 'status'))
                    if f:
                        for line in f:
                            if line.split(':')[0] == 'Uid':
                                process['username'] = pwd.getpwuid(int(line.split(':')[1].split('\t')[1])).pw_name
                            if line.split(':')[0] == 'PPid':
                                process['ppid'] = int(line.split(':')[1].split('\t')[1])
                            if line.split(':')[0] == 'VmSize':
                                process['vmsize'] = line.split(':')[1].split('kB')[0].strip()
                            if line.split(':')[0] == 'State':
                                process['cmdline'] += line.split(':')[1].strip()
                            if line.split(':')[0] == 'VmRSS':
                                process['vmrss'] = line.split(':')[1].split('kB')[0].strip()
                                break
                return process

def getPids():
    return [int(x) for x in os.listdir(b'/proc') if x.isdigit()]


class Plugin(plugins.BasePlugin):


    def run(self, *unused):
        process = []
        if sys.platform == "linux" or sys.platform == "linux2":
            processlist = []
            for pid in getPids():
                proc = procStats(str(pid))
                if proc != False:
                    process.append(proc)
        elif sys.platform == "darwin":
            for proc in psutil.process_iter():
                try:
                    pinfo = proc.as_dict(attrs=['pid', 'name', 'ppid', 'exe', 'cmdline', 'username', 'cpu_percent','memory_percent'])
                except psutil.NoSuchProcess:
                    pass
                else:
                    if ''.join(pinfo['cmdline']) != '':
                        process.append(pinfo)
        else:
            for proc in psutil.process_iter():
                try:
                    pinfo = proc.as_dict(attrs=['pid', 'name', 'ppid', 'exe', 'cmdline', 'username', 'cpu_percent','memory_percent'])
                except psutil.NoSuchProcess:
                    pass
                else:
                    process.append(pinfo)
        return process


if __name__ == '__main__':
    Plugin().execute()

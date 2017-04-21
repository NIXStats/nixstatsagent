#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# collectd-iostat-python
# ======================
#
# Collectd-iostat-python is an iostat plugin for collectd that allows you to
# graph Linux iostat metrics in Graphite or other output formats that are
# supported by collectd.
#
# https://github.com/powdahound/redis-collectd-plugin
#   - was used as template
# https://github.com/keirans/collectd-iostat/
#   - was used as inspiration and contains some code from
# https://bitbucket.org/jakamkon/python-iostat
#   - by Kuba Kończyk <jakamkon at users.sourceforge.net>
#

import os
import signal
import subprocess
import sys
import psutil
import plugins

__version__ = '0.0.3'
__author__ = 'denis.zhdanov@gmail.com'


class IOStatError(Exception):
    pass


class CmdError(IOStatError):
    pass


class ParseError(IOStatError):
    pass


class IOStat(object):
    def __init__(self, path='iostat', interval=2, count=2, disks=[]):
        self.path = path
        self.interval = interval
        self.count = count
        self.disks = disks

    def parse_diskstats(self, input):
        '''
        Parse iostat -d and -dx output.If there are more
        than one series of statistics, get the last one.
        By default parse statistics for all avaliable block devices.

        @type input: C{string}
        @param input: iostat output

        @type disks: list of C{string}s
        @param input: lists of block devices that
        statistics are taken for.

        @return: C{dictionary} contains per block device statistics.
        Statistics are in form of C{dictonary}.
        Main statistics:
          tps  Blk_read/s  Blk_wrtn/s  Blk_read  Blk_wrtn
        Extended staistics (available with post 2.5 kernels):
          rrqm/s  wrqm/s  r/s  w/s  rsec/s  wsec/s  rkB/s  wkB/s  avgrq-sz \
          avgqu-sz  await  svctm  %util
        See I{man iostat} for more details.
        '''
        dstats = {}
        dsi = input.rfind('Device:')
        if dsi == -1:
            raise ParseError('Unknown input format: %r' % input)

        ds = input[dsi:].splitlines()
        hdr = ds.pop(0).split()[1:]

        for d in ds:
            if d:
                d = d.split()
                dev = d.pop(0)
                if (dev in self.disks) or not self.disks:
                    dstats[dev] = dict([(k, float(v)) for k, v in zip(hdr, d)])

        return dstats

    def sum_dstats(self, stats, smetrics):
        '''
        Compute the summary statistics for chosen metrics.
        '''
        avg = {}

        for disk, metrics in stats.iteritems():
            for mname, metric in metrics.iteritems():
                if mname not in smetrics:
                    continue
                if mname in avg:
                    avg[mname] += metric
                else:
                    avg[mname] = metric

        return avg

    def _run(self, options=None):
        '''
        Run iostat command.
        '''
        close_fds = 'posix' in sys.builtin_module_names
        args = '%s %s %s %s %s' % (
            self.path,
            ''.join(options),
            self.interval,
            self.count,
            ' '.join(self.disks),
        )

        return subprocess.Popen(
            args,
            bufsize=1,
            shell=True,
            stdout=subprocess.PIPE,
            close_fds=close_fds)

    @staticmethod
    def _get_childs_data(child):
        '''
        Return child's data when avaliable.
        '''
        (stdout, stderr) = child.communicate()
        ecode = child.poll()

        if ecode != 0:
            raise CmdError('Command %r returned %d' % (child.cmd, ecode))

        return stdout

    def get_diskstats(self):
        '''
        Get all avaliable disks statistics that we can get.
        '''
        dstats = self._run(options=['-kNd'])
        extdstats = self._run(options=['-kNdx'])
        dsd = self._get_childs_data(dstats)
        edd = self._get_childs_data(extdstats)
        ds = self.parse_diskstats(dsd)
        eds = self.parse_diskstats(edd)

        for dk, dv in ds.iteritems():
            if dk in eds:
                ds[dk].update(eds[dk])

        return ds


class IOMon(object):
    def __init__(self):
        self.plugin_name = 'collectd-iostat-python'
        self.iostat_path = '/usr/bin/iostat'
        self.iostat_interval = 2
        self.iostat_count = 2
        self.iostat_disks = []
        self.iostat_nice_names = False
        self.iostat_disks_regex = ''
        self.verbose_logging = False
        self.names = {
            'tps': {'t': 'transfers_per_second'},
            'Blk_read/s': {'t': 'blocks_per_second', 'ti': 'read'},
            'kB_read/s': {'t': 'bytes_per_second', 'ti': 'read', 'm': 10e3},
            'MB_read/s': {'t': 'bytes_per_second', 'ti': 'read', 'm': 10e6},
            'Blk_wrtn/s': {'t': 'blocks_per_second', 'ti': 'write'},
            'kB_wrtn/s': {'t': 'bytes_per_second', 'ti': 'write', 'm': 10e3},
            'MB_wrtn/s': {'t': 'bytes_per_second', 'ti': 'write', 'm': 10e6},
            'Blk_read': {'t': 'blocks', 'ti': 'read'},
            'kB_read': {'t': 'bytes', 'ti': 'read', 'm': 10e3},
            'MB_read': {'t': 'bytes', 'ti': 'read', 'm': 10e6},
            'Blk_wrtn': {'t': 'blocks', 'ti': 'write'},
            'kB_wrtn': {'t': 'bytes', 'ti': 'write', 'm': 10e3},
            'MB_wrtn': {'t': 'bytes', 'ti': 'write', 'm': 10e6},
            'rrqm/s': {'t': 'requests_merged_per_second', 'ti': 'read'},
            'wrqm/s': {'t': 'requests_merged_per_second', 'ti': 'write'},
            'r/s': {'t': 'per_second', 'ti': 'read'},
            'w/s': {'t': 'per_second', 'ti': 'write'},
            'rsec/s': {'t': 'sectors_per_second', 'ti': 'read'},
            'rkB/s': {'t': 'bytes_per_second', 'ti': 'read', 'm': 10e3},
            'rMB/s': {'t': 'bytes_per_second', 'ti': 'read', 'm': 10e6},
            'wsec/s': {'t': 'sectors_per_second', 'ti': 'write'},
            'wkB/s': {'t': 'bytes_per_second', 'ti': 'write', 'm': 10e3},
            'wMB/s': {'t': 'bytes_per_second', 'ti': 'write', 'm': 10e6},
            'avgrq-sz': {'t': 'avg_request_size'},
            'avgqu-sz': {'t': 'avg_request_queue'},
            'await': {'t': 'avg_wait_time'},
            'r_await': {'t': 'avg_wait_time', 'ti': 'read'},
            'w_await': {'t': 'avg_wait_time', 'ti': 'write'},
            'svctm': {'t': 'avg_service_time'},
            '%util': {'t': 'percent', 'ti': 'util'}
        }


def restore_sigchld():
    '''
    Restore SIGCHLD handler for python <= v2.6
    It will BREAK exec plugin!!!
    See https://github.com/deniszh/collectd-iostat-python/issues/2 for details
    '''
    if sys.version_info[0] == 2 and sys.version_info[1] <= 6:
        signal.signal(signal.SIGCHLD, signal.SIG_DFL)


def diskstats_parse(dev=None):
    file_path = '/proc/diskstats'
    result = {}

    # ref: http://lxr.osuosl.org/source/Documentation/iostats.txt
    columns_disk = ['m', 'mm', 'dev', 'reads', 'rd_mrg', 'rd_sectors',
                    'ms_reading', 'writes', 'wr_mrg', 'wr_sectors',
                    'ms_writing', 'cur_ios', 'ms_doing_io', 'ms_weighted']

    columns_partition = ['m', 'mm', 'dev', 'reads', 'rd_sectors', 'writes', 'wr_sectors']

    lines = open(file_path, 'r').readlines()
    for line in lines:
        if line == '':
            continue
        split = line.split()
        if len(split) == len(columns_disk):
            columns = columns_disk
        elif len(split) == len(columns_partition):
            columns = columns_partition
        else:
            # No match
            continue

        data = dict(zip(columns, split))

        if int(data['mm']) > 0:
            continue

        if "loop" in data['dev'] or "ram" in data['dev']:
            continue
        
        if dev is not None and dev != data['dev']:
            continue
        for key in data:
            if key != 'dev':
                data[key] = int(data[key])
        result[data['dev']] = data

    return result


class Plugin(plugins.BasePlugin):
    __name__ = 'iostat'

    def run(self, *unused):
        if(os.path.isfile("/proc/diskstats")):
            return diskstats_parse()
        elif(os.path.isfile("/usr/bin/iostat")):
            iostat = IOStat()
            ds = iostat.get_diskstats()
            if ds:
                return ds
        else:
            results = {}
            diskdata = psutil.disk_io_counters(perdisk=True)
            for device, values in diskdata.items():
                device_stats = {}
                for key_value in values._fields:
                    device_stats[key_value] = getattr(values, key_value)
                results[device] = device_stats
            return results


if __name__ == '__main__':
    Plugin().execute()

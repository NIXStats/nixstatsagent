#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import glob
import pathlib
import pwd
import re
import time

import plugins


class Plugin(plugins.BasePlugin):
    __name__ = 'plesk-cgroups'

    def run(self, *unused):
        accounting = {}
        cache = self.get_agent_cache()
        uid_re = re.compile('\d+')

        # This silently depends on cgroup mounted virtual file systems
        # and SystemD user slices

        sysfs_prefix = '/sys/fs/cgroup/'
        sysfs_suffix = 'user.slice/user-*.slice'
        for user_slice in (
            glob.glob(sysfs_prefix + sysfs_suffix) +  # cgroup v2
            glob.glob(sysfs_prefix + 'systemd/' + sysfs_suffix)  # cgroup v1
        ):

            accounting[user_slice] = {}
            if not user_slice in cache:
                cache[user_slice] = {}

            accounting[user_slice]['uid'] = uid = \
                int(uid_re.search(user_slice).group())

            # Resolve uid to username
            try:
                accounting[user_slice]['username'] = pwd.getpwuid(uid).pw_name
            except KeyError:
                # There's no guarantee that the uid has a name
                pass

            # This silently depends on the corresponding CGroup controllers
            # being individually enabled

            # Memory accounting
            try:
                # cgroup v2
                with pathlib.Path(user_slice, 'memory.current').open() as f:
                    accounting[user_slice]['memory.current'] = \
                        int(f.read().strip())
            except FileNotFoundError:
                try:
                    # cgroup v1
                    with pathlib.Path(
                        sysfs_prefix,
                        'memory',
                        'user.slice',
                        'user-{}.slice'.format(uid),
                        'memory.usage_in_bytes'
                    ).open() as f:
                        accounting[user_slice]['memory.usage_in_bytes'] = \
                            int(f.read().strip())
                except FileNotFoundError:
                    pass

            # IO accounting
            try:
                # cgroup v2
                with pathlib.Path(user_slice, 'io.stat').open() as f:
                    accounting[user_slice]['io.stat'] = a = {}
                    if not 'io.stat' in cache[user_slice]:
                        cache[user_slice]['io.stat'] = c = {}
                    for line in f.readlines():
                        devnum, metrics = line.split(maxsplit=1)
                        if not devnum in a:
                            a[devnum] = {}
                            a[devnum]['ts'] = time.time()
                        if not devnum in c:
                            c[devnum] = {}
                        for kv in metrics.split():
                            k, v = kv.split('=')
                            a[devnum][k] = self.absolute_to_per_second(
                                k, int(v), c[devnum]
                            )
                            c[devnum][k] = int(v)
            except FileNotFoundError:
                try:
                    # cgroup v1
                    with pathlib.Path(
                        sysfs_prefix,
                        'blkio',
                        'user.slice',
                        'user-{}.slice'.format(uid),
                        'blkio.throttle.io_service_bytes'
                    ).open() as f:
                        accounting[user_slice]\
                            ['blkio.throttle.io_service_bytes'] = a = {}
                        if not 'blkio.throttle.io_service_bytes' \
                            in cache[user_slice]:
                            cache[user_slice]\
                                ['blkio.throttle.io_service_bytes'] = c = {}
                        for line in f.readlines():
                            try:
                                devnum, k, v = line.split()
                            except ValueError:
                                # The last line is "Total",
                                # it has only 2 values and is ignored
                                pass
                            if not devnum in a:
                                a[devnum] = {}
                                a[devnum]['ts'] = time.time()
                            if not devnum in c:
                                c[devnum] = {}
                            a[devnum][k] = self.absolute_to_per_second(
                                k, int(v), c[devnum]
                            )
                            c[devnum][k] = int(v)
                except FileNotFoundError:
                    pass

            # CPU accounting
            try:
                # cgroup v2
                with pathlib.Path(user_slice, 'cpu.stat').open() as f:
                    accounting[user_slice]['cpu.stat'] = a = {}
                    if not 'cpu.stat' in cache[user_slice]:
                        cache[user_slice]['cpu.stat'] = c = {}
                    a['ts'] = time.time()
                    for line in f.readlines():
                        k, v = line.split()
                        a[k] = self.absolute_to_per_second(k, int(v), c)
                        c[k] = int(v)
            except FileNotFoundError:
                try:
                    # cgroup v1
                    with pathlib.Path(
                        sysfs_prefix,
                        'cpu',
                        'user.slice',
                        'user-{}.slice'.format(uid),
                        'cpuacct.stat'
                    ).open() as f:
                        accounting[user_slice]['cpuacct.stat'] = a = {}
                        if not 'cpuacct.stat' in cache[user_slice]:
                            cache[user_slice]['cpuacct.stat'] = c = {}
                        a['ts'] = time.time()
                        for line in f.readlines():
                            k, v = line.split()
                            a[k] = self.absolute_to_per_second(k, int(v), c)
                            c[k] = int(v)
                except FileNotFoundError:
                    pass

        self.set_agent_cache(cache)
        return accounting


if __name__ == '__main__':
    Plugin().execute()

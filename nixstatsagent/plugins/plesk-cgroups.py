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
        acc = {}
        cache = self.get_agent_cache()
        uid_re = re.compile('\d+')

        # This is silently depending on cgroup mounted virtual file systems
        # and SystemD user slices

        for uslice in (
            glob.glob('/sys/fs/cgroup/user.slice/user-*.slice') +  # cgroup v2
            glob.glob('/sys/fs/cgroup/unified/user.slice/user-*.slice')  # cgroup v1+v2 mixed, e.g. on Focal
        ):

            acc[uslice] = {}
            if not uslice in cache:
                cache[uslice] = {}

            # Resolve uid to username
            acc[uslice]['uid'] = int(uid_re.search(uslice).group())
            try:
                acc[uslice]['username'] = \
                    pwd.getpwuid(acc[uslice]['uid']).pw_name
            except KeyError:
                # There's no guarantee that the uid has a name
                pass

            # This is silently depending
            # on the corresponding CGroup controllers individually enabled

            # Memory accounting
            try:
                # cgroup v2
                # See https://facebookmicrosites.github.io/cgroup2/docs/memory-controller.html
                with pathlib.Path(uslice, 'memory.current').open() as f:
                    acc[uslice]['memory.current'] = int(f.read().strip())
            except FileNotFoundError:
                try:
                    # cgroup v1
                    # See https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/6/html/resource_management_guide/sec-memory
                    with pathlib.Path(
                        uslice,
                        '..',
                        '..',
                        '..',
                        'memory',
                        'user.slice',
                        'user-{}.slice'.format(acc[uslice]['uid']),
                        'memory.usage_in_bytes'
                    ).open() as f:
                        acc[uslice]['memory.current'] = int(f.read().strip())
                except FileNotFoundError:
                    pass

            # IO accounting
            try:
                # cgroup v2
                # See https://facebookmicrosites.github.io/cgroup2/docs/io-controller.html
                with pathlib.Path(uslice, 'io.stat').open() as f:
                    acc[uslice]['io.stat'] = {}
                    if not 'io.stat' in cache[uslice]:
                        cache[uslice]['io.stat'] = {}
                    for line in f.readlines():
                        devnum, kv = line.split()
                        if not devnum in acc[uslice]['io.stat']:
                            acc[uslice]['io.stat'][devnum] = {}
                            acc[uslice]['io.stat'][devnum]['ts'] = time.time()
                        if not devnum in cache[uslice]['io.stat']:
                            cache[uslice]['io.stat'][devnum] = {}
                        k, v = kv.split('=')
                        acc[uslice]['io.stat'][devnum][k] = \
                            self.absolute_to_per_second(
                                k, int(v), cache[uslice]['io.stat'][devnum]
                            )
                        cache[uslice]['io.stat'][devnum][k] = int(v)
            except FileNotFoundError:
                try:
                    # cgroup v1
                    # See https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/6/html/resource_management_guide/ch-subsystems_and_tunable_parameters#sec-blkio
                    with pathlib.Path(
                        uslice,
                        '..',
                        '..',
                        '..',
                        'blkio',
                        'user.slice',
                        'user-{}.slice'.format(acc[uslice]['uid']),
                        'blkio.throttle.io_service_bytes'
                    ).open() as f:
                        acc[uslice]['io.stat'] = {}
                        if not 'io.stat' in cache[uslice]:
                            cache[uslice]['io.stat'] = {}
                        for line in f.readlines():
                            try:
                                devnum, k, v = line.split()
                            except ValueError:
                                # The last line has only 2 values
                                # but can be ignored
                                pass
                            if not devnum in acc[uslice]['io.stat']:
                                acc[uslice]['io.stat'][devnum] = {}
                                acc[uslice]['io.stat'][devnum]['ts'] = time.time()
                            if not devnum in cache[uslice]['io.stat']:
                                cache[uslice]['io.stat'][devnum] = {}
                            acc[uslice]['io.stat'][devnum][k] = \
                                self.absolute_to_per_second(
                                    k, int(v), cache[uslice]['io.stat'][devnum]
                                )
                            cache[uslice]['io.stat'][devnum][k] = int(v)
                except FileNotFoundError:
                    pass

            # CPU accounting
            try:
                with pathlib.Path(uslice, 'cpu.stat').open() as f:
                    acc[uslice]['cpu.stat'] = {}
                    if not 'cpu.stat' in cache[uslice]:
                        cache[uslice]['cpu.stat'] = {}
                    acc[uslice]['cpu.stat']['ts'] = time.time()
                    # See https://facebookmicrosites.github.io/cgroup2/docs/cpu-controller.html
                    for line in f.readlines():
                        k, v = line.split()
                        acc[uslice]['cpu.stat'][k] = \
                            self.absolute_to_per_second(
                                k, int(v), cache[uslice]['cpu.stat']
                            )
                        cache[uslice]['cpu.stat'][k] = int(v)
            except FileNotFoundError:
                pass

        self.set_agent_cache(cache)
        return acc


if __name__ == '__main__':
    Plugin().execute()

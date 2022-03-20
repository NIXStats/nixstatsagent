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

        # This is silently depending on CGroup virtual file system
        # and SystemD user slices

        for uslice in glob.glob('/sys/fs/cgroup/user.slice/user-*.slice'):
            acc[uslice] = {}
            if not uslice in cache:
                cache[uslice] = {}

            acc[uslice]['uid'] = int(uid_re.search(uslice).group())
            try:
                acc[uslice]['username'] = pwd.getpwuid(acc[uslice]['uid'])
            except KeyError:
                # There's no guarantee that the uid has a name
                pass

            # This is silently depending
            # on the corresponding CGroup controllers individually enabled

            try:
                with pathlib.Path(uslice, 'memory.current').open() as f:
                    # See https://facebookmicrosites.github.io/cgroup2/docs/memory-controller.html
                    acc[uslice]['memory.current'] = int(f.read().strip())
            except FileNotFoundError:
                pass

            try:
                with pathlib.Path(uslice, 'io.stat').open() as f:
                    acc[uslice]['io.stat'] = {}
                    if not 'io.stat' in cache[uslice]:
                        cache[uslice]['io.stat'] = {}
                    # See https://facebookmicrosites.github.io/cgroup2/docs/io-controller.html
                    for line in f.readlines():
                        devnum = line.split()[0]
                        acc[uslice]['io.stat'][devnum] = {}
                        if not devnum in cache[uslice]['io.stat']:
                            cache[uslice]['io.stat'][devnum] = {}
                        acc[uslice]['io.stat'][devnum]['ts'] = time.time()
                        for kv in line.split()[1:]:
                            k, v = kv.split('=')
                            acc[uslice]['io.stat'][devnum][k] = \
                                self.absolute_to_per_second(
                                    k, int(v), cache[uslice]['io.stat'][devnum]
                                )
            except FileNotFoundError:
                pass

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
            except FileNotFoundError:
                pass

        return acc


if __name__ == '__main__':
    Plugin().execute()

#!/usr/bin/env python

import psutil
import pickle
import sys


def run():
    memory = {}
    mem = psutil.virtual_memory()
    for name in mem._fields:
        memory[name] = getattr(mem, name)
    return memory


if __name__ == '__main__':
    pickle.dump(run(), sys.stdout)

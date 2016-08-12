#!/usr/bin/env python

import psutil
import pickle
import sys

memory = {}

mem = psutil.virtual_memory()
for name in mem._fields:
    memory[name] = getattr(mem, name)

pickle.dump(memory, sys.stdout)

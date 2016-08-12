#!/usr/bin/env python

import pickle
import sys

import psutil

name = 'cpu'
results = {}
data = psutil.cpu_times_percent(interval=1, percpu=True)
cpu_number = -1
for cpu in data:
	core = {}
	cpu_number = cpu_number+1
	results[cpu_number] = {}
	for key in cpu._fields:
		core[key] = getattr(cpu, key)
	results[cpu_number] = core
pickle.dump(results, sys.stdout)

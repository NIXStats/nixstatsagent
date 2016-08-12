#!/usr/bin/env python

import pickle
import sys
import psutil

pickle.dump(psutil.net_io_counters(pernic=True), sys.stdout)

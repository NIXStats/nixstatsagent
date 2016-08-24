#!/usr/bin/env python

import pickle
import sys
import psutil


def run():
    return psutil.net_io_counters(pernic=True)


if __name__ == '__main__':
    pickle.dump(run(), sys.stdout)


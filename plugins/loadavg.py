#!/usr/bin/env python

import pickle
import sys
import os


def run():
    return os.getloadavg()


if __name__ == '__main__':
    pickle.dump(run(), sys.stdout)

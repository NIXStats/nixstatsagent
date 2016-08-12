#!/usr/bin/env python

import pickle
import sys
import os

pickle.dump(os.getloadavg(), sys.stdout)

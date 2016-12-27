#!/usr/bin/env python

import os
import sys
import urllib
import urllib2


if len(sys.argv) != 2:
    sys.stderr.write('Usage: hello.py <user_id>\n')
    exit(1)

print(urllib2.urlopen('https://api.nixstats.com/hello.php', 
    data=urllib.urlencode({
        'user': sys.argv[1], 
        'hostname': os.uname()[1]}))
    .read())


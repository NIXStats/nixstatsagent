#!/usr/bin/env python

# by Al Nikolov <root@toor.fi.eu.org>

'''
A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
'''

import glob
import os
import setuptools


here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.rst')) as f:
    readme = f.read()

setuptools.setup(
    name='nixstatsagent',
    version='1.0.0',
    description='NixStats agent',
    long_description=readme,
    url='https://github.com/vfuse/nixstatsagent',
    author='NIXStats',
    author_email='vincent@nixstats.com',
    maintainer='Al Nikolov',
    maintainer_email='root@toor.fi.eu.org',
    license='BSD-3-Clause',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: No Input/Output (Daemon)'
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.4',
        'Topic :: System :: Monitoring',
    ],
    keywords='nixstats system monitoring',
    requires=['psutil'],
    packages=setuptools.find_packages(),
    data_files=[('share/doc/nixstatsagent', ['nixstats-example.ini'])],    
)
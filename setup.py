#!/usr/bin/env python
# -*- coding: utf-8 -*-
# by Al Nikolov <root@toor.fi.eu.org>


import os
import sys
import setuptools


here = os.path.abspath(os.path.dirname(__file__))

readme = open(os.path.join(here, 'README.md')).read()
if sys.version.startswith('3.'):
    install_requires = ['psutil', 'netifaces', 'configparser', 'future']
elif sys.version.startswith('2.6'):
    install_requires = ['psutil', 'netifaces', 'configparser==3.5.0', 'future']
else:
    install_requires = ['psutil', 'netifaces', 'configparser', 'future']


setuptools.setup(
    name='nixstatsagent',
    version='1.2.5',
    description='NixStats agent',
    long_description=readme,
    url='https://github.com/NIXStats/nixstatsagent',
    author='NIXStats',
    author_email='vincent@nixstats.com',
    maintainer='Al Nikolov',
    maintainer_email='root@toor.fi.eu.org',
    license='BSD-3-Clause',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: System :: Monitoring',
    ],
    keywords='nixstats system monitoring agent',
    install_requires=install_requires,
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            'nixstatsagent=nixstatsagent.nixstatsagent:main',
            'nixstatshello=nixstatsagent.nixstatsagent:hello',
        ],
    },
    data_files=[('share/doc/nixstatsagent', [
        'nixstats-example.ini',
        'LICENSE',
        'README.md',
    ])],
)

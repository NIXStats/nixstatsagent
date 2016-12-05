#!/usr/bin/env python

# by Al Nikolov <root@toor.fi.eu.org>

import glob
import os
import sys

import setuptools


here = os.path.abspath(os.path.dirname(__file__))

readme = open(os.path.join(here, 'README.rst')).read()
if sys.version.startswith('2.4') or sys.version.startswith('2.5'):
    dependency_links = ['https://pypi.python.org/pypi/psutil/2.1.3']
else:
    dependency_links = []

setuptools.setup(
    name='nixstatsagent',
    version='1.0.2',
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
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.4',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Monitoring',
    ],
    keywords='nixstats system monitoring agent',
    install_requires=['psutil'],
    dependency_links=dependency_links,
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            'nixstatsagent=nixstatsagent.nixstatsagent:run_agent',
        ],
    },
    data_files=[('share/doc/nixstatsagent', [
        'nixstats-example.ini',
        'LICENSE',
        'README.rst',
    ])],    
)

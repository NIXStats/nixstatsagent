#!/usr/bin/env python
# -*- coding: utf-8 -*-
# by Al Nikolov <root@toor.fi.eu.org>


import os
import sys
import setuptools


here = os.path.abspath(os.path.dirname(__file__))

readme = open(os.path.join(here, 'README.md')).read()
if sys.version.startswith('3.'):
    install_requires = ['psutil', 'netifaces', 'configparser', 'future', 'distro']
elif sys.version.startswith('2.7'):
    install_requires = ['psutil', 'netifaces', 'configparser==3.5.0', 'future']
else:
    install_requires = ['psutil', 'netifaces', 'configparser', 'future']


setuptools.setup(
    name='360agent',
    version='1.2.17',
    description='360 agent',
    long_description_content_type='text/markdown',
    long_description=readme,
    url='https://github.com/plesk/360agent',
    author='360',
    author_email='360support@webpros.com',
    maintainer='360',
    maintainer_email='360support@webpros.com',
    license='BSD-3-Clause',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: System :: Monitoring',
    ],
    keywords='360 system monitoring agent',
    install_requires=install_requires,
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            '360sagent=360agent.360agent:main',
            '360hello=360agent.360agent:hello',
        ],
    },
    data_files=[('share/doc/360agent', [
        '360agent-example.ini',
        'LICENSE',
        'README.md',
    ])],
)

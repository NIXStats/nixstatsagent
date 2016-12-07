==============
NixStats Agent
==============

NixStats.com is a web service of monitoring and displaying statistics of your 
server performance.

This software is an OS-agnostic agent compatible with Python >= 2.4. 
It's been optimized to have a small CPU consumption and comes with an 
extendable set of useful plugins.


------------
Installation
------------

Depending on your platform, many installation options are possible. We are listing
them more or less in the order from the most specific (and preferred) to the 
most generic ones.


Debian GNU/Linux
================

The package is submitted and should appear soon in Debian and derivaives.
See: https://ftp-master.debian.org/new/nixstatsagent_1.0.1-1.html

- Ubuntu 16.04 
- Ubuntu 14.04 
- Ubuntu 12.04 
- Debian 8 
- Debian 7 
- Debian 6 


Fedora
======

- CentOS 7
- CentOS 6
- CentOS 5 
- Fedora 25 (low priority)
- Fedora 24 (low priority)
- Fedora 23 (low priority)


Windows 
=======

- Windows 2016 (low priority)
- Windows 2012 (low priority)


Python 2.4 environment
======================

CentOS 5 is an example: it comes with Python 2.4, and if you don't want to 
update it, here are the steps to follow:

.. code:: shell

  yum install python-devel python-setuptools
  easy_install-2.4 nixstatsagent


Python 2.7 environment
======================

As binary packages are published on https://pypi.python.org/pypi, provided that 
you've obtained `pip`, simply do:

.. code:: shell

  pip install nixstatsagent

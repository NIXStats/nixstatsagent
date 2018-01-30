NixStats Agent
==============

NixStats.com is a web service of monitoring and displaying statistics of
your server performance.

This software is an OS-agnostic agent compatible with Python 2.4, 2.5, 2.6 and 2.7.
It's been optimized to have a small CPU consumption and comes with an
extendable set of useful plugins.

[![Build Status](https://travis-ci.org/NIXStats/nixstatsagent.svg?branch=master)](https://travis-ci.org/NIXStats/nixstatsagent)

Installation
------------

Depending on your platform, many installation options are possible. We
are listing them more or less in the order from the most specific (and
preferred) to the most generic ones.

### Debian GNU/Linux

The package is existing in Debian Sid and should appear soon in other releases
and derivaives. If your suite is already supported, simply do:

```
apt-get install nixstatsagent
wget -O /etc/nixstats.ini https://www.nixstats.com/nixstats.ini
service nixstatsagent restart
```

You will be asked for a userid, you can find this on the servers overview page when clicking "add server".

Until then, use our [packagecloud repository](https://packagecloud.io/nixstats/nixstats/install#bash)

Current status:

- [x] Ubuntu 16.04.1 LTS (packagecloud:ubuntu/xenial)
- [x] Ubuntu 14.04.5 LTS (packagecloud:ubuntu/trusty)
- [x] Ubuntu 12.04.5 LTS (packagecloud:ubuntu/precise)
- [x] Debian 8 (packagecloud:debian/jessie)
- [x] Debian 7 (packagecloud:debian/wheezy)
- [ ] Debian 6
- [x] Debian 9 (sid, stretch, packagecloud:debian/stretch)
- [x] Ubuntu 17.04 (zesty)

### Fedora

-   CentOS 7
-   CentOS 6
-   CentOS 5
-   Fedora 25 (low priority)
-   Fedora 24 (low priority)
-   Fedora 23 (low priority)

### Windows

-   Windows 2016 (low priority)
-   Windows 2012 (low priority)

### Python 2.6 or 2.7 environment

As the binary packages are published on [PyPI](https://pypi.python.org/pypi),
provided that you've obtained [pip](https://pip.pypa.io/en/latest/installing/),
simply do:

```
pip install nixstatsagent
```

### Python 2.4 or 2.5 environment

As the source package is published on [PyPI](https://pypi.python.org/pypi),
provided that you've obtained [setuptools](https://pypi.python.org/pypi/setuptools#installation-instructions),
simply do:

```
easy_install nixstatsagent
```



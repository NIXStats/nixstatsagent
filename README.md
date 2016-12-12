NixStats Agent
==============

NixStats.com is a web service of monitoring and displaying statistics of
your server performance.

This software is an OS-agnostic agent compatible with Python \>= 2.4.
It's been optimized to have a small CPU consumption and comes with an
extendable set of useful plugins.

Installation
------------

Depending on your platform, many installation options are possible. We
are listing them more or less in the order from the most specific (and
preferred) to the most generic ones.

### Debian GNU/Linux

The package is existing in Debian Sid and should appear soon in other releases
and derivaives. If your suite is already supported, simply do:

```shell
apt-get install nixstatsagent
```

Until then, use our [packagecloud repository](https://packagecloud.io/btbroot/nixstats/install#bash)

Current status:

-   Ubuntu 16.04
-   Ubuntu 14.04
-   Ubuntu 12.04
-   Debian 8
-   Debian 7
-   Debian 6
-   [x] Debian 9 (sid, packagecloud)

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

```shell
pip install nixstatsagent
```

### Python 2.4 or 2.5 environment

As the source package is published on [PyPI](https://pypi.python.org/pypi),
provided that you've obtained [setuptools](https://pypi.python.org/pypi/setuptools#installation-instructions),
simply do:

```shell
easy_install nixstatsagent
```



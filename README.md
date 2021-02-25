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

Manual installation:
```
apt-get install python3-devel python3-setuptools python3-pip
pip3 install nixstatsagent
wget -O /etc/nixstats.ini https://www.nixstats.com/nixstats.ini
```

You can find your USERTOKEN on the settings page (https://nixstats.com/settings/overview). You need this to generate a serverid.

```
nixstatshello USERTOKEN /etc/nixstats-token.ini
```

Create a service for systemd at `/etc/systemd/system/nixstatsagent.service`
```
[Unit]
Description=Nixstatsagent

[Service]
ExecStart=/usr/local/bin/nixstatsagent
User=nixstats

[Install]
WantedBy=multi-user.target
```
Then run:
```
chmod 644 /etc/systemd/system/nixstatsagent.service
systemctl daemon-reload
systemctl enable nixstatsagent
systemctl start nixstatsagent
```

### Fedora / CentOS

For version 6 or earlier (python 2.6, 2.7):
```
yum install python-devel python-setuptools gcc
easy_install nixstatsagent netifaces psutil
```

For version 7 and later (python 3):
```
yum install python36-devel python36 gcc
```

```
pip3 install nixstatsagent
```

### Windows

Download the [windows installer for nixstatsagent](https://nixstats.com/windows/nixstatsagent-setup.exe). When asked for the usertoken, provide the usertoken that is available on the [settings page](https://nixstats.com/settings) at Nixstats.

### Python 2.4 or 2.5 environment

As the source package is published on [PyPI](https://pypi.python.org/pypi),
provided that you've obtained [setuptools](https://pypi.python.org/pypi/setuptools#installation-instructions),
simply do:

```
easy_install nixstatsagent
```

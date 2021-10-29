Agent360
==============

360 Monitoring is a web service of monitoring and displaying statistics of
your server performance.

This software is an OS-agnostic agent compatible with Python 2.7, 3.5 and 3.6.
It's been optimized to have a small CPU consumption and comes with an
extendable set of useful plugins.

[![Build Status](https://github.com/plesk/agent360/workflows/Agent360-Test-And-Deploy/badge.svg?branch=master)](https://github.com/plesk/agent360/actions/workflows/test-and-deploy.yml)

Installation
------------

Depending on your platform, many installation options are possible. We
are listing them more or less in the order from the most specific (and
preferred) to the most generic ones.

### Debian GNU/Linux

Manual installation:
```
apt-get install python3-devel python3-setuptools python3-pip
pip3 install agent360
wget -O /etc/agent360.ini https://www.monitoring360.io/agent360.ini
```

You can find your USERTOKEN on the settings page (https://www.monitoring360.io/settings/overview). You need this to generate a serverid.

```
agent360hello USERTOKEN /etc/agent360-token.ini
```

Create a service for systemd at `/etc/systemd/system/agent360.service`
```
[Unit]
Description=Agent360

[Service]
ExecStart=/usr/local/bin/agent360
User=agent360

[Install]
WantedBy=multi-user.target
```
Then run:
```
chmod 644 /etc/systemd/system/agent360.service
systemctl daemon-reload
systemctl enable agent360
systemctl start agent360
```

### Fedora / CentOS

For version 6 or earlier (python 2.7):
```
yum install python-devel python-setuptools gcc
easy_install agent360 netifaces psutil
```

For version 7 and later (python 3):
```
yum install python36-devel python36 gcc
```

```
pip3 install agent360
```

### Windows

Download the [windows installer for agent360](https://www.monitoring360.io/windows/agent360-setup.exe).
When asked for the usertoken, provide the usertoken that is available on the [settings page](https://www.monitoring360.io/settings)
at 360 Monitoring.

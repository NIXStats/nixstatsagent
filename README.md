Agent360
==============

360 Monitoring is a web service that monitors and displays statistics of
your server performance.

Agent360 is OS agnostic software compatible with Python 2.7, 3.5, and 3.6.
It's been optimized to have low CPU consumption and comes with an
extendable set of useful plugins.

[![Build Status](https://github.com/plesk/agent360/workflows/Agent360-Test-And-Deploy/badge.svg?branch=master)](https://github.com/plesk/agent360/actions/workflows/test-and-deploy.yml)

Installation
------------

Depending on your platform, many installation options are available. We
are listing them in the following order: from the most preferred and specific to the most general ones.

### Debian GNU/Linux

**Manual installation**

#. Connect to your server via SSH and run the following command:
```
apt-get install python3-devel python3-setuptools python3-pip
pip3 install agent360
wget -O /etc/agent360.ini https://monitoring.platform360.io/agent360.ini
```

#. Find your USERTOKEN. To do so, [go to the servers page](https://monitoring.platform360.io/servers/overview) and then click the "Add server" button. You need this to generate a serverid.

#. Run the following command:

```
agent360 hello USERTOKEN /etc/agent360-token.ini
```

#. Create a systemd service at `/etc/systemd/system/agent360.service` by adding the following settings:

```
[Unit]
Description=Agent360

[Service]
ExecStart=/usr/local/bin/agent360
User=agent360

[Install]
WantedBy=multi-user.target
```

#. Run the following command:

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

Not available yet.

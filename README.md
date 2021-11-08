# Agent360

360 Monitoring is a web service that monitors and displays statistics of
your server performance.

Agent360 is OS agnostic software compatible with Python 2.7, 3.5, and 3.6.
It's been optimized to have low CPU consumption and comes with an
extendable set of useful plugins.

[![Build Status](https://github.com/plesk/agent360/workflows/Agent360-Test-And-Deploy/badge.svg?branch=master)](https://github.com/plesk/agent360/actions/workflows/test-and-deploy.yml)

## Automatic Installation (All Linux Distributions)

**Note:** Agent360 is not yet available on Windows.

You can install the default configuration of Agent360 on all Linux distributions with just one click.

1. Connect to your server via SSH.
2. Find your USERTOKEN. To do so, [go to the servers page](https://monitoring.platform360.io/servers/overview) and then click the "Add server" button. 
3. Run the following command:

   ```
   wget -q -N https://monitoring.platform360.io/agent360.sh && bash agent360.sh USERTOKEN
   ```

## Manual Installation

To customize installation options, install Agent360 manually.

1. Connect to your server via SSH.
2. Run the following command, which differs depending on your server platform: 

   -  Debian GNU/Linux:

      ```
      apt-get install python3-devel python3-setuptools python3-pip
      pip3 install agent360
      wget -O /etc/agent360.ini https://monitoring.platform360.io/agent360.ini
      ```

   -  Fedora/CentOS version 6 or earlier (python 2.7):

      ```
      yum install python-devel python-setuptools gcc
      easy_install agent360 netifaces psutil
      wget -O /etc/agent360.ini https://monitoring.platform360.io/agent360.ini
      ```
   
   
   -  Fedora/CentOS version 7 and later (python 3):

      ```
      yum install python36-devel python36 gcc  
      pip3 install agent360
      wget -O /etc/agent360.ini https://monitoring.platform360.io/agent360.ini
      ```

2. Find your USERTOKEN. To do so, [go to the servers page](https://monitoring.platform360.io/servers/overview) and then click the "Add server" button. 
   You need this to generate a serverid.
3. Run the following command (USERTOKEN is the one you got during the previous step):

   ```
   agent360 hello USERTOKEN /etc/agent360-token.ini
   ```

4. Create a systemd service at `/etc/systemd/system/agent360.service` by adding the following:

   ```
   [Unit]
   Description=Agent360

   [Service]
   ExecStart=/usr/local/bin/agent360
   User=agent360

   [Install]
   WantedBy=multi-user.target
   ```

5. Run the following command:

   ```
   chmod 644 /etc/systemd/system/agent360.service
   systemctl daemon-reload
   systemctl enable agent360
   systemctl start agent360
   ```


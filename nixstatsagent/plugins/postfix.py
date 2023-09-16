#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import plugins

class Plugin(plugins.BasePlugin):
    __name__ = 'postfix'

    def run(self, config):
        '''
        postfix mail queue monitoring. Needs sudo access.
        Add the following section to /etc/nixstats.ini

        [postfix]
        enabled=yes

        Inspiration:
        - https://github.com/NIXStats/nixstatsagent/blob/master/nixstatsagent/plugins/exim.py
        - https://serverfault.com/questions/697670/how-to-monitor-the-postfix-mail-queue-using-monit/1097886#1097886
        - https://serverfault.com/questions/58196/how-do-i-check-the-postfix-queue-size/577766#577766

        '''

        metrics = (
                'maildrop',
                'hold',
                'incoming',
                'active',
                'deferred',
                'bounce',
                'corrupt'                
        )

        data = {}

        for metric in metrics:
          data[metric] = int(os.popen('sudo find /var/spool/postfix/' + metric + ' -type f | wc -l').read())

        return data

if __name__ == '__main__':
    Plugin().execute()

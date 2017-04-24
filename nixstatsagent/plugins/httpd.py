#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib2
import time
import plugins
import re


class Plugin(plugins.BasePlugin):
    __name__ = 'httpd'

    def run(self, config):
        '''
        Apache/httpd status page metrics
        '''

        prev_cache = {}
        next_cache = dict()
        next_cache['ts'] = time.time()
        prev_cache = self.get_agent_cache()  # Get absolute values from previous check

        try:
            data = urllib2.urlopen(config.get('httpd', 'status_page_url')).read()
        except Exception, e:
            return False

        exp = re.compile('^([A-Za-z ]+):\s+(.+)$')
        results = {}
        def parse_score_board(sb):

            ret = []

            ret.append(('IdleWorkers', sb.count('_')))
            ret.append(('ReadingWorkers', sb.count('R')))
            ret.append(('WritingWorkers', sb.count('W')))
            ret.append(('KeepaliveWorkers', sb.count('K')))
            ret.append(('DnsWorkers', sb.count('D')))
            ret.append(('ClosingWorkers', sb.count('C')))
            ret.append(('LoggingWorkers', sb.count('L')))
            ret.append(('FinishingWorkers', sb.count('G')))
            ret.append(('CleanupWorkers', sb.count('I')))

            return ret
        for line in data.split('\n'):
            if line:
                m = exp.match(line)
                if m:
                    k = m.group(1)
                    v = m.group(2)

                    # Ignore the following values
                    if k == 'IdleWorkers' or k == 'Server Built' or k == 'Server Built' \
                            or k == 'CurrentTime' or k == 'RestartTime' or k == 'ServerUptime' \
                            or k == 'CPULoad' or k == 'CPUUser' or k == 'CPUSystem' \
                            or k == 'CPUChildrenUser' or k == 'CPUChildrenSystem' \
                            or k == 'ReqPerSec':
                        continue

                    if k == 'Total Accesses':
                        results['requests_per_second'] = self.absolute_to_per_second(k, int(v), prev_cache)
                        next_cache['Total Accesses'] = int(v)

                    if k == 'Scoreboard':
                        for sb_kv in parse_score_board(v):
                            results[sb_kv[0]] = sb_kv[1]
                    else:
                        results[k] = v
        self.set_agent_cache(next_cache)
        return results

if __name__ == '__main__':
    Plugin().execute()

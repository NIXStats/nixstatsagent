#!/usr/bin/env python
import plugins
import os
import json

DEFAULT_STAT_COMMAND = "/usr/sbin/bitninjacli --stats --minify"

class Plugin(plugins.BasePlugin):
    __name__ = 'bitninja'

    def run(self, config):
        '''
        Collects metrics from the BitNinja Linux Agent.

        For this plugin to work, at least BitNinja version 2.38.8 is required, and
        the following configurations must be applied to it:

        /etc/bitninja/System/config.ini:
        ```ini
        [statistics]
        enableIntegration = 1
        ```

        This will allow agent360 to access the statistics.

        Then after a BitNinja restart, the plugin can be tested by running:
        sudo -u agent360 agent360 test bitninja

        Add to /etc/agent360.ini:
        ```ini
        [bitninja]
        enabled = true
        ```
        '''
        try:
            command = config.get(__name__, "statCommand")
        except:
            command = DEFAULT_STAT_COMMAND

        stream = os.popen("sudo " + command)
        result = stream.readlines()
        firstLine = result[0]
        startIndex = firstLine.find('{')
        if startIndex >= 0:
            return json.loads(firstLine[startIndex::].replace("\n", ""))

        return None

if __name__ == '__main__':
    Plugin().execute()

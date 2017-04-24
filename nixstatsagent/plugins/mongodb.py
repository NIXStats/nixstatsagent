#!/usr/bin/env python

import urllib2
import time
import plugins
from pymongo import MongoClient

class Plugin(plugins.BasePlugin):
    __name__ = 'mongodb'

    def run(self, config):
        """
        Mongodb monitoring
        """

        client = MongoClient(config.get('mongodb', 'connection_string'))

        db = client.admin

        statistics = db.command("serverStatus")
        prev_cache = self.get_agent_cache()  # Get absolute values from previous check

        data = {}
        results = dict()
        data['connections.totalCreated'] = statistics['connections']['totalCreated']

        results['connections.available'] = statistics['connections']['available']
        results['connections.current'] = statistics['connections']['current']

        data['opcounters.command'] = statistics['opcounters']['command']
        data['opcounters.delete'] = statistics['opcounters']['delete']
        data['opcounters.getmore'] = statistics['opcounters']['getmore']
        data['opcounters.insert'] = statistics['opcounters']['insert']
        data['opcounters.query'] = statistics['opcounters']['query']
        data['opcounters.update'] = statistics['opcounters']['update']

        data['opLatencies.commands.latency'] = statistics['opLatencies']['commands']['latency']
        data['opLatencies.commands.ops'] = statistics['opLatencies']['commands']['ops']
        data['opLatencies.reads.latency'] = statistics['opLatencies']['reads']['latency']
        data['opLatencies.reads.ops'] = statistics['opLatencies']['reads']['ops']
        data['opLatencies.writes.latency'] = statistics['opLatencies']['writes']['latency']
        data['opLatencies.writes.ops'] = statistics['opLatencies']['writes']['ops']

        data['asserts.msg'] = statistics['asserts']['msg']
        data['asserts.regular'] = statistics['asserts']['regular']
        data['asserts.rollovers'] = statistics['asserts']['rollovers']
        data['asserts.user'] = statistics['asserts']['user']
        data['asserts.warning'] = statistics['asserts']['warning']
 
        try:
            results['repl']['hosts'] = statistics['repl']['hosts']
            results['repl']['isMaster'] = statistics['repl']['isMaster']
            results['repl']['secondary'] = statistics['repl']['secondary']
            results['repl']['setName'] = statistics['repl']['setName']

            data['opcountersRepl.command'] = statistics['opcountersRepl']['command']
            data['opcountersRepl.delete'] = statistics['opcountersRepl']['delete']
            data['opcountersRepl.getmore'] = statistics['opcountersRepl']['getmore']
            data['opcountersRepl.insert'] = statistics['opcountersRepl']['insert']
            data['opcountersRepl.query'] = statistics['opcountersRepl']['query']
            data['opcountersRepl.update'] = statistics['opcountersRepl']['update']
        except KeyError:
            pass

        for key, val in data.items():
            results[key] = self.absolute_to_per_second(key, val, prev_cache)

        try:
            results['opLatencies.commands'] = results['opLatencies.commands.latency']/results['opLatencies.commands.ops']
            results['opLatencies.writes'] = results['opLatencies.writes.latency']/results['opLatencies.writes.ops']
            results['opLatencies.reads'] = results['opLatencies.reads.latency']/results['opLatencies.reads.ops']
        except:
            pass
            
        next_cache = data
        next_cache['ts'] = time.time()
        self.set_agent_cache(next_cache)
        results['mem'] = statistics['mem']

        return results


if __name__ == '__main__':
    Plugin().execute()

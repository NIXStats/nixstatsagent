#!/usr/bin/env python
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
        results = {}
        # replication status
        try:
            results['isprimary'] = 0 if statistics['repl']['ismaster'] is False else 1
            results['members'] = len(statistics['repl']['hosts'])
        except:
            pass

        # transactions stats, available in v3.6.3 and up
        try:
            data['transactions-retriedCommandsCount'] = statistics['transactions']['retriedCommandsCount']
            data['transactions-retriedStatementsCount'] = statistics['transactions']['retriedStatementsCount']
            data['transactions-transactionsCollectionWriteCount'] = statistics['transactions']['transactionsCollectionWriteCount']
            data['transactions-totalAborted'] = statistics['transactions']['totalAborted']
            data['transactions-totalCommitted'] = statistics['transactions']['totalCommitted']
            data['transactions-totalStarted'] = statistics['transactions']['totalStarted']
            results['transactions-currentActive'] = statistics['transactions']['currentActive']
            results['transactions-currentInactive'] = statistics['transactions']['currentInactive']
            results['transactions-currentOpen'] = statistics['transactions']['currentOpen']
        except:
             pass

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

        data['globalLock.currentQueue.total'] = statistics['globalLock']['currentQueue']['total']
        data['globalLock.currentQueue.readers'] = statistics['globalLock']['currentQueue']['readers']
        data['globalLock.currentQueue.writers'] = statistics['globalLock']['currentQueue']['writers']

        data['globalLock.activeClients.total'] = statistics['globalLock']['activeClients']['total']
        data['globalLock.activeClients.readers'] = statistics['globalLock']['activeClients']['readers']
        data['globalLock.activeClients.writers'] = statistics['globalLock']['activeClients']['writers']

        data['asserts.msg'] = statistics['asserts']['msg']
        data['asserts.regular'] = statistics['asserts']['regular']
        data['asserts.rollovers'] = statistics['asserts']['rollovers']
        data['asserts.user'] = statistics['asserts']['user']
        data['asserts.warning'] = statistics['asserts']['warning']

        #deadlock stats
        try:
                for key, val in statistics['locks'].iteritems():
                        for key2, val2 in val.iteritems():
                                for key3, val3 in val2.iteritems():
                                        data['locks-{}-{}-{}'.format(key.lower(), key2, key3)] = val3
        except:
                pass

        try:
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
        results['mem.resident'] = statistics['mem']['resident']
        results['mem.bits'] = statistics['mem']['bits']
        results['mem.virtual'] = statistics['mem']['virtual']
        results['mem.supported'] = 0 if statistics['mem']['supported'] is False else 1

        return results


if __name__ == '__main__':
    Plugin().execute()

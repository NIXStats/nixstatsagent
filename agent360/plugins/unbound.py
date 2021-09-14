#!/usr/bin/env python
import plugins
import subprocess

# Needs: nixstats ALL=(ALL) NOPASSWD: /usr/sbin/unbound-control


class Plugin(plugins.BasePlugin):

    __name__ = 'unbound'

    floatKeys = [ '.avg', '.median', '.now', '.up', '.elapsed' ]

    rate_metrics = [
        "num.answer.bogus",
        "num.answer.rcode",
        "num.answer.secure",
        "num.cachehits",
        "num.cachemiss",
        "num.dnscrypt.cert",
        "num.dnscrypt.cleartext",
        "num.dnscrypt.crypted",
        "num.dnscrypt.malformed",
        "num.prefetch",
        "num.queries",
        "num.queries_ip_ratelimited",
        "num.query.aggressive",
        "num.query.authzone.down",
        "num.query.authzone.up",
        "num.query.class",
        "num.query.dnscrypt.replay",
        "num.query.dnscrypt.shared_secret.cachemiss",
        "num.query.edns",
        "num.query.flags",
        "num.query.ipv6",
        "num.query.opcode",
        "num.query.ratelimited",
        "num.query.subnet",
        "num.query.subnet_cache",
        "num.query.tcp",
        "num.query.tcpout",
        "num.query.tls",
        "num.query.tls.resume",
        "num.query.type",
        "num.recursivereplies",
        "num.rrset.bogus",
        "num.zero_ttl",
        "requestlist.exceeded",
        "requestlist.overwritten",
        "unwanted.queries",
        "unwanted.replies",
    ]

    gauge_metrics = [
        "dnscrypt_nonce.cache.count",
        "dnscrypt_shared_secret.cache.count",
        "infra.cache.count",
        "key.cache.count",
        "mem.cache.dnscrypt_nonce",
        "mem.cache.dnscrypt_shared_secret",
        "mem.cache.message",
        "mem.cache.rrset",
        "mem.mod.iterator",
        "mem.mod.validator",
        "mem.streamwait",
        "msg.cache.count",
        "recursion.time.avg",
        "recursion.time.median",
        "requestlist.avg",
        "requestlist.current.all",
        "requestlist.current.user",
        "requestlist.max",
        "rrset.cache.count",
        "tcpusage",
        "time.elapsed",
        "time.now",
        "time.up",
    ]

    by_tag_labels = [
        "num.answer.rcode",
        "num.query.aggressive",
        "num.query.class",
        "num.query.edns",
        "num.query.flags",
        "num.query.opcode",
        "num.query.type",
    ]

    def get_stats(self):
        cmd = 'sudo /usr/sbin/unbound-control stats'
        try:
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
        except subprocess.CalledProcessError as e:
            error_msg = 'ERROR CALLING {0}: {1}  {2}'.format(cmd, e, e.output)
            return None

        return output


    def parse_stat(self, stat):

        stats = {t[0]: t[2] for line in stat.splitlines() for t in [line.partition('=')]}
        for key, value in stats.items():
                if key.endswith(tuple(self.floatKeys)):
                        stats[key] = float(value)
                else:
                        stats[key] = int(value)
        return stats

    def run(self, *unused):

        resdata = self.get_stats()
        final = {}

        if resdata is None:
            return False
        else:
            final = self.parse_stat(resdata)

        return final

if __name__ == '__main__':

    Plugin().execute()

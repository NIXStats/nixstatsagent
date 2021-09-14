import plugins
import struct
import time
import memcache

class Plugin(plugins.BasePlugin):
    __name__ = 'memcached'

    def run(self, config):
        '''
        pip install python-memcached
        add to /etc/nixstats.ini
        [memcached]
        enabled=yes
        host=127.0.0.1
        port=11211
        '''
        prev_cache = self.get_agent_cache()  # Get absolute values from previous check
        try:
            socket = config.get('memcached', 'socket')
        except:
            socket = False
        try:
            # Connect
            if socket is False:
                mc = memcache.Client(['%s:%s' % (config.get('memcached', 'host'), config.get('memcached', 'port'))], debug=0)
            else:
                mc = memcache.Client(['unix:/%s' % socket], debug=0)
        except:
            return "Could not connect to memcached"

        non_delta = (
            'accepting_conns',
            'bytes',
            'uptime',
            'total_items',
            'total_connections',
            'time_in_listen_disabled_us',
            'threads',
            'rusage_user',
            'rusage_system',
            'reserved_fds',
            'pointer_size',
            'malloc_fails',
            'lrutail_reflocked',
            'listen_disabled_num',
            'limit_maxbytes',
            'hash_power_level',
            'hash_bytes',
            'curr_items',
            'curr_connections',
            'connection_structures',
            'conn_yields',
            'reclaimed'
        )
        delta_keys = (
            'auth_cmds',
            'auth_errors',
            'bytes_read',
            'bytes_written',
            'touch_misses',
            'touch_hits',
            'incr_misses',
            'incr_hits',
            'cas_misses',
            'cas_badval',
            'incr_hits',
            'get_misses',
            'get_hits',
            'expired_unfetched',
            'evictions',
            'evicted_unfetched',
            'delete_misses',
            'delete_hits',
            'decr_misses',
            'decr_hits',
            'crawler_reclaimed',
            'crawler_items_checked',
            'cmd_touch',
            'cmd_get',
            'cmd_set',
            'cmd_flush',
            'cmd_misses',
            'cmd_badval',
            'cmd_hits'
        )

        results = {}
        data = {}
        try:
            result = mc.get_stats()
            for key, key_value in enumerate(result[0][1]):
                value = result[0][1][key_value]
                key = key_value.lower().strip()
                if key in non_delta:
                    results[key] = float(value)
                elif key in delta_keys:
                    value = float(value)
                    results[key] = self.absolute_to_per_second(key, float(value), prev_cache)
                    data[key] = float(value)
                else:
                    pass
        except:
            return 'Could not fetch memcached stats'

        data['ts'] = time.time()
        self.set_agent_cache(data)
        return results


if __name__ == '__main__':
    Plugin().execute()

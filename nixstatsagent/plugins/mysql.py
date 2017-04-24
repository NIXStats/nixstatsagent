#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import MySQLdb
import plugins

class Plugin(plugins.BasePlugin):
    __name__ = 'mysql'

    def run(self, config):
        '''
        MySQL metrics plugin
        '''

        prev_cache = self.get_agent_cache()  # Get absolute values from previous check
        auth = {}
        try:
            auth['port'] = int(config.get('mysql', 'port'))
        except ValueError:
            auth['port'] = 3306
        db = MySQLdb.connect(host=config.get('mysql', 'host'),
                             port=auth['port'],
                             user=config.get('mysql', 'username'),
                             unix_socket=config.get('mysql', 'socket'),
                             passwd=config.get('mysql', 'password'),
                             db=config.get('mysql', 'database'))
        cursor = db.cursor()
        cursor.execute("SHOW GLOBAL STATUS;")
        query_result = cursor.fetchall()
        non_delta = (
            'max_used_connections',
            'open_files',
            'open_tables',
            'qcache_free_blocks',
            'qcache_free_memory',
            'qcache_total_blocks',
            'slave_open_temp_tables',
            'threads_cached',
            'threads_connected',
            'threads_running',
            'uptime'
        )
        delta_keys = (
            'aborted_clients',
            'aborted_connects',
            'binlog_cache_disk_use',
            'binlog_cache_use',
            'bytes_received',
            'bytes_sent',
            'com_delete',
            'com_delete_multi',
            'com_insert',
            'com_insert_select',
            'com_load',
            'com_replace',
            'com_replace_select',
            'com_select',
            'com_update',
            'com_update_multi',
            'connections',
            'created_tmp_disk_tables',
            'created_tmp_files',
            'created_tmp_tables',
            'key_reads',
            'key_read_requests',
            'key_writes',
            'key_write_requests',
            'max_used_connections',
            'open_files',
            'open_tables',
            'opened_tables',
            'qcache_free_blocks',
            'qcache_free_memory',
            'qcache_hits',
            'qcache_inserts',
            'qcache_lowmem_prunes',
            'qcache_not_cached',
            'qcache_queries_in_cache',
            'qcache_total_blocks',
            'questions',
            'select_full_join',
            'select_full_range_join',
            'select_range',
            'select_range_check',
            'select_scan',
            'slave_open_temp_tables',
            'slave_retried_transactions',
            'slow_launch_threads',
            'slow_queries',
            'sort_range',
            'sort_rows',
            'sort_scan',
            'table_locks_immediate',
            'table_locks_waited',
            'threads_cached',
            'threads_connected',
            'threads_created',
            'threads_running'
        )
        results = {}
        data = {}
        for key, value in query_result:
            key = key.lower()
            if key in non_delta:
                results[key] = value
            elif key in delta_keys:
                results[key] = self.absolute_to_per_second(key, value, prev_cache)
                data[key] = value
            else:
                continue
        db.close()
        data['ts'] = time.time()
        self.set_agent_cache(data)
        return results


if __name__ == '__main__':
    Plugin().execute()
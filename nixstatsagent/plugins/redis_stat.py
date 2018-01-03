#!/usr/bin/env python
# -*- coding: utf-8 -*-
import plugins
import redis

### Uncomment/Comment the Attribute Names to be monitored
METRICS = {
# Server section
    #"redis_version": "redis version",
    #"redis_git_sha1": "redis git sha1",
    #"redis_git_dirty": "redis git dirty", 
    #"redis_build_id": "redis build id", 
    #"redis_mode": "redis mode", 
    #"os": "os",    
    #"arch_bits": "arch bits", 
    #"multiplexing_api": "multiplexing api", 
    #"gcc_version": "gcc version",
    #"process_id": "process id",
    #"run_id": "run id", 
    #"tcp_port": "tcp port",
    "uptime_in_seconds": "uptime", 
    #"uptime_in_days": "uptime in days", 
    #"hz": "hz", 
    #"lru_clock": "lru clock", 
    #"executable": "redis path",
    #"config_file": "config file",

# Clients section
    "connected_clients": "connected clients",
    #"client_longest_output_list": "client longest output list", 
    #"client_biggest_input_buf": "client biggest input buf", 
    #"blocked_clients": "blocked clients", 

# Memory section
    "used_memory": "used memory", 
    #"used_memory_human": "used memory human", 
    #"used_memory_rss": "used memory rss",
    #"used_memory_rss_human": "used memory rss human",
    #"used_memory_peak": "used memory peak", 
    "used_memory_peak_human": "used memory peak human", 
    #"total_system_memory": "total system memory",
    #"total_system_memory_human": "total system memory human",
    #"used_memory_lua": "used memory lua",
    #"used_memory_lua_human": "used memory lua human",
    "maxmemory": "maxmemory",
    #"maxmemory_human": "maxmemory human",
    "maxmemory_policy": "maxmemory policy",
    #"mem_fragmentation_ratio": "mem fragmentation ratio",
    #"mem_allocator": "mem allocator",

# Persistence section     
    #"loading": "loading",
    #"rdb_changes_since_last_save": "rdb changes since last save",
    #"rdb_bgsave_in_progress": "rdb bgsave in progress",
    #"rdb_last_save_time": "rdb last save time",
    #"rdb_last_bgsave_status": "rdb last bgsave status",
    #"rdb_last_bgsave_time_sec": "rdb last bgsave time sec",
    #"rdb_current_bgsave_time_sec": "rdb current bgsave time sec",
    #"aof_enabled": "aof enabled",
    #"aof_rewrite_in_progress": "aof rewrite in progress",
    #"aof_rewrite_scheduled": "aof rewrite scheduled",    
    #"aof_last_rewrite_time_sec": "aof last rewrite time",
    #"aof_current_rewrite_time_sec": "aof current rewrite time",
    #"aof_last_bgrewrite_status": "aof last bgrewrite status",
    #"aof_last_write_status": "aof last write status",
    #"aof_current_size": "aof current size",
    #"aof_base_size": "aof base size",
    #"aof_pending_rewrite": "aof pending rewrite",
    #"aof_buffer_length": "aof buffer length",
    #"aof_rewrite_buffer_length": "aof rewrite buffer length",
    #"aof_pending_bio_fsync": "aof pending bio fsync",
    #"aof_delayed_fsync": "aof delayed fsync",

# Stats section
    #"total_connections_received": "total connections received",
    "total_commands_processed": "total commands processed",
    #"instantaneous_ops_per_sec": "instantaneous ops per sec",
    "total_net_input_bytes": "total net input bytes",
    "total_net_output_bytes": "total net output bytes",
    #"instantaneous_input_kbps": "instantaneous input kbps",
    #"instantaneous_output_kbps": "instantaneous output kbps",
    #"rejected_connections": "rejected connections",
    #"sync_full": "sync full",
    #"sync_partial_ok": "sync partial ok",
    #"sync_partial_err": "sync partial err",
    "expired_keys": "expired keys",
    "evicted_keys": "evicted keys",
    "keyspace_hits": "keyspace hits",
    "keyspace_misses": "keyspace misses",
    #"pubsub_channels": "pubsub channels",
    #"pubsub_patterns": "pubsub patterns",
    #"latest_fork_usec": "latest fork usec",
    #"migrate_cached_sockets": "migrate cached sockets",

# Replication section
    #"role": "role",
    #"connected_slaves": "connected slaves",
    #"master_repl_offset": "master repl offset",
    #"repl_backlog_active": "repl backlog active",
    #"repl_backlog_size": "repl backlog size",
    #"repl_backlog_first_byte_offset": "repl backlog first byte offset",
    #"repl_backlog_histlen": "repl backlog histlen",

# CPU section
    #"used_cpu_sys": "used cpu sys",
    #"used_cpu_user": "used cpu user",
    #"used_cpu_sys_children": "used cpu sys children",
    #"used_cpu_user_children": "used cpu user children",    

# Cluster section
    "cluster_enabled": "cluster enabled"
}

class Plugin(plugins.BasePlugin):
    __name__ = 'redis_stat'

    def run(self, config):
        data = {}
        stats = None
        try:
            redis_host = (config.get(__name__, 'host'))
        except:
            redis_host = '127.0.0.1'
        try:
            redis_port = (config.get(__name__, 'port'))
        except:
            redis_port = '6379'
        try:
            redis_db = (config.get(__name__, 'db'))
        except:
            redis_db = '0'
        try:
            redis_password = (config.get(__name__, 'password'))
        except:
            redis_password = ''

        try:
            redis_connection = redis.StrictRedis(host=redis_host,port=redis_port,db=redis_db,password=redis_password)
            stats = redis_connection.info()
        except Exception as e:
            data['status']=0
            data['msg']='Connection Error'
            if not stats:
                return data

        for name, value in stats.iteritems():
            if name in METRICS.keys() :
                data[METRICS[name]] = value
        return data

if __name__ == '__main__':
    Plugin().execute()
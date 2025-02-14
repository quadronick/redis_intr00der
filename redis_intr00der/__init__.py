from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import re
import socket


def encode_resp(command, *args):
    parts = [command.encode("utf-8")] + [arg.encode("utf-8") for arg in args]
    resp = f"*{len(parts)}\r\n" + "".join(
        f"${len(part)}\r\n{part.decode('utf-8')}\r\n" for part in parts
    )
    return resp


def send_redis_command(host, port, password=None, command="INFO", *args):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((host, port))
            if password:
                auth_command = encode_resp("AUTH", password)
                sock.sendall(auth_command.encode("utf-8"))
                response = sock.recv(1024).decode("utf-8")
                if "OK" not in response:
                    print("AUTH ERROR", response.strip())
                    return None
            redis_command = encode_resp(command, *args)
            sock.sendall(redis_command.encode("utf-8"))
            response = b""
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response += chunk
                if response.endswith(b"\r\n"):
                    break
            return response.decode("utf-8").strip()
    except ConnectionRefusedError:
        print("FAILED: Failed to retrieve data from Redis. Check IP and port!")
        return None
    except Exception as e:
        print(f"Exception happened: {e}")
        return None


def process_redis_info(info_data):
    replacements = {
        r"acl_access_denied_auth": "acl_access_denied_auth_total",
        r"acl_access_denied_channel": "acl_access_denied_channel_total",
        r"acl_access_denied_cmd": "acl_access_denied_cmd_total",
        r"acl_access_denied_key": "acl_access_denied_key_total",
        r"active_defrag_hits": "defrag_hits",
        r"active_defrag_key_hits": "defrag_key_hits",
        r"active_defrag_key_misses": "defrag_key_misses",
        r"active_defrag_misses": "defrag_misses",
        r"allocator_active": "allocator_active_bytes",
        r"allocator_allocated": "allocator_allocated_bytes",
        r"allocator_frag_bytes": "allocator_frag_bytes",
        r"allocator_resident": "allocator_resident_bytes",
        r"allocator_rss_bytes": "allocator_rss_bytes",
        r"aof_base_size": "aof_base_size_bytes",
        r"aof_current_rewrite_time_sec": "aof_current_rewrite_duration_sec",
        r"aof_current_size": "aof_current_size_bytes",
        r"aof_last_cow_size": "aof_last_cow_size_bytes",
        r"aof_last_rewrite_time_sec": "aof_last_rewrite_duration_sec",
        r"aof_rewrite_buffer_length": "aof_rewrite_buffer_length",
        r"cached_keys": "cached_keys_total",
        r"client_output_buffer_limit_disconnections": "client_output_buffer_limit_disconnections_total",
        r"client_query_buffer_limit_disconnections": "client_query_buffer_limit_disconnections_total",
        r"client_recent_max_input_buffer": "client_recent_max_input_buffer_bytes",
        r"client_recent_max_output_buffer": "client_recent_max_output_buffer_bytes",
        r"cluster_stats_messages_received": "cluster_messages_received_total",
        r"cluster_stats_messages_sent": "cluster_messages_sent_total",
        r"current_eviction_exceeded_time": "current_eviction_exceeded_time_ms",
        r"dump_payload_sanitizations": "dump_payload_sanitizations",
        r"evicted_clients": "evicted_clients_total",
        r"evicted_keys": "evicted_keys_total",
        r"evicted_scripts": "evicted_scripts_total",
        r"expire_cycle_cpu_milliseconds": "expire_cycle_cpu_time_ms_total",
        r"expired_keys": "expired_keys_total",
        r"expired_subkeys": "expired_subkeys_total",
        r"expired_time_cap_reached_count": "expired_time_cap_reached_total",
        r"io_threaded_reads_processed": "io_threaded_reads_processed",
        r"io_threaded_writes_processed": "io_threaded_writes_processed",
        r"keyspace_hits": "keyspace_hits_total",
        r"keyspace_misses": "keyspace_misses_total",
        r"loading": "loading_dump_file",
        r"long_lock_waits": "long_lock_waits_total",
        r"maxclients": "max_clients",
        r"maxfragmentationmemory_desired_reservation": "memory_max_fragmentation_reservation_desired_bytes",
        r"maxfragmentationmemory_reservation": "memory_max_fragmentation_reservation_bytes",
        r"maxmemory": "memory_max_bytes",
        r"maxmemory_desired_reservation": "memory_max_reservation_desired_bytes",
        r"maxmemory_reservation": "memory_max_reservation_bytes",
        r"mem_not_counted_for_evict": "mem_not_counted_for_eviction_bytes",
        r"mem_overhead_db_hashtable_rehashing": "mem_overhead_db_hashtable_rehashing_bytes",
        r"mem_total_replication_buffers": "mem_total_replication_buffers_bytes",
        r"migrate_cached_sockets": "migrate_cached_sockets_total",
        r"rdb_current_bgsave_time_sec": "rdb_current_bgsave_duration_sec",
        r"rdb_last_bgsave_time_sec": "rdb_last_bgsave_duration_sec",
        r"rdb_last_cow_size": "rdb_last_cow_size_bytes",
        r"rdb_last_load_keys_expired": "rdb_last_load_expired_keys",
        r"rdb_last_load_keys_loaded": "rdb_last_load_loaded_keys",
        r"rdb_last_save_time": "rdb_last_save_timestamp_seconds",
        r"rdb_saves": "rdb_saves_total",
        r"rejected_connections": "rejected_connections_total",
        r"reply_buffer_expands": "reply_buffer_expands_total",
        r"reply_buffer_shrinks": "reply_buffer_shrinks_total",
        r"search_bytes_collected": "search_collected_bytes",
        r"search_total_cycles": "search_cycles_total",
        r"search_total_indexing_time": "search_indexing_time_ms_total",
        r"search_total_ms_run": "search_run_ms_total",
        r"search_used_memory_indexes": "search_used_memory_indexes_bytes",
        r"server_threads": "server_threads_total",
        r"storage_provider_read_hits": "storage_provider_read_hits",
        r"storage_provider_read_misses": "storage_provider_read_misses",
        r"sync_full": "replica_resyncs_full",
        r"sync_partial_err": "replica_partial_resync_denied",
        r"sync_partial_ok": "replica_partial_resync_accepted",
        r"tile38_alloc_bytes": "tile38_mem_alloc_bytes",
        r"tile38_aof_size": "tile38_aof_size_bytes",
        r"tile38_avg_point_size": "tile38_avg_item_size_bytes",
        r"tile38_go_goroutines": "tile38_go_goroutines_total",
        r"tile38_go_threads": "tile38_threads_total",
        r"tile38_heap_alloc_bytes": "tile38_heap_size_bytes",
        r"tile38_heap_released_bytes": "tile38_heap_released_bytes",
        r"tile38_in_memory_size": "tile38_in_memory_size_bytes",
        r"tile38_max_heap_size": "tile38_max_heap_size_bytes",
        r"tile38_num_collections": "tile38_num_collections_total",
        r"tile38_num_hooks": "tile38_num_hooks_total",
        r"tile38_num_objects": "tile38_num_objects_total",
        r"tile38_num_points": "tile38_num_points_total",
        r"tile38_pointer_size": "tile38_pointer_size_bytes",
        r"tile38_sys_cpus": "tile38_cpus_total",
        r"total_commands_processed": "commands_processed_total",
        r"total_connections_received": "connections_received_total",
        r"total_error_replies": "total_error_replies",
        r"total_eviction_exceeded_time": "eviction_exceeded_time_ms_total",
        r"total_net_input_bytes": "net_input_bytes_total",
        r"total_net_output_bytes": "net_output_bytes_total",
        r"total_net_repl_input_bytes": "net_repl_input_bytes_total",
        r"total_net_repl_output_bytes": "net_repl_output_bytes_total",
        r"total_reads_processed": "total_reads_processed",
        r"total_writes_processed": "total_writes_processed",
        r"unexpected_error_replies": "unexpected_error_replies",
        r"used_cpu_sys": "cpu_sys_seconds_total",
        r"used_cpu_sys_children": "cpu_sys_children_seconds_total",
        r"used_cpu_sys_main_thread": "cpu_sys_main_thread_seconds_total",
        r"used_cpu_user": "cpu_user_seconds_total",
        r"used_cpu_user_children": "cpu_user_children_seconds_total",
        r"used_cpu_user_main_thread": "cpu_user_main_thread_seconds_total",
        r"used_memory": "memory_used_bytes",
        r"used_memory_dataset": "memory_used_dataset_bytes",
        r"used_memory_functions": "memory_used_functions_bytes",
        r"used_memory_lua": "memory_used_lua_bytes",
        r"used_memory_overhead": "memory_used_overhead_bytes",
        r"used_memory_peak": "memory_used_peak_bytes",
        r"used_memory_rss": "memory_used_rss_bytes",
        r"used_memory_scripts": "memory_used_scripts_bytes",
        r"used_memory_scripts_eval": "memory_used_scripts_eval_bytes",
        r"used_memory_startup": "memory_used_startup_bytes",
        r"used_memory_vm_eval": "memory_used_vm_eval_bytes",
        r"used_memory_vm_functions": "memory_used_vm_functions_bytes",
        r"used_memory_vm_total": "memory_used_vm_total",
    }

    for old_key, new_key in replacements.items():
        info_data = re.sub(
            rf"^{old_key}:", f"{new_key}:", info_data, flags=re.MULTILINE
        )

    return info_data


class RedisInfoHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        host = RemoteRedisHost
        port = RemoteRedisPort
        password = RemoteRedisHostPassword

        result = send_redis_command(host, port, password, "INFO", "ALL")

        if result is not None:
            processed_result = process_redis_info(result)

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            html_content = f"""
            <html>
                <head>
                    <title>Redis INFO ALL</title>
                </head>
                <body>
                    <pre>{processed_result}</pre>
                </body>
            </html>
            """
            self.wfile.write(html_content.encode("utf-8"))
        else:
            self.send_response(500)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            html_content = """
            <html>
                <head>
                    <title>Shit!</title>
                </head>
                <body>
                    <h1>Error retrieving data from Redis</h1>
                    <p>Failed to retrieve data. Check your Redis connection settings!</p>
                </body>
            </html>
            """
            self.wfile.write(html_content.encode("utf-8"))


def run_http_server(server_address=("0.0.0.0", 6339)):
    print("""
        R E D I S   I N T R U D E R
        "Find metrics in the Chaos"

       ||| .--.
      FUCK!
     |o_o |
     |:_/ |
    //   \\ \\
   (|     | )
  / \\_   _/ \\
  \\___)=(___/ """, flush=True)
    httpd = HTTPServer(server_address, RedisInfoHandler)
    print(f"Exporting at ://{server_address[0]}:{server_address[1]}/", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nHTTP-server shutted down.", flush=True)
    finally:
        httpd.server_close()


if __name__ == "__main__":
    try:
        RemoteRedisHost = os.environ["REDIS_INTR00DER_TARGET_HOST"]
        RemoteRedisPort = int(os.environ["REDIS_INTR00DER_TARGET_HOST_PORT"])
        RemoteRedisHostPassword = os.environ["REDIS_INTR00DER_TARGET_HOST_PASSWORD"] if (os.environ["REDIS_INTR00DER_TARGET_HOST_PASSWORD"] != "") else None
        run_http_server()
    except KeyError as e:
        print(f"ALARM: MIISSED ENV VARIABLE DETECTED: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"ALARM: INCORRECT ENV VARIABLE VALUE DETECTED: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ALARM! WTF?!: {e}", file=sys.stderr)
        sys.exit(1)

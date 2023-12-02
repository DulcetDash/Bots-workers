import redis

def delete_redis_keys_by_suffix(r, suffix):
    """
    Connect to a remote Redis server and delete all keys that end with a specified suffix.

    :param host: The host of the Redis server.
    :param port: The port of the Redis server.
    :param password: The password for the Redis server (if required).
    :param suffix: The suffix of the keys to be deleted.
    """
    try:
        # Find all keys that end with the specified suffix
        keys_to_delete = r.keys(f'*{suffix}')

        if keys_to_delete:
            # Delete all found keys
            r.delete(*keys_to_delete)
            print(f"Deleted {len(keys_to_delete)} keys with suffix '{suffix}'.")
        else:
            print(f"No keys found with suffix '{suffix}'.")
    except Exception as e:
        print(f"Error: {e}")

def delete_redis_key(key, suffix='-searchedProduct'):
    """
    Connect to a remote Redis server and delete a specified key.

    :param host: The host of the Redis server.
    :param port: The port of the Redis server.
    :param password: The password for the Redis server (if required).
    :param key: The key to delete from Redis.
    """
    host = '18.204.117.172'
    port = 6379

    try:
        # Connect to Redis
        r = redis.Redis(host=host, port=port, decode_responses=True)

        # Delete the key
        result = r.delete(key)

        if result == 1:
            print(f"Key '{key}' deleted successfully.")
        else:
            print(f"Key '{key}' not found.")

        if suffix:
            delete_redis_keys_by_suffix(r, suffix)
    except Exception as e:
        print(f"Error: {e}")
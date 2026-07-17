import os

# Set OpenBLAS to use 1 thread to avoid memory / thread allocation errors
os.environ["OPENBLAS_NUM_THREADS"] = "1"

# Monkey patch redis-py to force RESP2 protocol for compatibility
# Catch all exceptions so a version mismatch never crashes the app on startup
try:
    import redis.connection
    if hasattr(redis.connection, 'MaintNotificationsAbstractConnection'):
        redis.connection.MaintNotificationsAbstractConnection._configure_maintenance_notifications = lambda *args, **kwargs: None
    if hasattr(redis.connection, 'DEFAULT_RESP_VERSION'):
        redis.connection.DEFAULT_RESP_VERSION = 2
except Exception:
    pass

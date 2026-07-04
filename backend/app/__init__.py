import os

# Set OpenBLAS to use 1 thread to avoid Windows virtual memory / thread allocation errors
os.environ["OPENBLAS_NUM_THREADS"] = "1"

# Monkey patch redis-py to force RESP2 protocol for compatibility with older Redis servers (like Redis 3.0 on Windows)
try:
    import redis.connection
    redis.connection.MaintNotificationsAbstractConnection._configure_maintenance_notifications = lambda *args, **kwargs: None
    redis.connection.DEFAULT_RESP_VERSION = 2
except ImportError:
    pass

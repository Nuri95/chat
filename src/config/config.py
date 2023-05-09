from contextlib import contextmanager

from psycopg2.pool import ThreadedConnectionPool

POSTGRES_SERVER: str = "192.168.64.2"
POSTGRES_USER: str = "app"
POSTGRES_PASSWORD: str = "pass"
POSTGRES_DB: str = "chat"


pool = ThreadedConnectionPool(
    host=POSTGRES_SERVER,
    database=POSTGRES_DB,
    user=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
    connect_timeout=2,
    minconn=1,
    maxconn=10,
)


@contextmanager
def get_connection():
    conn, cursor = None, None

    try:
        conn = pool.getconn()
        cursor = conn.cursor()
        yield cursor
        conn.commit()
    finally:
        cursor.close()
        pool.putconn(conn)

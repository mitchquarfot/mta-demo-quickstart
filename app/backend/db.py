import os
import snowflake.connector
from contextlib import contextmanager


def _get_token():
    token_path = "/snowflake/session/token"
    if os.path.exists(token_path):
        with open(token_path) as f:
            return f.read().strip()
    return None


def get_connection():
    token = _get_token()
    if token:
        host = os.getenv("SNOWFLAKE_HOST")
        account = os.getenv("SNOWFLAKE_ACCOUNT") or (host.split(".")[0] if host else None)
        return snowflake.connector.connect(
            host=host,
            account=account,
            authenticator="oauth",
            token=token,
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE", "MTA_WH"),
            database="MTA_DEMO",
            schema="ANALYTICS",
        )
    conn_name = os.getenv("SNOWFLAKE_CONNECTION_NAME", "my_connection")
    return snowflake.connector.connect(
        connection_name=conn_name,
        database="MTA_DEMO",
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE", "MTA_WH"),
    )


@contextmanager
def snowflake_cursor():
    conn = get_connection()
    try:
        cur = conn.cursor()
        yield cur
    finally:
        conn.close()


def query_to_dicts(sql: str, params: dict | None = None) -> list[dict]:
    with snowflake_cursor() as cur:
        cur.execute(sql, params or {})
        cols = [d[0] for d in cur.description]
        rows = cur.fetchall()
        return [dict(zip(cols, row)) for row in rows]

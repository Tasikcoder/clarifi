import snowflake.connector
from config import get_snowflake_config
from contextlib import contextmanager
from typing import Any


@contextmanager
def get_connection():
    conn = snowflake.connector.connect(**get_snowflake_config())
    try:
        yield conn
    finally:
        conn.close()


def execute_query(sql: str, params: tuple = None) -> list[dict[str, Any]]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(sql, params)
        columns = [desc[0] for desc in cur.description] if cur.description else []
        rows = cur.fetchall()
        return [dict(zip(columns, row)) for row in rows]


def execute_procedure(sql: str, params: tuple = None) -> str:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(sql, params)
        result = cur.fetchone()
        return result[0] if result else None


def upload_file_to_stage(local_path: str, stage_path: str):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(f"PUT 'file://{local_path}' '{stage_path}' AUTO_COMPRESS=FALSE OVERWRITE=TRUE")
        return cur.fetchall()

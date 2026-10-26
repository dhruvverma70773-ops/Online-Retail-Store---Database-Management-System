"""Small MySQL connection helper used by the Streamlit application."""

import os
from contextlib import contextmanager
from typing import Any, Iterator

import mysql.connector
from mysql.connector import Error


def connection_config() -> dict[str, Any]:
    """Read connection settings from environment variables."""
    return {
        "host": os.getenv("RETAIL_DB_HOST", "127.0.0.1"),
        "port": int(os.getenv("RETAIL_DB_PORT", "3306")),
        "database": os.getenv("RETAIL_DB_NAME", "retail_store"),
        "user": os.getenv("RETAIL_DB_USER", "retail_app"),
        "password": os.getenv("RETAIL_DB_PASSWORD", "retail_app_password"),
    }


@contextmanager
def get_connection() -> Iterator[Any]:
    """Yield a connection and close it reliably after use."""
    connection = None
    try:
        connection = mysql.connector.connect(**connection_config())
        yield connection
    except Error:
        raise
    finally:
        if connection is not None and connection.is_connected():
            connection.close()


def query_df(sql: str, params: tuple[Any, ...] = ()):
    """Execute a read-only query and return a pandas DataFrame."""
    import pandas as pd

    with get_connection() as connection:
        cursor = connection.cursor()
        try:
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description or ()]
            return pd.DataFrame(rows, columns=columns)
        finally:
            cursor.close()


def execute(sql: str, params: tuple[Any, ...] = ()) -> int:
    """Execute one write statement and return its generated id if available."""
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(sql, params)
        connection.commit()
        return cursor.lastrowid or cursor.rowcount

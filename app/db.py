"""Oracle connection helpers — same DB account as project root dataload.py."""

from __future__ import annotations

import os
import threading

import oracledb

# DB Creds.
username = "JNGUYEN7496_SCHEMA_1FOBA"
password = "GHDE1ABLXQYB7GYJhGGG0QJ4ZZ$MAY"
dsn = "db.freesql.com:1521/23ai_34ui2"

# Class DB requires python-oracledb "thick" mode.
# The Oracle Instant Client folder is per-machine, so it is read from an env var.
# Set ORACLE_LIB_DIR to the folder that contains the client libraries; if it is
# not set, the driver tries to find the client on PATH / LD_LIBRARY_PATH.
_ORACLE_LIB_DIR_ENV = "ORACLE_LIB_DIR"

_client_initialized = False
_conn = None
# One connection for the whole app; lock because the GUI runs queries on a worker thread.
_db_lock = threading.RLock()


def _ensure_thick_mode() -> None:
    global _client_initialized
    if _client_initialized:
        return
    lib_dir = os.environ.get(_ORACLE_LIB_DIR_ENV, "").strip() or None
    if lib_dir:
        oracledb.init_oracle_client(lib_dir=lib_dir)
    else:
        oracledb.init_oracle_client()
    _client_initialized = True


def get_connection():
    """Return the shared connection, opening it on first use (thick mode)."""
    global _conn
    with _db_lock:
        _ensure_thick_mode()
        if _conn is None:
            _conn = oracledb.connect(user=username, password=password, dsn=dsn)
        return _conn


def execute_query(sql: str, params: dict | None = None):
    """Run a SELECT; return (column_names, rows). Uses shared connection; closes only the cursor."""
    with _db_lock:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(sql, params or {})
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            return columns, rows
        finally:
            cursor.close()


def fetch_single_column(sql: str, params: dict | None = None) -> list:
    """Run a SELECT expected to return one column; return a flat list of values."""
    _, rows = execute_query(sql, params)
    return [r[0] for r in rows if r and r[0] is not None]


def close_connection() -> None:
    """Close the shared connection (call when the app exits)."""
    global _conn
    with _db_lock:
        if _conn is not None:
            try:
                _conn.close()
            finally:
                _conn = None

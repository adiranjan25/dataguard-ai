from __future__ import annotations

import re

import pandas as pd

_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_$.]*$")

def _safe_ident(name: str) -> str:
    if not _IDENT.fullmatch(name):
        raise ValueError("Unsafe table identifier. Use letters, numbers, _, $, and dots only.")
    return name

def load_duckdb(database: str, table: str, limit: int | None = None) -> pd.DataFrame:
    try:
        import duckdb
    except ImportError as e:
        raise RuntimeError('DuckDB support requires: pip install "dataguard-ai[duckdb]"') from e
    table = _safe_ident(table)
    sql = f"SELECT * FROM {table}" + (f" LIMIT {int(limit)}" if limit else "")
    con = duckdb.connect(database=database, read_only=True)
    try:
        return con.execute(sql).fetchdf()
    finally:
        con.close()

def load_postgres(url: str, table: str, limit: int | None = None) -> pd.DataFrame:
    try:
        from sqlalchemy import create_engine, text
    except ImportError as e:
        raise RuntimeError('PostgreSQL support requires: pip install "dataguard-ai[postgres]"') from e
    table = _safe_ident(table)
    sql = f"SELECT * FROM {table}" + (f" LIMIT {int(limit)}" if limit else "")
    engine = create_engine(url)
    try:
        with engine.connect() as conn:
            return pd.read_sql(text(sql), conn)
    finally:
        engine.dispose()

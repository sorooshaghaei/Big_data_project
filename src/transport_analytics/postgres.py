"""PostgreSQL loading utilities."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import PostgresConfig


def _load_sqlalchemy():
    """Import SQLAlchemy lazily.

    Lazy imports keep the rest of the package usable even when
    PostgreSQL dependencies are not installed.
    """
    try:
        from sqlalchemy import create_engine, text
    except Exception as exc:  # pragma: no cover
        raise ImportError(
            "SQLAlchemy + psycopg are required for PostgreSQL loading. "
            "Install with: pip install sqlalchemy psycopg[binary]"
        ) from exc
    return create_engine, text


def execute_sql_file(sql_path: Path, pg: PostgresConfig) -> None:
    """Execute a SQL script file against PostgreSQL."""
    create_engine, text = _load_sqlalchemy()
    sql = sql_path.read_text(encoding="utf-8")
    engine = create_engine(pg.sqlalchemy_url)

    # Use a transaction block so schema/view updates are atomic.
    with engine.begin() as conn:
        conn.execute(text(sql))


def write_fact_table(
    df: pd.DataFrame,
    table_name: str,
    pg: PostgresConfig,
    if_exists: str = "append",
) -> None:
    """Write a pandas DataFrame into PostgreSQL."""
    create_engine, _ = _load_sqlalchemy()
    engine = create_engine(pg.sqlalchemy_url)

    # `method="multi"` batches inserts for better throughput.
    df.to_sql(table_name, engine, schema=pg.schema, if_exists=if_exists, index=False, method="multi")

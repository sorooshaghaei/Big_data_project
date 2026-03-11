# Mehdi AGHAEI
"""PostgreSQL loading utilities."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import PostgresConfig
from .pipeline import PipelineArtifacts


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

    with engine.begin() as conn:
        conn.execute(text(sql))


def write_dataframe(
    df: pd.DataFrame,
    table_name: str,
    pg: PostgresConfig,
    if_exists: str = "append",
) -> None:
    """Write a pandas DataFrame into PostgreSQL."""
    create_engine, _ = _load_sqlalchemy()
    engine = create_engine(pg.sqlalchemy_url)
    df.to_sql(table_name, engine, schema=pg.schema, if_exists=if_exists, index=False, method="multi")


def write_fact_table(
    df: pd.DataFrame,
    table_name: str,
    pg: PostgresConfig,
    if_exists: str = "append",
) -> None:
    """Backward-compatible alias for writing one table."""
    write_dataframe(df=df, table_name=table_name, pg=pg, if_exists=if_exists)


def write_pipeline_outputs(artifacts: PipelineArtifacts, pg: PostgresConfig, replace: bool = True) -> None:
    """Load the cleaned pipeline outputs into PostgreSQL tables."""
    mode = "replace" if replace else "append"
    write_dataframe(artifacts.station_fact.rename(columns={"date": "demand_date"}), "fact_demand", pg, if_exists=mode)
    write_dataframe(
        artifacts.calendar.rename(columns={"date": "calendar_date"})[
            ["calendar_date", "year", "month", "day_of_week", "is_weekend", "is_holiday", "holiday_name"]
        ],
        "dim_calendar",
        pg,
        if_exists=mode,
    )
    write_dataframe(
        artifacts.weather.rename(columns={"date": "weather_date", "weather_source": "source"}),
        "dim_weather",
        pg,
        if_exists=mode,
    )

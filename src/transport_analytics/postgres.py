# Mehdi AGHAEI
"""PostgreSQL utilities for the Stage 1 DB-backed workflow."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import PostgresConfig
from .features import add_time_features
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


def read_sql_query(
    query: str,
    pg: PostgresConfig,
    *,
    parse_dates: list[str] | None = None,
) -> pd.DataFrame:
    """Read a SQL query result into a pandas DataFrame."""
    create_engine, text = _load_sqlalchemy()
    engine = create_engine(pg.sqlalchemy_url)

    with engine.begin() as conn:
        return pd.read_sql_query(text(query), conn, parse_dates=parse_dates)


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


def load_postgres_artifacts(pg: PostgresConfig) -> PipelineArtifacts:
    """Load Stage 1 analysis artifacts directly from PostgreSQL views."""
    station_fact = read_sql_query(
        """
        SELECT
            demand_date AS date,
            region,
            location_id,
            location_name,
            metric_type,
            value,
            source
        FROM transport.fact_demand
        ORDER BY demand_date, city, region, source, location_name
        """,
        pg,
        parse_dates=["date"],
    )

    daily = read_sql_query(
        """
        SELECT
            demand_date AS date,
            region,
            source,
            metric_type,
            total_value AS value
        FROM transport.v_daily_demand
        ORDER BY demand_date, city, region, source, metric_type
        """,
        pg,
        parse_dates=["date"],
    )

    featured = add_time_features(daily)
    enriched = featured.copy()

    nyc_hourly = read_sql_query(
        """
        SELECT
            region,
            hour,
            hour_label,
            hourly_total AS value
        FROM transport.v_nyc_hourly_profile
        ORDER BY region, hour
        """,
        pg,
    )

    paris_hourly = read_sql_query(
        """
        SELECT
            day_category,
            hour_bin,
            validation_share_pct
        FROM transport.v_paris_hourly_profile
        ORDER BY day_category, hour_bin
        """,
        pg,
    )

    return PipelineArtifacts(
        station_fact=station_fact,
        daily=daily,
        featured=featured,
        enriched=enriched,
        calendar=pd.DataFrame(),
        weather=pd.DataFrame(),
        mta_hourly_profile=nyc_hourly,
        paris_hourly_profile=paris_hourly,
        weather_source="not_used_stage1",
    )

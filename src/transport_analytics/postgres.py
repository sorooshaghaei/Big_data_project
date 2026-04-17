#Mehdi AGHAEI

from __future__ import annotations

from pathlib import Path
from typing import Callable

import pandas as pd

from .config import PostgresConfig
from .features import add_time_features
from .pipeline import PipelineArtifacts

# opens sqlalchemy only when postgres is needed
def _load_sqlalchemy():
    try:
        from sqlalchemy import create_engine, text
    except Exception as exc:
        raise ImportError(
            "SQLAlchemy + psycopg are required for PostgreSQL loading. "
            "Install with: pip install sqlalchemy psycopg[binary]"
        ) from exc
    return create_engine, text

# sends a whole sql file to postgres
def execute_sql_file(sql_path: Path, pg: PostgresConfig) -> None:
    create_engine, _ = _load_sqlalchemy()
    sql = sql_path.read_text(encoding="utf-8")
    engine = create_engine(pg.sqlalchemy_url)

    with engine.begin() as conn:

        conn.exec_driver_sql("SET lock_timeout = '10s'")

        conn.exec_driver_sql(sql)

# brings a query result back as a dataframe
def read_sql_query(
    query: str,
    pg: PostgresConfig,
    *,
    parse_dates: list[str] | None = None,
) -> pd.DataFrame:
    create_engine, text = _load_sqlalchemy()
    engine = create_engine(pg.sqlalchemy_url)

    with engine.begin() as conn:
        return pd.read_sql_query(text(query), conn, parse_dates=parse_dates)

# forwards progress text when needed
def _emit_progress(progress: Callable[[str], None] | None, message: str) -> None:
    if progress is not None:
        progress(message)

# pulls the stage tables from postgres
def load_postgres_artifacts(
    pg: PostgresConfig,
    *,
    progress: Callable[[str], None] | None = None,
) -> PipelineArtifacts:
    _emit_progress(progress, "Loading daily demand view from PostgreSQL")
    daily = read_sql_query(
        """
        SELECT
            demand_date AS date,
            region,
            source,
            metric_type,
            total_value AS value
        FROM transport.v_daily_demand
        """,
        pg,
        parse_dates=["date"],
    )
    _emit_progress(progress, f"Loaded daily rows: {len(daily)}")

    _emit_progress(progress, "Building time-series features")
    featured = add_time_features(daily)
    _emit_progress(progress, f"Built featured rows: {len(featured)}")
    enriched = featured.copy()

    _emit_progress(progress, "Loading NYC hourly profile from PostgreSQL")
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
    _emit_progress(progress, f"Loaded NYC hourly rows: {len(nyc_hourly)}")

    _emit_progress(progress, "Loading Paris hourly profile from PostgreSQL")
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
    _emit_progress(progress, f"Loaded Paris hourly rows: {len(paris_hourly)}")

    _emit_progress(progress, "Loading contributor-level facts from PostgreSQL")
    station_fact = read_sql_query(
        """
        SELECT
            region,
            location_id,
            location_name,
            metric_type,
            total_value AS value,
            source
        FROM transport.v_contributor_source
        """,
        pg,
    )
    _emit_progress(progress, f"Loaded station_fact rows: {len(station_fact)}")

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

#!/usr/bin/env python3
"""Run the Stage 1 PostgreSQL-first transport analytics workflow."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the PostgreSQL-backed transport analytics workflow.")
    parser.add_argument(
        "--refresh-sql",
        action="store_true",
        help="Apply sql/01_schema.sql and sql/02_views.sql before reading the analytical contract.",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    os.environ.setdefault("MPLCONFIGDIR", "/tmp/mpl")
    sys.path.insert(0, str(root / "src"))

    from transport_analytics.config import PostgresConfig
    from transport_analytics.methods import run_stage_workflow
    from transport_analytics.postgres import execute_sql_file, load_postgres_artifacts

    pg = PostgresConfig.from_env()
    if args.refresh_sql:
        execute_sql_file(root / "sql" / "01_schema.sql", pg)
        execute_sql_file(root / "sql" / "02_views.sql", pg)

    artifacts = load_postgres_artifacts(pg)
    outputs = run_stage_workflow(artifacts, root=root)

    print("Workflow complete")
    print("db_host:", pg.host)
    print("analysis_schema:", "transport")
    print("station_fact_rows:", len(artifacts.station_fact))
    print("daily_rows:", len(artifacts.daily))
    print("selected_methods:", len(outputs["stage1_plan"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

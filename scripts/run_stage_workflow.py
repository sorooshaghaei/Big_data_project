#!/usr/bin/env python3
"""Run the Stage 1 PostgreSQL-first transport analytics workflow."""

from __future__ import annotations

import argparse
import os
import sys
import threading
import time
from contextlib import contextmanager
from pathlib import Path


def _progress(message: str) -> None:
    print(f"[progress] {message}", flush=True)


@contextmanager
def _heartbeat(label: str, interval_seconds: int = 5):
    stop_event = threading.Event()

    def run() -> None:
        while not stop_event.wait(interval_seconds):
            _progress(f"Still running: {label}")

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    try:
        yield
    finally:
        stop_event.set()
        thread.join(timeout=0.1)


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
        _progress("Applying sql/01_schema.sql")
        with _heartbeat("sql/01_schema.sql"):
            execute_sql_file(root / "sql" / "01_schema.sql", pg)
        _progress("Applying sql/02_views.sql")
        with _heartbeat("sql/02_views.sql"):
            execute_sql_file(root / "sql" / "02_views.sql", pg)

    _progress("Loading PostgreSQL artifacts")
    with _heartbeat("load PostgreSQL artifacts"):
        artifacts = load_postgres_artifacts(pg, progress=_progress)
    _progress("Running Stage 1 workflow")
    with _heartbeat("Stage 1 workflow"):
        outputs = run_stage_workflow(artifacts, root=root, progress=_progress)

    print("Workflow complete")
    print("db_host:", pg.host)
    print("analysis_schema:", "transport")
    print("station_fact_rows:", len(artifacts.station_fact))
    print("daily_rows:", len(artifacts.daily))
    print("selected_methods:", len(outputs["stage1_plan"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

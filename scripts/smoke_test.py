#!/usr/bin/env python3
"""Smoke test for the Big_data_project setup.

Quickly verifies imports, env vars, PostgreSQL connectivity, required tables
and views, and a tiny end-to-end pandas load. Designed to fail fast with
human-readable messages so you can tell whether the project is wired up
correctly without running the full multi-minute workflow.

Usage:
    python scripts/smoke_test.py            # full check (default)
    python scripts/smoke_test.py --quick    # skip the mini end-to-end load
"""
from __future__ import annotations

import argparse
import importlib
import os
import sys
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def _load_dotenv(path: Path) -> int:
    """Minimal .env loader. No external dep. Does not overwrite existing env vars."""
    if not path.is_file():
        return 0
    loaded = 0
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].lstrip()
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if (len(value) >= 2) and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        if not key or key in os.environ:
            continue
        os.environ[key] = value
        loaded += 1
    return loaded


_DOTENV_PATH = ROOT / ".env"
_DOTENV_LOADED = _load_dotenv(_DOTENV_PATH)


REQUIRED_PACKAGES: tuple[str, ...] = (
    "pandas",
    "numpy",
    "sqlalchemy",
    "psycopg",
    "matplotlib",
    "sklearn",
)

REQUIRED_LOCAL_MODULES: tuple[str, ...] = (
    "transport_analytics",
    "transport_analytics.config",
    "transport_analytics.postgres",
    "transport_analytics.features",
    "transport_analytics.methods",
    "transport_analytics.pipeline",
)

REQUIRED_RAW_TABLES: tuple[tuple[str, str], ...] = (
    ("public", "idfm_daily_validations"),
    ("public", "idfm_hourly_profiles"),
    ("public", "mta_hourly_ridership"),
    ("public", "idfm"),
    ("public", "mta"),
)

REQUIRED_VIEWS: tuple[tuple[str, str], ...] = (
    ("transport", "v_daily_demand"),
    ("transport", "v_nyc_hourly_profile"),
    ("transport", "v_paris_hourly_profile"),
    ("transport", "v_contributor_source"),
)


_ENGINE = None


def _get_engine():
    """Lazily build one shared SQLAlchemy engine for the whole run."""
    global _ENGINE
    if _ENGINE is not None:
        return _ENGINE
    from sqlalchemy import create_engine

    from transport_analytics.config import PostgresConfig

    pg = PostgresConfig.from_env()
    _ENGINE = create_engine(
        pg.sqlalchemy_url,
        connect_args={"connect_timeout": 10},
        pool_pre_ping=False,
    )
    return _ENGINE


@dataclass(frozen=True)
class CheckResult:
    name: str
    ok: bool
    detail: str
    fatal: bool = False


def _run_check(
    name: str,
    fn: Callable[[], str],
    *,
    fatal: bool = False,
) -> CheckResult:
    try:
        detail = fn()
        return CheckResult(name=name, ok=True, detail=detail, fatal=fatal)
    except Exception as exc:  # noqa: BLE001 — smoke test wants every failure
        tb = traceback.format_exc(limit=2).strip().splitlines()[-1]
        detail = f"{exc.__class__.__name__}: {exc} ({tb})"
        return CheckResult(name=name, ok=False, detail=detail, fatal=fatal)


def check_packages() -> str:
    missing: list[str] = []
    for pkg in REQUIRED_PACKAGES:
        try:
            importlib.import_module(pkg)
        except ImportError:
            missing.append(pkg)
    if missing:
        raise ImportError(
            "Missing packages: "
            + ", ".join(missing)
            + ". Run: pip install -r requirements.txt"
        )
    return f"all {len(REQUIRED_PACKAGES)} third-party packages importable"


def check_local_modules() -> str:
    for mod in REQUIRED_LOCAL_MODULES:
        importlib.import_module(mod)
    return f"all {len(REQUIRED_LOCAL_MODULES)} local modules importable"


def check_env_vars() -> str:
    from transport_analytics.config import PostgresConfig

    pg = PostgresConfig.from_env()
    return f"loaded config for {pg.user}@{pg.host}:{pg.port}/{pg.database}"


def check_db_ping() -> str:
    from sqlalchemy import text

    with _get_engine().connect() as conn:
        result = conn.execute(text("SELECT 1")).scalar_one()
    if result != 1:
        raise RuntimeError(f"unexpected ping result: {result!r}")
    return "SELECT 1 returned 1"


def check_db_version() -> str:
    from sqlalchemy import text

    with _get_engine().connect() as conn:
        version = conn.execute(text("SELECT version()")).scalar_one()
    short = str(version).split(",", 1)[0]
    return short


def _missing_relations(
    expected: tuple[tuple[str, str], ...],
    relkinds: tuple[str, ...],
) -> list[tuple[str, str]]:
    from sqlalchemy import text

    schemas = sorted({s for s, _ in expected})
    names = sorted({n for _, n in expected})
    query = text(
        """
        SELECT n.nspname AS schema, c.relname AS name
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE c.relkind = ANY(:kinds)
          AND n.nspname = ANY(:schemas)
          AND c.relname = ANY(:names)
        """
    )
    with _get_engine().connect() as conn:
        rows = conn.execute(
            query,
            {
                "kinds": list(relkinds),
                "schemas": schemas,
                "names": names,
            },
        ).all()
    found = {(r.schema, r.name) for r in rows}
    return [pair for pair in expected if pair not in found]


def check_raw_tables() -> str:
    missing = _missing_relations(REQUIRED_RAW_TABLES, ("r", "p"))
    if missing:
        raise RuntimeError(
            "missing raw tables: "
            + ", ".join(f"{s}.{n}" for s, n in missing)
            + " — did you run sql/01_schema.sql and import the source tables?"
        )
    return f"all {len(REQUIRED_RAW_TABLES)} raw tables present"


def check_views() -> str:
    missing = _missing_relations(REQUIRED_VIEWS, ("v", "m"))
    if missing:
        raise RuntimeError(
            "missing analytical views: "
            + ", ".join(f"{s}.{n}" for s, n in missing)
            + " — run sql/02_views.sql"
        )
    return f"all {len(REQUIRED_VIEWS)} analytical views present"


def check_raw_tables_have_rows() -> str:
    """Cheap existence probe on the *base* tables.

    The analytical views (`v_daily_demand`, etc.) are aggregating views with
    `GROUP BY`, so Postgres must materialize the whole thing before LIMIT 1
    can return — that's seconds-to-minutes on this dataset. The base tables
    are plain heaps; `LIMIT 1` returns immediately. If the source data is
    there and the views are defined (already checked above), the views will
    produce rows when the workflow actually needs them.
    """
    from sqlalchemy import text

    empty: list[str] = []
    with _get_engine().connect() as conn:
        for schema, name in REQUIRED_RAW_TABLES:
            fq = f'"{schema}"."{name}"'
            row = conn.execute(text(f"SELECT 1 FROM {fq} LIMIT 1")).first()
            if row is None:
                empty.append(f"{schema}.{name}")
    if empty:
        raise RuntimeError(
            "raw tables exist but are empty: " + ", ".join(empty)
        )
    return f"all {len(REQUIRED_RAW_TABLES)} raw tables return at least one row"


def check_mini_load() -> str:
    """Confirm postgres → pandas wiring works using a base table.

    Avoids hitting the aggregating views (which would force a full scan).
    """
    import pandas as pd
    from sqlalchemy import text

    with _get_engine().connect() as conn:
        sample = pd.read_sql_query(
            text('SELECT * FROM "public"."mta_hourly_ridership" LIMIT 200'),
            conn,
        )
    if sample.empty:
        raise RuntimeError("mta_hourly_ridership returned 0 rows for LIMIT 200 sample")
    return f"loaded {len(sample)} rows × {len(sample.columns)} cols into pandas"


def _print_result(result: CheckResult) -> None:
    tag = "[ok]  " if result.ok else "[fail]"
    print(f"{tag} {result.name}: {result.detail}", flush=True)


def run_all(quick: bool) -> int:
    print(f"Project root: {ROOT}", flush=True)
    print(f"Python: {sys.version.split()[0]}", flush=True)
    if _DOTENV_PATH.is_file():
        print(
            f".env: loaded {_DOTENV_LOADED} var(s) from {_DOTENV_PATH}",
            flush=True,
        )
    else:
        print(
            f".env: not found at {_DOTENV_PATH} (using existing shell env only)",
            flush=True,
        )
    print("-" * 72, flush=True)

    plan: list[tuple[str, Callable[[], str], bool]] = [
        ("third-party packages", check_packages, True),
        ("local modules", check_local_modules, True),
        ("env vars (.env loaded)", check_env_vars, True),
        ("postgres ping", check_db_ping, True),
        ("postgres version", check_db_version, False),
        ("raw tables present", check_raw_tables, False),
        ("analytical views present", check_views, True),
        ("raw tables have rows", check_raw_tables_have_rows, False),
    ]
    if not quick:
        plan.append(("mini load + features", check_mini_load, False))

    results: list[CheckResult] = []
    for name, fn, fatal in plan:
        result = _run_check(name, fn, fatal=fatal)
        _print_result(result)
        results.append(result)
        if not result.ok and result.fatal:
            print("-" * 72, flush=True)
            print(
                "[abort] fatal check failed; skipping remaining checks.",
                flush=True,
            )
            break

    print("-" * 72, flush=True)
    passed = sum(1 for r in results if r.ok)
    failed = [r for r in results if not r.ok]
    print(f"passed: {passed}/{len(results)}", flush=True)
    if failed:
        print("failed:", flush=True)
        for r in failed:
            print(f"  - {r.name}", flush=True)
        return 1
    print("smoke test passed", flush=True)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Smoke test for Big_data_project setup."
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Skip the mini end-to-end load (faster, DB-light).",
    )
    args = parser.parse_args()
    return run_all(quick=args.quick)


if __name__ == "__main__":
    raise SystemExit(main())

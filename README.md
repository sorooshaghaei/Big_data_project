# Big_data_project

PostgreSQL-first reusable project for public transport demand analytics.

Main goals:
- build a canonical analytical layer from PostgreSQL transport tables
- analyze daily/hourly usage patterns
- support forecasting and anomaly detection

Traffic in this project means **validations / entries / ridership counts**.

## Restructured layout

```text
Big_data_project/
├── presentation/
│   ├── metro_ridership_forecasting_isa_tf.pdf
│   ├── README.md
│   └── source/
│       ├── itsc.tex
│       └── images/
├── src/
│   ├── transport_analytics/
│   │   ├── config.py
│   │   ├── io.py
│   │   ├── features.py
│   │   ├── postgres.py
│   │   └── pipeline.py
│   ├── baseline.py            # compatibility wrapper
│   └── utils.py               # compatibility wrapper
├── sql/
│   ├── 01_schema.sql
│   ├── 02_views.sql
│   └── 03_analytics_examples.sql
├── notebooks/
│   └── transport_analytics_workbook.ipynb
├── report/
│   ├── transport_analytics_compendium.tex
│   ├── figures/
│   └── results/
├── scripts/
│   ├── strip_notebook_metadata.py
│   ├── build_report_figures.py
│   └── setup_git_filters.sh
├── docs/
│   ├── PROJECT_STRUCTURE.md
│   ├── GIT_NOTEBOOK_FILTER_SETUP.md
│   └── papers/
```

## Presentation

The professor-facing presentation is here:
- `presentation/metro_ridership_forecasting_isa_tf.pdf`

Slide source files are here:
- `presentation/source/itsc.tex`
- `presentation/source/images/`

## Main Workbook

The main project notebook is now:
- `notebooks/transport_analytics_workbook.ipynb`

The consolidated LaTeX companion document is:
- `report/transport_analytics_compendium.tex`

Analytical outputs from Stage 1 + Stage 2 are written to:
- `report/results/`

Report figures are written to:
- `report/figures/`

## Source Data On PostgreSQL

Stage 1 assumes source truth already exists on PostgreSQL in `public`.

Primary uploaded tables discovered during Stage 0:

- `public.idfm`
- `public.idfm_daily_validations`
- `public.idfm_hourly_profiles`
- `public.mta`
- `public.mta_hourly_ridership`

The project now builds an analytical contract in the `transport` schema on top of those source tables.

## Quick start

1. Load PostgreSQL credentials:
   - `set -a; source .env; set +a`

2. Apply the Stage 1 SQL contract:
   - `psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" -f sql/01_schema.sql`
   - `psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" -f sql/02_views.sql`

3. Run the PostgreSQL-backed workflow:
   - `python3 scripts/run_stage_workflow.py`

4. Read the consolidated notebook:
   - `notebooks/transport_analytics_workbook.ipynb`

5. Read the LaTeX report:
   - `report/transport_analytics_compendium.tex`

Project PostgreSQL/pgAdmin entry:
- `http://34.155.143.75/pgadmin4/browser/`

## Teammate setup (important)

After cloning, run this once so notebook metadata stays clean in git history:

```bash
bash scripts/setup_git_filters.sh
```

If you already have local notebook changes and want to normalize them:

```bash
bash scripts/setup_git_filters.sh --normalize
```

Beginner guide:
- `docs/GIT_NOTEBOOK_FILTER_SETUP.md`

## PostgreSQL-backed Python usage

```python
from pathlib import Path

from transport_analytics.config import PostgresConfig
from transport_analytics.postgres import load_postgres_artifacts
from transport_analytics.methods import run_stage_workflow

pg = PostgresConfig.from_env()
artifacts = load_postgres_artifacts(pg)
outputs = run_stage_workflow(artifacts, root=Path("."))
```

Example SQL analysis queries are in:
- `sql/03_analytics_examples.sql`

## Bibliography

Background paper references are stored in:
- `docs/papers/citations.txt`

## Authors

Nguyen Ho Bao Khanh, Maksym Dolhov, Mehdi Aghaei, Nima Davari

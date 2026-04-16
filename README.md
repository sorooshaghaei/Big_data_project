# Big_data_project

This repository contains the final report assets, SQL views, and Python analysis code for a public-transport analytics project comparing Paris and NYC demand patterns. The official workflow is PostgreSQL-first and the report is written from generated outputs under `report/results/`.

The current repository baseline is:

- a main notebook: `notebooks/transport_analytics_workbook.ipynb`
- a LaTeX report: `report/transport_analytics_compendium.tex`
- the compiled report PDF: `report/transport_analytics_compendium.pdf`
- SQL schema/views/examples under `sql/`
- Python analysis code under `src/transport_analytics/`
- figure and workflow scripts under `scripts/`
- project planning/audit notes under `docs/`

## Contents

### Notebook

- `notebooks/transport_analytics_workbook.ipynb`

Supporting walkthrough aligned with the paper. It reads generated outputs rather than rerunning the full workflow by default.

### Report

- `report/transport_analytics_compendium.tex`
- `report/transport_analytics_compendium.pdf`

These are the main written project artifacts.

### SQL

- `sql/00_db_schema.sql`
- `sql/01_schema.sql`
- `sql/02_views.sql`
- `sql/03_analytics_examples.sql`

These files cover both the database bootstrap and the analytical SQL contract.
`sql/00_db_schema.sql` creates the raw PostgreSQL tables expected by the
project when you are starting from an empty database; `sql/01_schema.sql` and
`sql/02_views.sql` define the analytical layer used by the workflow.

### Python Code

- `src/transport_analytics/`
- `scripts/run_stage_workflow.py`
- `scripts/build_report_figures.py`

This code contains the project’s analysis logic and report-generation helpers. The official entrypoint is `scripts/run_stage_workflow.py`, which writes `report/results/`.

## Current State

- Source datasets are not stored in this repository.
- PostgreSQL is the analysis source of truth.
- `sql/00_db_schema.sql` is available when you need to bootstrap the raw source-table layout in PostgreSQL.
- `report/results/` contains the generated result set used by the paper.
- `report/figures/` is generated from those result tables.
- `notebooks/transport_analytics_workbook.ipynb` is a supporting notebook, not the source of truth for the project narrative.

## Quick Start (PostgreSQL-first)

```bash
set -a
source .env
set +a
# Optional when your PostgreSQL instance does not already contain
# the raw MTA / IDFM source tables:
# psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" -f sql/00_db_schema.sql
# Then apply the project analytical layer:
# psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" -f sql/01_schema.sql
# psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" -f sql/02_views.sql
.venv/bin/python scripts/run_stage_workflow.py
MPLCONFIGDIR=/tmp/mpl .venv/bin/python scripts/build_report_figures.py
```

## Useful Files

- `docs/AGILE_EXECUTION_PLAN.md`
- `docs/STAGE_0_BASELINE_AUDIT.md`
- `docs/PROJECT_STRUCTURE.md`
- `docs/GIT_NOTEBOOK_FILTER_SETUP.md`
- `presentation/metro_ridership_forecasting_isa_tf.pdf`

## Requirements

Python dependencies are listed in `requirements.txt`.

## Authors

- Nguyen Ho Bao Khanh
- Maksym Dolhov
- Mehdi Aghaei
- Nima Davari

# Big_data_project

Course project comparing Paris and NYC public-transport demand with a PostgreSQL-first analysis workflow

## Datasets

The project uses five source tables loaded into PostgreSQL:

- `public.idfm_daily_validations`
- `public.idfm_hourly_profiles`
- `public.mta_hourly_ridership`
- `public.idfm`
- `public.mta`

## Architecture

- PostgreSQL is the source of truth
- `sql/00_db_schema.sql` creates the raw table layout
- `sql/01_schema.sql` and `sql/02_views.sql` create the reporting schema and views
- `scripts/run_stage_workflow.py` reads PostgreSQL and writes `report/results/`
- `scripts/build_report_figures.py` rebuilds `report/figures/`
- `src/transport_analytics/legacy_*.py` is old local-file code and is not part of the final submission path

## Files That Matter

- `report/transport_analytics_compendium.tex` and `report/transport_analytics_compendium.pdf`
- `report/results/`
- `report/figures/`
- `notebooks/transport_analytics_workbook.ipynb`
- `sql/00_db_schema.sql`
- `sql/01_schema.sql`
- `sql/02_views.sql`
- `scripts/run_stage_workflow.py`
- `scripts/build_report_figures.py`
- `docs/POSTGRES_DBEAVER_IMPORT.md`

## Rerun The Analysis

Install dependencies:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

Load the PostgreSQL settings:

```bash
cp .env.example .env
set -a
source .env
set +a
```

Prepare the database with the same process used for this project:

- run `sql/00_db_schema.sql`
- import the five source tables with DBeaver
- run `sql/01_schema.sql`
- run `sql/02_views.sql`
- detailed steps are in `docs/POSTGRES_DBEAVER_IMPORT.md`

Run the analysis:

```bash
.venv/bin/python scripts/run_stage_workflow.py
.venv/bin/python scripts/build_report_figures.py
```

The full-data PostgreSQL run can take several minutes because the reporting views read the whole dataset

## Main Findings

- Paris has higher average daily demand than NYC at about `4.13M` versus `2.63M`
- the lag-based baseline reaches single-digit MAPE in both cities: `5.86%` for NYC and `6.94%` for Paris
- Paris shows a much higher anomaly rate than NYC: `8.96%` versus `0.73%`
- top contributors include Saint-Lazare, La Defense-Grande Arche, Gare de Lyon, Times Sq--42 St, and Grand Central--42 St

## Authors

- Nguyen Ho Bao Khanh
- Maksym Dolhov
- Mehdi Aghaei
- Nima Davari

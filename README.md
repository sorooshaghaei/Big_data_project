# Big_data_project

Course project on public-transport demand in Paris and New York City

## Datasets

We worked with five tables loaded into PostgreSQL:

- `public.idfm_daily_validations`
- `public.idfm_hourly_profiles`
- `public.mta_hourly_ridership`
- `public.idfm`
- `public.mta`

## How It Works

- the raw tables are stored in PostgreSQL
- `sql/01_schema.sql` creates the `transport` schema and the raw table layout in `public` (idempotent: safe to re-run on a populated database)
- `sql/02_views.sql` builds the cleaned views used for the analysis
- `scripts/run_stage_workflow.py` generates the result files in `report/results/`
- `scripts/build_report_figures.py` rebuilds the figures in `report/figures/`

## repo structure

Big_data_project_submission/
├── README.md
├── requirements.txt
├── LICENSE
├── .gitignore
├── .env.example
├── sql/
│   ├── 01_schema.sql
│   ├── 02_views.sql
│   └── 03_analytics_examples.sql  
├── src/
│   └── transport_analytics/
│       ├── __init__.py
│       ├── config.py
│       ├── context.py
│       ├── features.py
│       ├── methods.py
│       ├── pipeline.py
│       └── postgres.py
├── scripts/
│   ├── run_stage_workflow.py
│   └── build_report_figures.py
├── notebooks/
│   └── transport_analytics_workbook.ipynb
├── report/
│   ├── transport_analytics_compendium.pdf
│   ├── transport_analytics_compendium.tex
│   ├── results/
│   └── figures/

## Rerun The Analysis

Install the dependencies:

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

Prepare the database the same way we did during the project:

- run `sql/01_schema.sql`
- import the five source tables with DBeaver
- run `sql/02_views.sql`
- detailed steps are in `docs/POSTGRES_DBEAVER_IMPORT.md`

Then run:

```bash
.venv/bin/python scripts/run_stage_workflow.py
.venv/bin/python scripts/build_report_figures.py
```

The full run can take several minutes because it reads the whole dataset

## Main Findings

- Paris has higher average daily demand than NYC at about `4.13M` versus `2.63M`
- the forecasting baseline reaches single-digit MAPE in both cities: `5.86%` for NYC and `6.94%` for Paris
- Paris shows a much higher anomaly rate than NYC: `8.96%` versus `0.73%`
- top contributors include Saint-Lazare, La Defense-Grande Arche, Gare de Lyon, Times Sq--42 St, and Grand Central--42 St

## Authors

- Nguyen Ho Bao Khanh
- Maksym Dolhov
- Mehdi Aghaei
- Nima Davari

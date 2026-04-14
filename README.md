# Big_data_project

PostgreSQL-first reusable project for public transport demand analytics.

Main goals:
- build a canonical fact table from raw transit datasets
- analyze daily/hourly usage patterns
- support forecasting and anomaly detection
- enrich demand with weather and holidays

Traffic in this project means **validations / entries / ridership counts**.

## Restructured layout

```text
Big_data_project/
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
│   ├── 00_db_schema.sql
│   ├── 01_schema.sql
│   ├── 02_views.sql
│   └── 03_analytics_examples.sql
├── notebooks/
│   ├── 00_python_numpy_matplotlib_pandas_pyspark_bootcamp.ipynb
│   ├── 01_data_analytics_pipeline.ipynb
│   ├── 02_papers_summary.ipynb
│   ├── 03_data_science_big_data_sql_foundations.ipynb
│   └── 04_sql_active_learning_practice.ipynb
├── scripts/
│   ├── strip_notebook_metadata.py
│   └── setup_git_filters.sh
├── docs/
│   ├── PROJECT_STRUCTURE.md
│   ├── POSTGRES_SETUP.md
│   └── GIT_NOTEBOOK_FILTER_SETUP.md
└── data/processed/
```

## Datasets

Main dataset (hourly):
- MTA Subway Hourly Ridership (2020-2024)
  https://data.ny.gov/Transportation/MTA-Subway-Hourly-Ridership-2020-2024/wujg-7c2s

Secondary datasets:
- Ile-de-France Mobilites daily validations (surface network)
  https://data.iledefrance-mobilites.fr/explore/dataset/validations-reseau-surface-nombre-validations-par-jour-1er-trimestre/
- Public transport traffic data in France (Kaggle)
  https://www.kaggle.com/datasets/gatandubuc/public-transport-traffic-data-in-france

## `data/` vs `datasets/`

These two folders have different roles:

- `data/`
  - Main project storage for raw and generated data.
  - Includes large raw sources (for example `data/soroosh_MTA/...`) and processed outputs (`data/processed/...`).
  - Think: **working data area**.

- `datasets/`
  - Curated secondary datasets downloaded by project scripts.
  - Usually smaller, cleaner CSV inputs used for comparative analysis.
  - Think: **packaged dataset inputs**.

In short:
- `data/` = raw + processed pipeline data
- `datasets/` = curated external dataset files

## Quick start

1. Run analytics notebook:
   - `notebooks/00_python_numpy_matplotlib_pandas_pyspark_bootcamp.ipynb`
   - Start here for full Python/data stack foundations + practice

2. Run analytics notebook:
   - `notebooks/01_data_analytics_pipeline.ipynb`

3. Learn project SQL and DS basics:
   - `notebooks/03_data_science_big_data_sql_foundations.ipynb`

4. Practice SQL actively:
   - `notebooks/04_sql_active_learning_practice.ipynb`

5. Setup PostgreSQL:
   - follow `docs/POSTGRES_SETUP.md`
   - run `sql/01_schema.sql`, then `sql/02_views.sql`

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

## Python pipeline usage

```python
from pathlib import Path
from transport_analytics.pipeline import run_local_pipeline

daily, featured = run_local_pipeline(root=Path("."), sample_mode=True)
```

This writes:
- `data/processed/daily_fact_table.csv`
- `data/processed/daily_fact_table_featured.csv`

## PostgreSQL usage

Use `src/transport_analytics/postgres.py` for programmatic loading.

Example SQL analysis queries are in:
- `sql/03_analytics_examples.sql`

## Bibliography

References are stored in:
- `docs/papers/citations.txt`

## Authors

Nguyen Ho Bao Khanh, Maksym Dolhov, Mehdi Aghaei, Nima Davari

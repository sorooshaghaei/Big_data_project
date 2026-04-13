# Big_data_project

This repository contains the final report assets, SQL views, and Python analysis code for a public-transport analytics project comparing Paris and NYC demand patterns.

The current repository baseline is:

- a main notebook: `notebooks/transport_analytics_workbook.ipynb`
- a LaTeX report: `report/transport_analytics_compendium.tex`
- the compiled report PDF: `report/transport_analytics_compendium.pdf`
- SQL schema/views/examples under `sql/`
- Python analysis code under `src/transport_analytics/`
- figure and workflow scripts under `scripts/`
- project planning/audit notes under `docs/`

## What Is In The Repo

### Notebook

- `notebooks/transport_analytics_workbook.ipynb`

This is the main notebook currently tracked in the repository.

### Report

- `report/transport_analytics_compendium.tex`
- `report/transport_analytics_compendium.pdf`

These are the main written project artifacts.

### SQL

- `sql/01_schema.sql`
- `sql/02_views.sql`
- `sql/03_analytics_examples.sql`

These files define and query the project’s analytical SQL layer.

### Python Code

- `src/transport_analytics/`
- `scripts/run_stage_workflow.py`
- `scripts/build_report_figures.py`

This code contains the project’s analysis logic and report-generation helpers.

## Current Repository State

- Source datasets are not stored in this repository.
- PostgreSQL is the analysis source of truth.
- `report/results/` contains the generated Stage 2 result set used by the paper.
- `report/figures/` is generated from those result tables.
- `notebooks/transport_analytics_workbook.ipynb` is a supporting notebook, not the source of truth for the project narrative.

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

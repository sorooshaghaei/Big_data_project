# Big_data_project

This repository contains the written artifacts, SQL files, and Python code for a public transport analytics project comparing Paris and NYC demand patterns.

It is not a polished standalone product. The repo currently serves as a working project archive with:

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
- The notebook is still broader than a final cleaned submission notebook.
- The report exists, but later cleanup and restructuring may still be needed.
- Some scripts assume an external database/environment that is not documented as a public setup flow here.

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

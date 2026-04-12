# Project Structure (Restructured)

This project is now organized around PostgreSQL-backed analysis and clearer delivery of the final artifacts.

## Main directories

- `presentation/`
  - Final presentation PDF for the professor plus LaTeX source assets under `presentation/source/`.
- `notebooks/`
  - One primary workbook: `notebooks/transport_analytics_workbook.ipynb`.
- `report/`
  - One full LaTeX report plus generated figures and method outputs.
- `src/transport_analytics/`
  - Reusable Python package for PostgreSQL-backed loading, feature engineering, and analysis methods.
- `sql/`
  - PostgreSQL schema, views, and analytics query examples.
- `docs/papers/`
  - Background research papers and bibliography notes.
## Backward compatibility

- `src/utils.py` and `src/baseline.py` are kept as compatibility wrappers.

## Suggested workflow

1. Load `.env` into your shell.
2. Apply `sql/01_schema.sql` and `sql/02_views.sql` against PostgreSQL.
3. Run `scripts/run_stage_workflow.py`.
4. Start with `notebooks/transport_analytics_workbook.ipynb`.
5. Use `report/transport_analytics_compendium.tex` for the full written report.
6. Inspect `report/results/` for generated method outputs.
7. Query PostgreSQL through the `transport` views and example SQL scripts.

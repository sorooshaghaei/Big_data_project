# Project Structure

This project is organized around a PostgreSQL-backed analysis workflow and a
small set of final submission artifacts.

## Main directories

- `presentation/`
  - Final presentation PDF for the professor plus LaTeX source assets under `presentation/source/`.
  - Slide images live under `presentation/source/images/`.
- `notebooks/`
  - One trimmed supporting workbook aligned with the final paper.
- `report/`
  - One final LaTeX paper plus generated figures and the `results/` output folder.
- `src/transport_analytics/`
  - Python package for PostgreSQL-backed loading, feature engineering, and analysis methods.
- `sql/`
  - PostgreSQL schema, views, and analytics query examples.
- `docs/papers/`
  - Background research papers and bibliography notes.
## Suggested workflow

1. Load `.env` into your shell.
2. Apply `sql/01_schema.sql` and `sql/02_views.sql` against PostgreSQL.
3. Run `scripts/run_stage_workflow.py` to fill `report/results/`.
4. Regenerate `report/figures/` with `scripts/build_report_figures.py`.
5. Use `report/transport_analytics_compendium.tex` as the primary written artifact.
6. Use `notebooks/transport_analytics_workbook.ipynb` as a supporting walkthrough of the generated outputs.
7. Inspect `report/results/` and the `transport` schema views for reproducibility checks.

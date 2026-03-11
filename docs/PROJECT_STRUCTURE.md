# Project Structure (Restructured)

This project is now organized for reusability, PostgreSQL integration, and clearer delivery of the presentation artifact.

## Main directories

- `presentation/`
  - Final presentation PDF for the professor plus LaTeX source assets under `presentation/source/`.
- `notebooks/`
  - One primary workbook: `notebooks/transport_analytics_workbook.ipynb`.
- `report/`
  - One full LaTeX report plus generated figures and method outputs.
- `src/transport_analytics/`
  - Reusable Python package for chunked ingestion, normalization, feature engineering, context enrichment, and analysis methods.
- `sql/`
  - PostgreSQL schema, views, and analytics query examples.
- `docs/papers/`
  - Background research papers and bibliography notes.
- `data/processed/`
  - Generated clean artifacts from pipeline runs.

## Backward compatibility

- `src/utils.py` and `src/baseline.py` are kept as compatibility wrappers.

## Suggested workflow

1. Run `scripts/run_stage_workflow.py --sample`.
2. Start with `notebooks/transport_analytics_workbook.ipynb`.
3. Use `report/transport_analytics_compendium.tex` for the full Stage 1 + Stage 2 written report.
4. Inspect `report/results/` for generated method outputs.
5. Load the cleaned outputs into PostgreSQL.
6. Query with SQL views and analytics scripts.

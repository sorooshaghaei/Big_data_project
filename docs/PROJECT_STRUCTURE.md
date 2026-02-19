# Project Structure (Restructured)

This project is now organized for reusability and PostgreSQL integration.

## Main directories

- `src/transport_analytics/`
  - Reusable Python package for loading, normalization, feature engineering, and pipeline orchestration.
- `sql/`
  - PostgreSQL schema, views, and analytics query examples.
- `notebooks/`
  - Analysis, learning, and practice notebooks (start with `00_...`).
- `data/processed/`
  - Generated clean artifacts from pipeline runs.

## Backward compatibility

- `src/utils.py` and `src/baseline.py` are kept as compatibility wrappers.

## Suggested workflow

1. Explore and learn with notebooks.
2. Build canonical tables with Python pipeline.
3. Load into PostgreSQL.
4. Query with SQL views and analytics scripts.

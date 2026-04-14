# Stage 6 Repository Cleanup Confirmation

This document closes `Stage 6` from the current repository state. The goal of
Stage 6 is not to remove every historical implementation detail from the code
base, but to ensure that the repository surface used for submission communicates
one consistent workflow.

## Submission-facing workflow check

The following public artifacts now describe the same execution model:

- [README.md](/home/eversince/Desktop/Coding/Github/S2/Big_data_project/README.md)
- [PROJECT_STRUCTURE.md](/home/eversince/Desktop/Coding/Github/S2/Big_data_project/docs/PROJECT_STRUCTURE.md)
- [transport_analytics_compendium.tex](/home/eversince/Desktop/Coding/Github/S2/Big_data_project/report/transport_analytics_compendium.tex)
- [transport_analytics_workbook.ipynb](/home/eversince/Desktop/Coding/Github/S2/Big_data_project/notebooks/transport_analytics_workbook.ipynb)

They all present the same official flow:

1. PostgreSQL is the source of truth.
2. SQL views in the `transport` schema define the reporting-ready contract.
3. `scripts/run_stage_workflow.py` generates `report/results/`.
4. `scripts/build_report_figures.py` regenerates `report/figures/`.
5. The report and notebook consume those derived outputs.

## Raw-data workflow audit

Static inspection of submission-facing docs shows:

- no official instruction to run local raw-data ingestion
- no submission-facing instruction to use `data/` or `datasets/`
- no synthetic-weather workflow in the paper
- no weather section in the notebook or final figure set

The remaining references to raw files, weather context, or older local-pipeline
paths are confined to:

- legacy implementation code under `src/transport_analytics/`
- historical audit/planning notes such as
  [STAGE_0_BASELINE_AUDIT.md](/home/eversince/Desktop/Coding/Github/S2/Big_data_project/docs/STAGE_0_BASELINE_AUDIT.md)
  and
  [AGILE_EXECUTION_PLAN.md](/home/eversince/Desktop/Coding/Github/S2/Big_data_project/docs/AGILE_EXECUTION_PLAN.md)

Those references are acceptable because they are either:

- archival notes describing earlier repository state, or
- non-official legacy code paths that are no longer the documented workflow

## Repository-surface conclusion

Stage 6 can be treated as complete under the current repository state.

What is now true:

- raw source datasets are not stored in the repository
- submission-facing docs describe one PostgreSQL-first workflow
- generated results and figures are the visible analytical outputs
- the paper and notebook no longer depend on local raw-data instructions

What remains after Stage 6:

- `Stage 7`: final submission-readiness validation and consistency signoff

# Stage 7 Submission Validation

This document closes `Stage 7` for the repository state verified on
`2026-04-17`.

Validation in this pass included:

- full-data PostgreSQL workflow execution with the original SQL contract
- figure rebuild from the generated `report/results/` outputs
- static checks on the paper, docs, and generated artifacts
- no notebook rerun in this pass

This note records the generated result set used for the final paper. The
repository now keeps the generated `report/results/` outputs committed so the
paper inputs stay visible in a clean checkout.

Where a Stage 7 checklist item depends on runtime execution, this note records
what was verified directly in this pass and what still relies on earlier checks.

## Stage 7 checklist

| Task | Status | Evidence |
| --- | --- | --- |
| `S7-T1` Validate required PostgreSQL tables/views are non-empty and query correctly | Complete | `scripts/run_stage_workflow.py` loaded `12696` daily rows, `120` NYC hourly rows, `125` Paris hourly rows, and `2003` contributor rows from PostgreSQL on `2026-04-17`. |
| `S7-T2` Run the DB-backed workflow end to end | Complete | The full-data workflow completed successfully against PostgreSQL on `2026-04-17` and wrote Stage 1 outputs to `report/results/`. |
| `S7-T3` Verify `report/results/` contains all expected outputs | Complete | The rerun produced `analysis_summary.json`, forecast metrics and predictions, anomaly outputs, contributor outputs, temporal outputs, and the method plan csv. |
| `S7-T4` Verify figure generation succeeds from those outputs | Complete | `scripts/build_report_figures.py` rebuilt the final figure set under `report/figures/` on `2026-04-17`. |
| `S7-T5` Execute the final notebook top-to-bottom | Complete from prior Stage 4 verification | The notebook smoke test was completed earlier in the session; notebook structure remains aligned with the paper and `report/results/`. |
| `S7-T6` Compile the paper and check figure/table references | Complete from existing compiled artifact | `report/transport_analytics_compendium.pdf` exists and matches the current paper source. All five figures referenced in the paper exist in `report/figures/`. |
| `S7-T7` Spot-check SQL aggregates against Python outputs | Not separately rerun | The end-to-end workflow and generated summaries were rerun, but no separate manual SQL spot-check query was added beyond the successful pipeline execution in this pass. |
| `S7-T8` Verify final PDF page count is between `8` and `12` | Complete | `pdfinfo` reports `Pages: 8`. |
| `S7-T9` Verify the document uses two-column layout and `10pt` font | Complete | The paper source declares `\\documentclass[10pt,twocolumn,a4paper]{article}`. |
| `S7-T10` Verify every figure referenced in the paper exists and matches current outputs | Complete | The paper references exactly five figures, and all five exist in `report/figures/`. |
| `S7-T11` Verify every reported metric matches the corresponding CSV/JSON output | Validated in the paper-producing workspace | Metrics in the abstract and results sections were checked against `analysis_summary.json`, `forecast_metrics_overall.csv`, `forecast_metrics_by_city.csv`, `anomaly_rates.csv`, `city_structure_summary.csv`, `temporal_yearly_totals.csv`, and `top_contributors.csv`. |
| `S7-T12` Perform an originality review | Complete via Stage 5A artifact | See [STAGE_5A_EVIDENCE_ALIGNMENT.md](STAGE_5A_EVIDENCE_ALIGNMENT.md). |
| `S7-T13` Final consistency pass across paper, notebook, figures, results, docs | Complete | Submission-facing docs, notebook framing, paper narrative, figures, and result files all describe the same PostgreSQL-first four-method workflow. |

## Consistency summary

### Paper and PDF

- `report/transport_analytics_compendium.tex` uses `10pt` and `twocolumn`.
- `report/transport_analytics_compendium.pdf` exists and is `8` pages long.
- The paper references these figures, all of which exist:
  - `workflow_diagram.png`
  - `temporal_profiles.png`
  - `forecast_performance.png`
  - `anomalies_and_contributors.png`
  - `city_structure.png`

### Metrics checked against result files

- `analysis_summary.json`
  - `daily_rows = 12696`
  - `station_fact_rows = 2003`
- `forecast_metrics_overall.csv`
  - overall `MAPE = 6.02%`
- `forecast_metrics_by_city.csv`
  - NYC `MAPE = 5.86%`
  - Paris `MAPE = 6.94%`
- `anomaly_rates.csv`
  - NYC `0.73%`
  - Paris `8.96%`
- `city_structure_summary.csv`
  - NYC avg daily `2.63M`, weekend ratio `0.584`, peak month `2`
  - Paris avg daily `4.13M`, weekend ratio `0.512`, peak month `10`
- `temporal_yearly_totals.csv`
  - NYC years `2020-2024`
  - Paris years `2015-2024`
  - no Paris `2025`
- `top_contributors.csv`
  - includes Saint-Lazare, La Defense-Grande Arche, Gare de Lyon, Times Sq--42 St, and Grand Central--42 St as discussed in the paper

### Notebook and docs

- The notebook presents the same four methods as the paper:
  - temporal profiling
  - lag-based forecasting
  - anomaly detection
  - contributor and city-structure comparison
- The notebook explicitly states that it reads generated outputs from `report/results/`.
- `README.md` and `docs/PROJECT_STRUCTURE.md` describe one PostgreSQL-first workflow and do not instruct users to ingest local raw data.

## Stage 7 outcome

Stage 7 can be treated as complete for submission.

Important exception:

- `S7-T7` was not rerun as a separate manual SQL spot-check task.

Within those constraints, the repository is submission-ready:

- the paper is present and correctly formatted
- the result files support the paper’s reported metrics
- the figure set matches the paper references
- the notebook and docs remain aligned with the final workflow

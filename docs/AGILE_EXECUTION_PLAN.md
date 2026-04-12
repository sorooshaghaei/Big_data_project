# AGILE Execution Plan

## Goal

Convert the project into a PostgreSQL-first analytics project with no raw data stored in the repository, then produce the final scientific-style report and reproducible result artifacts.

## Delivery Rules

- Execute stages in order.
- Do not keep raw input files in the repo.
- PostgreSQL is the single source of truth.
- Final deliverables are generated analysis outputs, a trimmed final notebook, and a two-column scientific paper.

## Stage 0. Baseline Audit

### Objective

Confirm what already exists on PostgreSQL and what the repo still assumes about local raw files.

### Tasks

- `S0-T1` Inspect current PostgreSQL tables, schemas, and views used for the project.
- `S0-T2` Map uploaded server data to the project’s expected analytical inputs.
- `S0-T3` Identify every code path, notebook section, doc page, and script that still depends on `data/` or `datasets/`.
- `S0-T4` Confirm which current report claims are based on missing local artifacts or sample-mode placeholders.

### Done Criteria

- A clear inventory exists for:
  - DB tables/views already available
  - local-file dependencies to remove
  - missing analytical result artifacts to regenerate

## Stage 1. PostgreSQL-First Architecture

### Objective

Make the database the only official project input source.

### Tasks

- `S1-T1` Define the final database contract for analysis:
  - canonical demand source
  - daily demand aggregate
  - hourly profile sources
  - contributor ranking source
  - city comparison source
- `S1-T2` Update SQL scripts so required analytical views are stable and named consistently.
- `S1-T3` Remove the repo’s official dependence on local raw-file ingestion.
- `S1-T4` Decide which existing Python interfaces remain public and which become legacy.

### Done Criteria

- SQL layer is sufficient to support all final analyses.
- PostgreSQL is the documented system of record.
- No required final analysis depends on local raw files.

## Stage 2. Workflow Refactor

### Objective

Refactor execution so Python reads from PostgreSQL instead of local raw datasets.

### Tasks

- `S2-T1` Add a DB-backed loader that returns the dataframe set needed by the analysis methods.
- `S2-T2` Replace or retire `run_local_pipeline(...)` in the official workflow.
- `S2-T3` Update `scripts/run_stage_workflow.py` to run from PostgreSQL by default.
- `S2-T4` Ensure generated outputs still land in `report/results/` and `report/figures/`.
- `S2-T5` Keep only derived outputs in the repo workflow, never raw inputs.

### Done Criteria

- End-to-end workflow runs from PostgreSQL.
- Analysis outputs are regenerated without `data/` or `datasets/`.
- No official script requires local raw files.

## Stage 3. Analysis Scope Cleanup

### Objective

Align the analytical story with a defensible final paper.

### Tasks

- `S3-T1` Remove weather from the core final methodology and paper claims.
- `S3-T2` Keep the final method set focused on:
  - temporal profiling
  - forecasting
  - anomaly detection
  - contributor ranking
  - Paris vs NYC structural comparison
- `S3-T3` Regenerate all result tables from the PostgreSQL-backed workflow.
- `S3-T4` Rebuild figures so every figure is backed by real generated outputs.
- `S3-T5` Eliminate hard-coded sample-mode metrics from report text.

### Done Criteria

- Final results are database-backed and reproducible.
- No synthetic-weather placeholder remains in the final narrative.
- All figures and tables correspond to generated result files.

## Stage 4. Notebook Finalization

### Objective

Turn the notebook into a final project notebook rather than a learning workbook.

### Tasks

- `S4-T1` Remove bootcamp, exercises, and raw-file exploration sections.
- `S4-T2` Keep only project-relevant analysis sections in execution order.
- `S4-T3` Add a PostgreSQL connection/setup section.
- `S4-T4` Add result interpretation sections for each final method.
- `S4-T5` Ensure the notebook can run top-to-bottom without local raw data present.

### Done Criteria

- The notebook is short, focused, and submission-ready.
- The notebook reflects the same story as the final paper.
- The notebook is fully PostgreSQL-backed.

## Stage 5. Scientific Paper Rewrite

### Objective

Produce the final report in scientific two-column format.

### Tasks

- `S5-T1` Convert the LaTeX report to a two-column conference/paper style.
- `S5-T2` Rewrite the structure into:
  - Abstract
  - Introduction
  - Data and Architecture
  - Methods
  - Results
  - Discussion and Limitations
  - Conclusion
  - References
- `S5-T3` Replace pipeline-history language with final system description.
- `S5-T4` Insert final generated figures and tables.
- `S5-T5` Make all claims consistent with actual regenerated outputs.

### Done Criteria

- The report compiles cleanly.
- The report reads like a scientific paper, not a project diary.
- The report and notebook are numerically consistent.

## Stage 6. Repository Cleanup

### Objective

Remove raw-data assumptions from the repo surface and leave a clean final submission state.

### Tasks

- `S6-T1` Update `README.md` to describe a PostgreSQL-first workflow only.
- `S6-T2` Update project docs to remove `data/` and `datasets/` as operational inputs.
- `S6-T3` Remove or demote download/raw-ingestion scripts from the official workflow.
- `S6-T4` Ensure `.gitignore` and docs match the new repo policy.
- `S6-T5` Verify no final docs tell users to run local raw-data ingestion.

### Done Criteria

- The repo communicates one consistent workflow.
- Raw data is absent from the project path and documentation.
- Submission reviewers can understand how to reproduce results from PostgreSQL.

## Stage 7. Validation And Submission Readiness

### Objective

Verify that the project is complete and internally consistent.

### Tasks

- `S7-T1` Validate that required PostgreSQL tables/views are non-empty and query correctly.
- `S7-T2` Run the DB-backed workflow end to end.
- `S7-T3` Verify `report/results/` contains all expected outputs.
- `S7-T4` Verify figure generation succeeds from those outputs.
- `S7-T5` Execute the final notebook top-to-bottom.
- `S7-T6` Compile the paper and check figure/table references.
- `S7-T7` Spot-check one or two SQL aggregates against the Python-produced outputs.

### Done Criteria

- Workflow executes successfully from PostgreSQL.
- Notebook runs.
- Paper compiles.
- Results are internally consistent.

## Final Deliverables

- PostgreSQL-first analysis workflow
- Clean SQL views/scripts supporting final analysis
- Generated result tables in `report/results/`
- Generated figures in `report/figures/`
- Final trimmed notebook
- Final two-column scientific paper
- Updated README and docs without raw-data workflow references

## Defaults And Assumptions

- PostgreSQL already contains the project data needed for analysis.
- Weather is removed from the final paper instead of supported with synthetic data.
- The final report is the primary submission artifact.
- Generated outputs may remain in the project as derived artifacts; raw inputs may not.

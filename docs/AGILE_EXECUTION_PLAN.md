# AGILE Execution Plan

## Goal

Convert the project into a PostgreSQL-first analytics project with no raw data stored in the repository, then produce a submission-ready scientific report and reproducible result artifacts.

## Delivery Rules

- Execute stages in order.
- Do not keep raw input files in the repo.
- PostgreSQL is the single source of truth.
- Final deliverables are generated analysis outputs, a trimmed final notebook, and a two-column scientific paper.
- The final paper must be `8-12 pages`, `two columns`, and `10pt`.
- All report writing must be original; copied or closely paraphrased paper text is not acceptable.

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
- `S4-T6` Align notebook sections with the final paper order where relevant.
- `S4-T7` Keep notebook commentary original and concise rather than copied from the paper.
- `S4-T8` Ensure the notebook supports the paper instead of creating a second competing narrative.

### Done Criteria

- The notebook is short, focused, and submission-ready.
- The notebook reflects the same story as the final paper.
- The notebook is fully PostgreSQL-backed.
- The notebook does not introduce extra claims absent from the paper.
- The notebook and paper remain numerically consistent.

## Stage 5. Scientific Paper Production

### Objective

Produce a submission-ready scientific paper of `8-12 pages`, `two columns`, `10pt`, fully consistent with the generated outputs and written in original language.

### Tasks

- `S5-T1` Lock the final paper template and format:
  - two-column layout
  - 10pt font
  - final page target of `8-12 pages`
- `S5-T2` Build the full scientific structure:
  - Abstract
  - Introduction
  - Related Work
  - Data Description
  - PostgreSQL-Centered Architecture
  - Methods
  - Results
  - Discussion and Limitations
  - Conclusion
  - References
- `S5-T3` Add a literature synthesis section using the papers already stored in `docs/papers/`.
- `S5-T4` Expand Data and Methods so the report explains:
  - source datasets
  - temporal and spatial coverage
  - reporting-clean filtering
  - final SQL analytical contract
  - rationale for each of the four methods
- `S5-T4A` Explain why PostgreSQL was chosen as the analytical backbone:
  - single source of truth for uploaded data
  - separation between source tables and analytical views
  - reproducible SQL-defined contract for Python, notebook, and report
  - removal of dependence on local raw files
  - better fit for structured transport analytics than ad hoc CSV-only execution
- `S5-T4B` Do not include server hardware or infrastructure specifications unless they become formally required by the course.
- `S5-T5` Expand Results into four result subsections:
  - temporal profiling
  - forecasting
  - anomaly detection
  - contributor / city-structure comparison
- `S5-T6` Add a dedicated Limitations subsection that is analytical rather than apologetic.
- `S5-T7` Use only original writing; no pasted or lightly reworded paper text.
- `S5-T8` Ensure every claim is backed by either:
  - generated results in `report/results/`
  - a cited paper from the literature set
- `S5-T9` Follow a page-budget target:
  - Abstract: `0.25-0.5` page
  - Introduction: `0.75-1.0` page
  - Related Work: `0.75-1.0` page
  - Data + Architecture: `1.0-1.5` pages
  - Methods: `1.5-2.0` pages
  - Results: `2.0-3.0` pages
  - Discussion + Conclusion: `1.0-1.5` pages
  - References: remaining space as needed

### Done Criteria

- The report compiles cleanly.
- The report is `8-12 pages`.
- The report uses two-column `10pt` formatting.
- The report reads like a scientific paper, not a project diary.
- The report and notebook are numerically consistent.
- All analytical claims match generated outputs.
- Literature discussion is cited properly and paraphrased originally.
- The paper includes a short PostgreSQL rationale subsection.
- The paper does not include hardware or server-specification claims.

## Stage 5A. Evidence And Citation Alignment

### Objective

Ensure the report is evidence-backed, properly cited, and original.

### Tasks

- `S5A-T1` Map each quantitative claim in the paper to a generated file in `report/results/`.
- `S5A-T2` Map each literature claim to a cited paper in `docs/papers/`.
- `S5A-T3` Remove uncited background statements and unsupported conclusions.
- `S5A-T4` Replace generic filler prose with analysis tied to actual project outputs.
- `S5A-T5` Review wording for plagiarism risk:
  - no copied abstract or introduction text
  - no close paraphrase of related-work papers
  - no copied dataset descriptions from source documents
- `S5A-T6` Standardize bibliography and in-text citation style.

### Done Criteria

- Each figure, table, and claim has a traceable source.
- No unsupported statements remain.
- Literature summaries are original and paraphrased.
- Bibliography is complete and consistent.

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
- `S7-T8` Verify the final PDF page count is between `8` and `12`.
- `S7-T9` Verify the document uses two-column layout and `10pt` font.
- `S7-T10` Verify every figure referenced in the paper exists and matches current outputs.
- `S7-T11` Verify every reported metric matches the corresponding CSV or JSON output.
- `S7-T12` Perform an originality review:
  - no copied passages from source papers
  - no copied dataset descriptions
  - no stale placeholder text
- `S7-T13` Perform a final consistency pass across:
  - paper
  - notebook
  - figures
  - results
  - README and docs if relevant to submission

### Done Criteria

- Workflow executes successfully from PostgreSQL.
- Notebook runs.
- Paper compiles.
- Paper satisfies page-count and format rules.
- Results are internally consistent.
- Originality review is complete.

## Final Deliverables

- PostgreSQL-first analysis workflow
- Clean SQL views/scripts supporting final analysis
- Generated result tables in `report/results/`
- Generated figures in `report/figures/`
- Final trimmed notebook
- Final `8-12` page, `10pt`, two-column scientific paper
- Updated README and docs without raw-data workflow references

## Defaults And Assumptions

- PostgreSQL already contains the project data needed for analysis.
- Weather is removed from the final paper instead of supported with synthetic data.
- The final report is the primary submission artifact.
- Generated outputs may remain in the project as derived artifacts; raw inputs may not.
- Anti-plagiarism means original prose throughout, with citations used for attribution rather than copied wording.
- Papers already stored under `docs/papers/` are the initial literature base for related work and citation support.
- PostgreSQL rationale is part of the methodology; hardware details are out of scope unless the course explicitly requires them.

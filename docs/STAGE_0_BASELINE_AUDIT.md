# Stage 0 Baseline Audit

## Scope

This audit executes Stage 0 of [AGILE_EXECUTION_PLAN.md](AGILE_EXECUTION_PLAN.md) as far as possible from the repository state alone.

Current limitation:

- None for Stage 0. Database inspection was completed after loading valid PostgreSQL connection values from `.env`.

## Task Status

| Task | Status | Notes |
| --- | --- | --- |
| `S0-T1` Inspect current PostgreSQL tables, schemas, and views | Complete | Database connectivity succeeded and the non-system schema/table inventory was captured. |
| `S0-T2` Map uploaded server data to expected analytical inputs | Complete | Uploaded tables can support the final analysis, but the repo still needs a PostgreSQL-first analytical layer on top of them. |
| `S0-T3` Identify repo dependencies on `data/` or `datasets/` | Complete | Raw-data assumptions are still widespread across docs, notebook content, and the local pipeline code. |
| `S0-T4` Confirm report claims based on missing artifacts or placeholders | Complete | The report still relies on sample-mode language, synthetic weather, and generated outputs that are not present in the repo. |

## Findings For `S0-T1`

### 1. Active database connection

- Database: `transport`
- User: `team`
- Default schema from `.env`: `public`

### 2. Available non-system schemas

- `public`
- `pg_toast`

Only `public` is relevant to the project.

### 3. Uploaded project tables already on PostgreSQL

The server already holds the source-level transport data in `public`:

- `public.idfm`
  - Paris / Ile-de-France network dimension table
- `public.idfm_daily_validations`
  - Parent partitioned table for daily validations
- `public.idfm_hourly_profiles`
  - Parent partitioned table for hourly profile shares
- `public.mta`
  - NYC station dimension table
- `public.mta_hourly_ridership`
  - Parent partitioned table for hourly ridership

### 4. Partition layout

The main fact-style tables are partitioned by year and already loaded:

- `idfm_daily_validations`
  - partitions `2015` through `2026` plus `default`
- `idfm_hourly_profiles`
  - partitions `2015` through `2026` plus `default`
- `mta_hourly_ridership`
  - partitions `2020` through `2026` plus `default`

### 5. Coverage windows

- `idfm_daily_validations`
  - date range: `2015-01-01` to `2025-12-09`
- `mta_hourly_ridership`
  - date range: `2020-01-01` to `2024-12-31`

### 6. Dimension-table shape

- `public.idfm`
  - approx. `10,031` dimension rows
  - `network_type` breakdown:
    - `line`: `6,847`
    - `station`: `3,241`
  - key columns:
    - `network_id`
    - `network_name`
    - `network_type`
    - `id_refa_lda`
- `public.mta`
  - `428` station rows
  - includes:
    - `station_id`
    - `station_name`
    - `borough`
    - `latitude`
    - `longitude`

### 7. No analytical views yet

At Stage 0, the server contains uploaded source tables, not the final analytical contract expected by the repo.

Missing from PostgreSQL right now:

- canonical merged demand fact view/table
- daily analytical aggregate view
- calendar dimension
- weather dimension
- final analysis views under a dedicated project schema such as `transport`

## Findings For `S0-T3`

### 1. Local raw-data dependency in code

- `src/transport_analytics/pipeline.py`
  - Reads local raw files from `data/` and `datasets/`.
  - Persists derived CSVs into `data/processed/`.
  - Remains the main source for `run_local_pipeline(...)`.
- `src/transport_analytics/config.py`
  - Encodes file-system paths for `datasets/`, `data/`, MTA, Ile-de-France, and weather CSV inputs.
- `src/transport_analytics/context.py`
  - Still supports `data/weather_daily.csv`.
  - Falls back to synthetic weather when no local weather file exists.
- `src/baseline.py`
  - Still runs the local pipeline.
- `src/transport_analytics/__init__.py`
  - Exposes `run_local_pipeline`, `build_station_fact_table`, and other local-file pipeline interfaces as public API.
- `scripts/run_stage_workflow.py`
  - Still executes the local pipeline before running Stage 2 methods.
- `src/transport_analytics/postgres.py`
  - Is currently positioned as a loader target, not the primary analysis source.

### 2. Local raw-data dependency in docs

- `README.md`
  - Describes `data/` and `datasets/` as part of the official workflow.
  - Documents `run_local_pipeline(...)`.
  - Describes `write_pipeline_outputs(...)` as the PostgreSQL path, which makes PostgreSQL downstream of local files.
- `docs/PROJECT_STRUCTURE.md`
  - Still references `data/processed/` as part of the intended structure.
  - Recommends running the local stage workflow first.
- `docs/POSTGRES_SETUP.md`
  - Was previously written around local pipeline execution followed by PostgreSQL loading.
  - Current worktree state should be re-checked before editing because it is not clean.

### 3. Local raw-data dependency in notebook content

- `notebooks/transport_analytics_workbook.ipynb`
  - Still contains explicit sections describing `data/` and `datasets/`.
  - Includes raw-file exploration and teaching content unrelated to the final project deliverable.
  - Includes synthetic/demo sections that are not appropriate for the final PostgreSQL-first submission notebook.

## Findings For `S0-T4`

### 1. Report claims tied to placeholders

- `report/transport_analytics_compendium.tex`
  - Still references synthetic weather as part of the workflow.
  - Still claims a validated sample-mode run.
  - Still instructs readers to inspect `data/processed/`.
  - Still frames some findings around placeholder or interim execution constraints rather than the intended final system.

### 2. Report claims tied to missing generated artifacts

- The report references `report/results/*.csv` outputs extensively.
- `report/results/` is not present in the repository.
- This means the paper currently documents generated outputs that are expected to exist at runtime, but are not available for verification from the tracked repo alone.

### 3. Figure/story mismatch

- `scripts/build_report_figures.py`
  - Still builds a combined weather-and-forecast figure even though the final plan removes weather from the final paper.
  - Still visualizes a workflow that starts from raw files rather than PostgreSQL.

## Findings For `S0-T2`

### 1. Uploaded PostgreSQL tables already cover the core project inputs

The current server data can support the final paper’s reduced method set.

#### Canonical demand source

Can be built from:

- `public.idfm_daily_validations`
  - Paris / Ile-de-France daily validations
- `public.mta_hourly_ridership`
  - NYC hourly ridership, aggregatable to daily level

#### Daily demand aggregate

Can be derived in SQL by:

- grouping `idfm_daily_validations` by `service_date` and chosen Paris grouping level
- grouping `mta_hourly_ridership` by `transit_date_local` and chosen NYC grouping level

#### Hourly profile sources

Already available as:

- `public.idfm_hourly_profiles`
  - Paris hourly validation-share profiles
- `public.mta_hourly_ridership`
  - NYC hourly ridership, aggregatable by hour

#### Contributor ranking source

Can be built from:

- `public.idfm_daily_validations` joined to `public.idfm`
- `public.mta_hourly_ridership` joined to `public.mta`

Important limitation:

- Paris data is keyed by `network_id`, which can represent either a `line` or a `station`.
- Final contributor logic will need an explicit rule for whether the paper compares stations only, lines only, or both with labeling.

#### Paris vs NYC structural comparison

Can be built from:

- Paris daily validations from `public.idfm_daily_validations`
- NYC daily ridership aggregated from `public.mta_hourly_ridership`

### 2. What is still missing for the repo’s intended workflow

The uploaded server data is usable, but not yet shaped into the project’s intended analysis interface.

Stage 1 must create:

- stable analytical SQL views
- a canonical cross-city demand model
- a DB-backed Python loader that reads those views directly

### 3. Contract mismatch with the current repo

The repo currently expects or documents:

- local raw files under `data/` and `datasets/`
- optional loading into PostgreSQL
- a project schema named `transport`

The server currently provides:

- source tables in `public`
- no final `transport` analysis schema
- no calendar or weather support

This mismatch is the main result of Stage 0 and defines the required Stage 1 work.

## Stage 0 Exit Criteria Status

### Completed

- Database-side inventory of schemas, tables, partitions, and date coverage.
- Mapping of uploaded PostgreSQL tables to final analytical inputs.
- Repo-side inventory of raw-data dependencies.
- Repo-side inventory of report placeholders and unverifiable generated-output references.

## Required Next Step

Stage 0 is complete.

Stage 1 should now begin with:

1. defining the PostgreSQL-first analytical contract
2. creating stable SQL views on top of `public.idfm_*` and `public.mta_*`
3. deciding how Paris contributor granularity should be handled in the final paper
4. replacing the repo’s local-file-first workflow with DB-backed execution

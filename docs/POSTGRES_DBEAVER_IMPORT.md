# PostgreSQL DBeaver Import

This is the exact workflow used for the project

1. Run `sql/01_schema.sql` to create the `transport` schema and the raw tables in PostgreSQL
2. Open DBeaver and connect to the PostgreSQL database
3. Import the five source tables into the raw `public` schema tables created by `sql/01_schema.sql`

The five imported tables are:

- `public.idfm_daily_validations`
- `public.idfm_hourly_profiles`
- `public.mta_hourly_ridership`
- `public.idfm`
- `public.mta`

After the raw tables are loaded:

1. Run `sql/02_views.sql`
2. Load `.env`
3. Run `scripts/run_stage_workflow.py`
4. Run `scripts/build_report_figures.py`

The final submission path is PostgreSQL-first

- `report/results/` stores the generated outputs used by the paper
- `report/figures/` stores the rebuilt figures
- `src/transport_analytics/legacy_*.py` is older local-file code and is not part of the final submission path

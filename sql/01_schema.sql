-- ---------------------------------------------------------------------
-- Stage 1 PostgreSQL-first schema bootstrap
-- ---------------------------------------------------------------------

-- Source truth remains in the `public` schema.
-- The `transport` schema contains only derived analytical views and helpers.
CREATE SCHEMA IF NOT EXISTS transport;

-- ---------------------------------------------------------------------
-- Stage 2 analytical views built from PostgreSQL source tables
-- Reporting-facing views exclude incomplete years and normalize obvious
-- contributor label issues so downstream outputs stay consistent.
-- ---------------------------------------------------------------------

CREATE SCHEMA IF NOT EXISTS transport;

-- Remove legacy placeholder objects from earlier local-file-first versions.
DROP VIEW IF EXISTS transport.v_city_structure_source CASCADE;
DROP VIEW IF EXISTS transport.v_contributor_source CASCADE;
DROP VIEW IF EXISTS transport.v_paris_hourly_profile CASCADE;
DROP VIEW IF EXISTS transport.v_nyc_hourly_profile CASCADE;
DROP VIEW IF EXISTS transport.v_daily_demand_enriched CASCADE;
DROP VIEW IF EXISTS transport.v_daily_demand CASCADE;
DROP VIEW IF EXISTS transport.v_daily_demand_raw CASCADE;
DROP VIEW IF EXISTS transport.fact_demand CASCADE;
DROP VIEW IF EXISTS transport.v_reporting_date_ranges CASCADE;
DROP VIEW IF EXISTS transport.v_reporting_complete_years CASCADE;
DROP TABLE IF EXISTS transport.fact_demand CASCADE;
DROP TABLE IF EXISTS transport.dim_calendar CASCADE;
DROP TABLE IF EXISTS transport.dim_weather CASCADE;

-- Raw daily demand aggregate. This preserves the Stage 1 fast path and lets
-- reporting-year coverage be calculated from a much smaller daily layer.
CREATE VIEW transport.v_daily_demand_raw AS
WITH paris_daily AS (
    SELECT
        d.service_date AS demand_date,
        'Paris'::text AS city,
        'Ile-de-France'::text AS region,
        'idfm_station_daily'::text AS source,
        'validations'::text AS metric_type,
        SUM(d.nb_validations)::numeric AS total_value
    FROM public.idfm_daily_validations d
    JOIN public.idfm n
        ON n.network_id = d.network_id
    WHERE n.network_type = 'station'
      AND d.service_date IS NOT NULL
      AND d.nb_validations IS NOT NULL
    GROUP BY d.service_date
), nyc_daily AS (
    SELECT
        h.transit_date_local AS demand_date,
        'NYC'::text AS city,
        COALESCE(m.borough, 'NYC')::text AS region,
        'mta_station_daily'::text AS source,
        'ridership'::text AS metric_type,
        SUM(h.ridership)::numeric AS total_value
    FROM public.mta_hourly_ridership h
    LEFT JOIN public.mta m
        ON m.station_id = h.station_id
    WHERE h.transit_date_local IS NOT NULL
      AND h.ridership IS NOT NULL
    GROUP BY
        h.transit_date_local,
        COALESCE(m.borough, 'NYC')::text
)
SELECT * FROM paris_daily
UNION ALL
SELECT * FROM nyc_daily;

-- Reporting-safe year scope by city. The project only needs to exclude
-- partial boundary years, so use cheap min/max date bounds rather than
-- scanning every day in the source tables.
CREATE VIEW transport.v_reporting_complete_years AS
WITH city_bounds AS (
    SELECT
        'Paris'::text AS city,
        MIN(d.service_date) AS min_date,
        MAX(d.service_date) AS max_date
    FROM public.idfm_daily_validations d
    JOIN public.idfm n
        ON n.network_id = d.network_id
    WHERE n.network_type = 'station'
      AND d.service_date IS NOT NULL
      AND d.nb_validations IS NOT NULL
    UNION ALL
    SELECT
        'NYC'::text AS city,
        MIN(h.transit_date_local) AS min_date,
        MAX(h.transit_date_local) AS max_date
    FROM public.mta_hourly_ridership h
    WHERE h.transit_date_local IS NOT NULL
      AND h.ridership IS NOT NULL
), included_years AS (
    SELECT
        b.city,
        year_candidate AS year
    FROM city_bounds b
    CROSS JOIN LATERAL generate_series(
        EXTRACT(YEAR FROM b.min_date)::integer,
        EXTRACT(YEAR FROM b.max_date)::integer
    ) AS year_candidate
    WHERE (
        year_candidate > EXTRACT(YEAR FROM b.min_date)::integer
        OR (
            year_candidate = EXTRACT(YEAR FROM b.min_date)::integer
            AND b.min_date = MAKE_DATE(year_candidate, 1, 1)
        )
    )
      AND (
        year_candidate < EXTRACT(YEAR FROM b.max_date)::integer
        OR (
            year_candidate = EXTRACT(YEAR FROM b.max_date)::integer
            AND b.max_date = MAKE_DATE(year_candidate, 12, 31)
        )
    )
)
SELECT
    i.city,
    i.year,
    min_date,
    max_date,
    (
        MAKE_DATE(i.year, 12, 31)
        - MAKE_DATE(i.year, 1, 1)
        + 1
    )::integer AS observed_days,
    expected_days
FROM (
    SELECT
        city,
        year,
        MAKE_DATE(year, 1, 1) AS min_date,
        MAKE_DATE(year, 12, 31) AS max_date,
        (
            MAKE_DATE(year, 12, 31)
            - MAKE_DATE(year, 1, 1)
            + 1
        )::integer AS expected_days
    FROM included_years
) i;

CREATE VIEW transport.v_reporting_date_ranges AS
SELECT
    city,
    MIN(min_date) AS start_date,
    MAX(max_date) + INTERVAL '1 day' AS end_date_exclusive
FROM transport.v_reporting_complete_years
GROUP BY city;

-- Canonical station-grain demand facts, derived directly from PostgreSQL
-- source tables. Paris is restricted to station entities only so later
-- contributor comparisons remain comparable with NYC stations.
CREATE VIEW transport.fact_demand AS
WITH paris_reporting_range AS (
    SELECT start_date, end_date_exclusive::date AS end_date_exclusive
    FROM transport.v_reporting_date_ranges
    WHERE city = 'Paris'
), nyc_reporting_range AS (
    SELECT start_date, end_date_exclusive::date AS end_date_exclusive
    FROM transport.v_reporting_date_ranges
    WHERE city = 'NYC'
), paris_station_daily AS (
    SELECT
        d.service_date AS demand_date,
        'Paris'::text AS city,
        'Ile-de-France'::text AS region,
        COALESCE(NULLIF(n.id_refa_lda, ''), n.network_id::text) AS location_id,
        REGEXP_REPLACE(BTRIM(n.network_name), '\s+', ' ', 'g') AS location_name,
        'validations'::text AS metric_type,
        SUM(d.nb_validations)::numeric AS value,
        'idfm_station_daily'::text AS source
    FROM public.idfm_daily_validations d
    JOIN public.idfm n
        ON n.network_id = d.network_id
    CROSS JOIN paris_reporting_range r
    WHERE n.network_type = 'station'
      AND d.service_date IS NOT NULL
      AND d.nb_validations IS NOT NULL
      AND d.service_date >= r.start_date
      AND d.service_date < r.end_date_exclusive
    GROUP BY
        d.service_date,
        COALESCE(NULLIF(n.id_refa_lda, ''), n.network_id::text),
        REGEXP_REPLACE(BTRIM(n.network_name), '\s+', ' ', 'g')
), nyc_station_daily AS (
    SELECT
        h.transit_date_local AS demand_date,
        'NYC'::text AS city,
        COALESCE(m.borough, 'NYC')::text AS region,
        h.station_id::text AS location_id,
        REGEXP_REPLACE(BTRIM(COALESCE(m.station_name, h.station_id::text)), '\s+', ' ', 'g') AS location_name,
        'ridership'::text AS metric_type,
        SUM(h.ridership)::numeric AS value,
        'mta_station_daily'::text AS source
    FROM public.mta_hourly_ridership h
    LEFT JOIN public.mta m
        ON m.station_id = h.station_id
    CROSS JOIN nyc_reporting_range r
    WHERE h.transit_date_local IS NOT NULL
      AND h.ridership IS NOT NULL
      AND h.transit_date_local >= r.start_date
      AND h.transit_date_local < r.end_date_exclusive
    GROUP BY
        h.transit_date_local,
        COALESCE(m.borough, 'NYC')::text,
        h.station_id::text,
        REGEXP_REPLACE(BTRIM(COALESCE(m.station_name, h.station_id::text)), '\s+', ' ', 'g')
)
SELECT *
FROM paris_station_daily
UNION ALL
SELECT *
FROM nyc_station_daily;

-- Reporting-clean daily demand aggregated from the raw daily layer.
CREATE VIEW transport.v_daily_demand AS
WITH paris_reporting_range AS (
    SELECT start_date, end_date_exclusive::date AS end_date_exclusive
    FROM transport.v_reporting_date_ranges
    WHERE city = 'Paris'
), nyc_reporting_range AS (
    SELECT start_date, end_date_exclusive::date AS end_date_exclusive
    FROM transport.v_reporting_date_ranges
    WHERE city = 'NYC'
)
SELECT d.*
FROM transport.v_daily_demand_raw d
CROSS JOIN paris_reporting_range r
WHERE d.city = 'Paris'
  AND d.demand_date >= r.start_date
  AND d.demand_date < r.end_date_exclusive
UNION ALL
SELECT d.*
FROM transport.v_daily_demand_raw d
CROSS JOIN nyc_reporting_range r
WHERE d.city = 'NYC'
  AND d.demand_date >= r.start_date
  AND d.demand_date < r.end_date_exclusive;

-- NYC hourly ridership profile derived from hourly source truth.
CREATE VIEW transport.v_nyc_hourly_profile AS
WITH nyc_reporting_range AS (
    SELECT start_date, end_date_exclusive::date AS end_date_exclusive
    FROM transport.v_reporting_date_ranges
    WHERE city = 'NYC'
)
SELECT
    COALESCE(m.borough, 'NYC')::text AS region,
    EXTRACT(HOUR FROM h.transit_local_hour)::integer AS hour,
    LPAD(EXTRACT(HOUR FROM h.transit_local_hour)::integer::text, 2, '0') || ':00' AS hour_label,
    SUM(h.ridership)::numeric AS hourly_total
FROM public.mta_hourly_ridership h
LEFT JOIN public.mta m
    ON m.station_id = h.station_id
CROSS JOIN nyc_reporting_range r
WHERE h.transit_local_hour IS NOT NULL
  AND h.transit_date_local IS NOT NULL
  AND h.ridership IS NOT NULL
  AND h.transit_date_local >= r.start_date
  AND h.transit_date_local < r.end_date_exclusive
GROUP BY
    COALESCE(m.borough, 'NYC')::text,
    EXTRACT(HOUR FROM h.transit_local_hour)::integer;

-- Paris hourly validation-share profile restricted to station entities.
CREATE VIEW transport.v_paris_hourly_profile AS
SELECT
    'Paris'::text AS city,
    p.day_type AS day_category,
    p.hour_slot AS hour_bin,
    AVG(p.pct_validations)::numeric AS validation_share_pct
FROM public.idfm_hourly_profiles p
JOIN public.idfm n
    ON n.network_id = p.network_id
WHERE n.network_type = 'station'
  AND p.day_type IS NOT NULL
  AND p.hour_slot IS NOT NULL
  AND p.pct_validations IS NOT NULL
GROUP BY p.day_type, p.hour_slot;

-- Stable source for contributor analysis.
CREATE VIEW transport.v_contributor_source AS
WITH paris_reporting_range AS (
    SELECT start_date, end_date_exclusive::date AS end_date_exclusive
    FROM transport.v_reporting_date_ranges
    WHERE city = 'Paris'
), nyc_reporting_range AS (
    SELECT start_date, end_date_exclusive::date AS end_date_exclusive
    FROM transport.v_reporting_date_ranges
    WHERE city = 'NYC'
), paris_raw AS (
    SELECT
        'Paris'::text AS city,
        'Ile-de-France'::text AS region,
        'idfm_station_daily'::text AS source,
        'validations'::text AS metric_type,
        COALESCE(NULLIF(n.id_refa_lda, ''), n.network_id::text) AS location_id,
        n.network_name AS raw_location_name,
        SUM(d.nb_validations)::numeric AS total_value
    FROM public.idfm_daily_validations d
    JOIN public.idfm n
        ON n.network_id = d.network_id
    CROSS JOIN paris_reporting_range r
    WHERE n.network_type = 'station'
      AND d.nb_validations IS NOT NULL
      AND d.service_date >= r.start_date
      AND d.service_date < r.end_date_exclusive
    GROUP BY
        COALESCE(NULLIF(n.id_refa_lda, ''), n.network_id::text),
        n.network_name
), paris_contributors AS (
    SELECT
        city,
        region,
        source,
        metric_type,
        location_id,
        REGEXP_REPLACE(BTRIM(raw_location_name), '\s+', ' ', 'g') AS location_name,
        SUM(total_value)::numeric AS total_value
    FROM paris_raw
    GROUP BY
        city,
        region,
        source,
        metric_type,
        location_id,
        REGEXP_REPLACE(BTRIM(raw_location_name), '\s+', ' ', 'g')
), nyc_raw AS (
    SELECT
        'NYC'::text AS city,
        COALESCE(m.borough, 'NYC')::text AS region,
        'mta_station_daily'::text AS source,
        'ridership'::text AS metric_type,
        h.station_id::text AS location_id,
        COALESCE(m.station_name, h.station_id::text) AS raw_location_name,
        SUM(h.ridership)::numeric AS total_value
    FROM public.mta_hourly_ridership h
    LEFT JOIN public.mta m
        ON m.station_id = h.station_id
    CROSS JOIN nyc_reporting_range r
    WHERE h.ridership IS NOT NULL
      AND h.transit_date_local >= r.start_date
      AND h.transit_date_local < r.end_date_exclusive
    GROUP BY
        COALESCE(m.borough, 'NYC')::text,
        h.station_id::text,
        COALESCE(m.station_name, h.station_id::text)
), nyc_contributors AS (
    SELECT
        city,
        region,
        source,
        metric_type,
        location_id,
        REGEXP_REPLACE(BTRIM(raw_location_name), '\s+', ' ', 'g') AS location_name,
        SUM(total_value)::numeric AS total_value
    FROM nyc_raw
    GROUP BY
        city,
        region,
        source,
        metric_type,
        location_id,
        REGEXP_REPLACE(BTRIM(raw_location_name), '\s+', ' ', 'g')
)
SELECT * FROM paris_contributors
UNION ALL
SELECT * FROM nyc_contributors;

-- Stable source for city-level structural comparisons.
CREATE VIEW transport.v_city_structure_source AS
SELECT
    demand_date,
    city,
    SUM(total_value) AS total_value,
    EXTRACT(MONTH FROM demand_date)::integer AS month,
    CASE
        WHEN EXTRACT(ISODOW FROM demand_date) IN (6, 7) THEN TRUE
        ELSE FALSE
    END AS is_weekend
FROM transport.v_daily_demand
GROUP BY demand_date, city;

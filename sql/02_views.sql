-- ---------------------------------------------------------------------
-- Stage 1 analytical views built from PostgreSQL source tables
-- ---------------------------------------------------------------------

CREATE SCHEMA IF NOT EXISTS transport;

-- Remove legacy placeholder objects from earlier local-file-first versions.
DROP VIEW IF EXISTS transport.v_city_structure_source CASCADE;
DROP VIEW IF EXISTS transport.v_contributor_source CASCADE;
DROP VIEW IF EXISTS transport.v_paris_hourly_profile CASCADE;
DROP VIEW IF EXISTS transport.v_nyc_hourly_profile CASCADE;
DROP VIEW IF EXISTS transport.v_daily_demand_enriched CASCADE;
DROP VIEW IF EXISTS transport.v_daily_demand CASCADE;
DROP VIEW IF EXISTS transport.fact_demand CASCADE;
DROP TABLE IF EXISTS transport.fact_demand CASCADE;
DROP TABLE IF EXISTS transport.dim_calendar CASCADE;
DROP TABLE IF EXISTS transport.dim_weather CASCADE;

-- Canonical station-grain demand facts, derived directly from PostgreSQL
-- source tables. Paris is restricted to station entities only so later
-- contributor comparisons remain comparable with NYC stations.
CREATE VIEW transport.fact_demand AS
WITH paris_station_daily AS (
    SELECT
        d.service_date AS demand_date,
        'Paris'::text AS city,
        'Ile-de-France'::text AS region,
        COALESCE(NULLIF(n.id_refa_lda, ''), n.network_id::text) AS location_id,
        n.network_name AS location_name,
        'validations'::text AS metric_type,
        SUM(d.nb_validations)::numeric AS value,
        'idfm_station_daily'::text AS source
    FROM public.idfm_daily_validations d
    JOIN public.idfm n
        ON n.network_id = d.network_id
    WHERE n.network_type = 'station'
      AND d.service_date IS NOT NULL
      AND d.nb_validations IS NOT NULL
    GROUP BY
        d.service_date,
        COALESCE(NULLIF(n.id_refa_lda, ''), n.network_id::text),
        n.network_name
), nyc_station_daily AS (
    SELECT
        h.transit_date_local AS demand_date,
        'NYC'::text AS city,
        COALESCE(m.borough, 'NYC')::text AS region,
        h.station_id::text AS location_id,
        COALESCE(m.station_name, h.station_id)::text AS location_name,
        'ridership'::text AS metric_type,
        SUM(h.ridership)::numeric AS value,
        'mta_station_daily'::text AS source
    FROM public.mta_hourly_ridership h
    LEFT JOIN public.mta m
        ON m.station_id = h.station_id
    WHERE h.transit_date_local IS NOT NULL
      AND h.ridership IS NOT NULL
    GROUP BY
        h.transit_date_local,
        COALESCE(m.borough, 'NYC')::text,
        h.station_id::text,
        COALESCE(m.station_name, h.station_id)::text
)
SELECT *
FROM paris_station_daily
UNION ALL
SELECT *
FROM nyc_station_daily;

-- Daily demand aggregated from the canonical fact demand view.
CREATE VIEW transport.v_daily_demand AS
SELECT
    demand_date,
    city,
    region,
    source,
    metric_type,
    SUM(value) AS total_value
FROM transport.fact_demand
GROUP BY demand_date, city, region, source, metric_type;

-- NYC hourly ridership profile derived from hourly source truth.
CREATE VIEW transport.v_nyc_hourly_profile AS
SELECT
    COALESCE(m.borough, 'NYC')::text AS region,
    EXTRACT(HOUR FROM h.transit_local_hour)::integer AS hour,
    LPAD(EXTRACT(HOUR FROM h.transit_local_hour)::integer::text, 2, '0') || ':00' AS hour_label,
    SUM(h.ridership)::numeric AS hourly_total
FROM public.mta_hourly_ridership h
LEFT JOIN public.mta m
    ON m.station_id = h.station_id
WHERE h.transit_local_hour IS NOT NULL
  AND h.ridership IS NOT NULL
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
SELECT
    city,
    region,
    source,
    metric_type,
    location_id,
    location_name,
    SUM(value) AS total_value
FROM transport.fact_demand
GROUP BY city, region, source, metric_type, location_id, location_name;

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

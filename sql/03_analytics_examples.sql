-- ---------------------------------------------------------------------
-- Example analytics queries for the PostgreSQL-first contract
-- ---------------------------------------------------------------------

-- 1) Canonical fact demand filter.
SELECT *
FROM transport.fact_demand
WHERE demand_date >= DATE '2024-01-01'
  AND city = 'Paris';

-- 2) Daily demand by source and city.
SELECT
    city,
    source,
    metric_type,
    COUNT(*) AS day_rows,
    SUM(total_value) AS summed_daily_value,
    AVG(total_value) AS avg_daily_value
FROM transport.v_daily_demand
GROUP BY city, source, metric_type
ORDER BY summed_daily_value DESC;

-- 3) Rolling average with a window function.
SELECT
    demand_date,
    city,
    source,
    metric_type,
    total_value,
    AVG(total_value) OVER (
        PARTITION BY city, source, metric_type
        ORDER BY demand_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS rolling_7_avg
FROM transport.v_daily_demand
ORDER BY city, source, metric_type, demand_date;

-- 4) Top contributors across both cities.
SELECT
    city,
    source,
    location_name,
    total_value
FROM transport.v_contributor_source
ORDER BY total_value DESC
LIMIT 20;

-- 5) Paris vs NYC structural comparison.
SELECT
    city,
    AVG(total_value) AS avg_daily_value,
    STDDEV_POP(total_value) AS std_daily_value,
    STDDEV_POP(total_value) / NULLIF(AVG(total_value), 0) AS coeff_variation,
    AVG(CASE WHEN is_weekend THEN total_value END)
        / NULLIF(AVG(CASE WHEN NOT is_weekend THEN total_value END), 0) AS weekend_weekday_ratio
FROM transport.v_city_structure_source
GROUP BY city
ORDER BY city;

-- 6) NYC hourly ridership profile.
SELECT
    region,
    hour,
    hourly_total
FROM transport.v_nyc_hourly_profile
ORDER BY region, hour;

-- 7) Paris hourly validation-share profile.
SELECT
    day_category,
    hour_bin,
    validation_share_pct
FROM transport.v_paris_hourly_profile
ORDER BY day_category, hour_bin;

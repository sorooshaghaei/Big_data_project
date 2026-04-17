-- example queries for the project

-- shows sample fact demand rows
SELECT *
FROM transport.fact_demand
WHERE demand_date >= DATE '2024-01-01'
  AND city = 'Paris';

-- sums daily demand by city and source
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

-- adds a rolling 7 day average
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

-- shows the biggest contributors
SELECT
    city,
    source,
    location_name,
    total_value
FROM transport.v_contributor_source
ORDER BY total_value DESC
LIMIT 20;

-- compares city level metrics
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

-- shows the nyc hourly profile
SELECT
    region,
    hour,
    hourly_total
FROM transport.v_nyc_hourly_profile
ORDER BY region, hour;

-- shows the paris hourly profile
SELECT
    day_category,
    hour_bin,
    validation_share_pct
FROM transport.v_paris_hourly_profile
ORDER BY day_category, hour_bin;

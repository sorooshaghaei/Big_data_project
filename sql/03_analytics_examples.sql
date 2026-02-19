-- ---------------------------------------------------------------------
-- Example analytics queries for learning and validation
-- ---------------------------------------------------------------------

-- 1) Basic filter query (date + region).
SELECT *
FROM transport.fact_demand
WHERE demand_date >= DATE '2024-01-01'
  AND region = 'Ile-de-France';

-- 2) Aggregation with grouping.
SELECT
    region,
    metric_type,
    COUNT(*) AS rows_count,
    SUM(value) AS total_value,
    AVG(value) AS avg_value
FROM transport.fact_demand
GROUP BY region, metric_type
ORDER BY total_value DESC;

-- 3) INNER JOIN example (keep only dates present in both tables).
SELECT
    d.demand_date,
    d.region,
    d.total_value,
    c.is_holiday
FROM transport.v_daily_demand d
INNER JOIN transport.dim_calendar c
    ON d.demand_date = c.calendar_date;

-- 4) LEFT JOIN example (keep all demand rows, even if no weather row).
SELECT
    d.demand_date,
    d.region,
    d.total_value,
    w.mean_temp_c,
    w.precip_mm
FROM transport.v_daily_demand d
LEFT JOIN transport.dim_weather w
    ON d.demand_date = w.weather_date
   AND d.region = w.region;

-- 5) Rolling average with window function.
SELECT
    demand_date,
    region,
    metric_type,
    SUM(value) AS daily_value,
    AVG(SUM(value)) OVER (
        PARTITION BY region, metric_type
        ORDER BY demand_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS rolling_7_avg
FROM transport.fact_demand
GROUP BY demand_date, region, metric_type;

-- 6) CTE-based anomaly marker (z-score threshold).
WITH daily AS (
    SELECT
        demand_date,
        region,
        metric_type,
        SUM(value) AS daily_value
    FROM transport.fact_demand
    GROUP BY demand_date, region, metric_type
), scored AS (
    SELECT
        demand_date,
        region,
        metric_type,
        daily_value,
        AVG(daily_value) OVER (PARTITION BY region, metric_type) AS mean_value,
        STDDEV_POP(daily_value) OVER (PARTITION BY region, metric_type) AS std_value
    FROM daily
)
SELECT
    demand_date,
    region,
    metric_type,
    daily_value,
    CASE
        WHEN std_value = 0 THEN 0
        WHEN ABS((daily_value - mean_value) / std_value) >= 2.5 THEN 1
        ELSE 0
    END AS is_anomaly
FROM scored
ORDER BY demand_date;

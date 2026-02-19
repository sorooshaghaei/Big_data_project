-- ---------------------------------------------------------------------
-- Analytical views
-- ---------------------------------------------------------------------

-- Daily demand aggregated from the raw fact table.
CREATE OR REPLACE VIEW transport.v_daily_demand AS
SELECT
    demand_date,
    region,
    source,
    metric_type,
    SUM(value) AS total_value
FROM transport.fact_demand
GROUP BY demand_date, region, source, metric_type;

-- Daily demand enriched with calendar and weather context.
CREATE OR REPLACE VIEW transport.v_daily_demand_enriched AS
SELECT
    d.demand_date,
    d.region,
    d.source,
    d.metric_type,
    d.total_value,
    c.day_of_week,
    c.is_weekend,
    c.is_holiday,
    c.holiday_name,
    w.mean_temp_c,
    w.precip_mm
FROM transport.v_daily_demand d
LEFT JOIN transport.dim_calendar c
    ON d.demand_date = c.calendar_date
LEFT JOIN transport.dim_weather w
    ON d.demand_date = w.weather_date
   AND d.region = w.region;

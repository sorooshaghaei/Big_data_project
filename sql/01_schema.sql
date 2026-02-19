-- ---------------------------------------------------------------------
-- Core schema for transport analytics
-- ---------------------------------------------------------------------

-- Create dedicated namespace so transport objects are isolated.
CREATE SCHEMA IF NOT EXISTS transport;

-- ---------------------------------------------------------------------
-- Fact table: one row per observed metric event/value
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS transport.fact_demand (
    demand_id BIGSERIAL PRIMARY KEY,
    demand_date DATE NOT NULL,
    region TEXT NOT NULL,
    location_id TEXT,
    location_name TEXT,
    metric_type TEXT NOT NULL,
    value NUMERIC NOT NULL,
    source TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes supporting common analytics filters/grouping.
CREATE INDEX IF NOT EXISTS idx_fact_demand_date ON transport.fact_demand (demand_date);
CREATE INDEX IF NOT EXISTS idx_fact_demand_region ON transport.fact_demand (region);
CREATE INDEX IF NOT EXISTS idx_fact_demand_metric ON transport.fact_demand (metric_type);
CREATE INDEX IF NOT EXISTS idx_fact_demand_source ON transport.fact_demand (source);

-- ---------------------------------------------------------------------
-- Calendar dimension: joins for weekday/holiday seasonality analysis
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS transport.dim_calendar (
    calendar_date DATE PRIMARY KEY,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    is_weekend BOOLEAN NOT NULL,
    is_holiday BOOLEAN,
    holiday_name TEXT
);

-- ---------------------------------------------------------------------
-- Weather dimension: joins for weather-demand effect analysis
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS transport.dim_weather (
    weather_id BIGSERIAL PRIMARY KEY,
    weather_date DATE NOT NULL,
    region TEXT NOT NULL,
    mean_temp_c NUMERIC,
    precip_mm NUMERIC,
    wind_kmh NUMERIC,
    source TEXT,
    UNIQUE (weather_date, region)
);

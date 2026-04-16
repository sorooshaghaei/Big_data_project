-- ==============================================================================
-- MTA TRANSPORT DATABASE
-- ==============================================================================


-- ==========================================
-- 1. TABLE: mta (NY MTA subway stations)
-- ==========================================
CREATE TABLE mta (
    station_id TEXT PRIMARY KEY,
    station_name TEXT NOT NULL,
    borough TEXT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION
);

-- ==========================================
-- 2. TABLE: mta_hourly_ridership
-- PK: surrogate id , FK: station_id -> mta
-- ==========================================
CREATE TABLE mta_hourly_ridership (
    id                  BIGINT GENERATED ALWAYS AS IDENTITY,
    station_id          TEXT NOT NULL,
    transit_local_hour  TIMESTAMPTZ NOT NULL,
    transit_date_local  DATE NOT NULL,
    payment_method      TEXT,
    fare_class_category TEXT,
    transit_mode        TEXT,
    ridership           INTEGER NOT NULL DEFAULT 0,
    transfers           INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (id, transit_date_local)
) PARTITION BY RANGE (transit_date_local);

ALTER TABLE mta_hourly_ridership
    ADD CONSTRAINT fk_mta_station FOREIGN KEY (station_id) REFERENCES mta(station_id) ON DELETE CASCADE;

CREATE INDEX idx_mta_hourly_ridership_station_id ON mta_hourly_ridership(station_id);
CREATE INDEX idx_mta_hourly_ridership_transit_hour ON mta_hourly_ridership(transit_local_hour);
CREATE INDEX idx_mta_hourly_ridership_transit_date ON mta_hourly_ridership(transit_date_local);

-- Create Partitions from 2020-2026
CREATE TABLE mta_hourly_2020 PARTITION OF mta_hourly_ridership FOR VALUES FROM ('2020-01-01') TO ('2021-01-01');
CREATE TABLE mta_hourly_2021 PARTITION OF mta_hourly_ridership FOR VALUES FROM ('2021-01-01') TO ('2022-01-01');
CREATE TABLE mta_hourly_2022 PARTITION OF mta_hourly_ridership FOR VALUES FROM ('2022-01-01') TO ('2023-01-01');
CREATE TABLE mta_hourly_2023 PARTITION OF mta_hourly_ridership FOR VALUES FROM ('2023-01-01') TO ('2024-01-01');
CREATE TABLE mta_hourly_2024 PARTITION OF mta_hourly_ridership FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
CREATE TABLE mta_hourly_2025 PARTITION OF mta_hourly_ridership FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');
CREATE TABLE mta_hourly_2026 PARTITION OF mta_hourly_ridership FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');

-- Create a fallback partition for records with invalid date data.
CREATE TABLE mta_hourly_default PARTITION OF mta_hourly_ridership DEFAULT;


-- ==============================================================================
-- IDFM TRANSPORT DATABASE
-- ==============================================================================

-- ==========================================
-- 1. TABLE: idfm
-- ==========================================
CREATE TABLE idfm (
    network_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    network_name TEXT NOT NULL,
    network_type TEXT NOT NULL,         -- 'station' or 'line'
    cod_stif_trns TEXT,
    cod_stif_res TEXT,
    cod_stif TEXT,
    id_refa_lda TEXT
);

-- ==========================================
-- 2. TABLE: idfm_daily_validations
-- ==========================================
CREATE TABLE idfm_daily_validations (
    id BIGINT GENERATED ALWAYS AS IDENTITY,
    network_id BIGINT NOT NULL,
    service_date DATE NOT NULL,
    fare_category TEXT NOT NULL,
    nb_validations INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (id, service_date)
) PARTITION BY RANGE (service_date);

-- Add Foreign Key for Partition table
ALTER TABLE idfm_daily_validations
    ADD CONSTRAINT fk_network FOREIGN KEY (network_id) REFERENCES idfm(network_id) ON DELETE CASCADE;

CREATE INDEX idx_idfm_daily_validations_network ON idfm_daily_validations(network_id);
CREATE INDEX idx_idfm_daily_validations_date ON idfm_daily_validations(service_date);

-- Create Partitions 2015-2026
CREATE TABLE idfm_daily_2015 PARTITION OF idfm_daily_validations FOR VALUES FROM ('2015-01-01') TO ('2016-01-01');
CREATE TABLE idfm_daily_2016 PARTITION OF idfm_daily_validations FOR VALUES FROM ('2016-01-01') TO ('2017-01-01');
CREATE TABLE idfm_daily_2017 PARTITION OF idfm_daily_validations FOR VALUES FROM ('2017-01-01') TO ('2018-01-01');
CREATE TABLE idfm_daily_2018 PARTITION OF idfm_daily_validations FOR VALUES FROM ('2018-01-01') TO ('2019-01-01');
CREATE TABLE idfm_daily_2019 PARTITION OF idfm_daily_validations FOR VALUES FROM ('2019-01-01') TO ('2020-01-01');
CREATE TABLE idfm_daily_2020 PARTITION OF idfm_daily_validations FOR VALUES FROM ('2020-01-01') TO ('2021-01-01');
CREATE TABLE idfm_daily_2021 PARTITION OF idfm_daily_validations FOR VALUES FROM ('2021-01-01') TO ('2022-01-01');
CREATE TABLE idfm_daily_2022 PARTITION OF idfm_daily_validations FOR VALUES FROM ('2022-01-01') TO ('2023-01-01');
CREATE TABLE idfm_daily_2023 PARTITION OF idfm_daily_validations FOR VALUES FROM ('2023-01-01') TO ('2024-01-01');
CREATE TABLE idfm_daily_2024 PARTITION OF idfm_daily_validations FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
CREATE TABLE idfm_daily_2025 PARTITION OF idfm_daily_validations FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');
CREATE TABLE idfm_daily_2026 PARTITION OF idfm_daily_validations FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');

-- Create a fallback partition for records with invalid date data.
CREATE TABLE idfm_daily_default PARTITION OF idfm_daily_validations DEFAULT;

-- ==========================================
-- 3. TABLE: idfm_hourly_profiles
-- ==========================================
CREATE TABLE idfm_hourly_profiles (
    id BIGINT GENERATED ALWAYS AS IDENTITY,
    network_id BIGINT NOT NULL,
    day_type TEXT NOT NULL,
    hour_slot TEXT NOT NULL,
    pct_validations NUMERIC(6,2) NOT NULL,
    period_label TEXT NOT NULL,
    PRIMARY KEY (id, period_label)
) PARTITION BY LIST (period_label);

ALTER TABLE idfm_hourly_profiles
    ADD CONSTRAINT fk_network_hourly FOREIGN KEY (network_id) REFERENCES idfm(network_id) ON DELETE CASCADE;

CREATE INDEX idx_idfm_hourly_profiles_network ON idfm_hourly_profiles(network_id);

-- Create Partitions 2015-2026
CREATE TABLE idfm_hourly_2015 PARTITION OF idfm_hourly_profiles FOR VALUES IN ('2015S1', '2015S2', '2015');
CREATE TABLE idfm_hourly_2016 PARTITION OF idfm_hourly_profiles FOR VALUES IN ('2016S1', '2016S2', '2016');
CREATE TABLE idfm_hourly_2017 PARTITION OF idfm_hourly_profiles FOR VALUES IN ('2017S1', '2017S2', '2017');
CREATE TABLE idfm_hourly_2018 PARTITION OF idfm_hourly_profiles FOR VALUES IN ('2018S1', '2018S2', '2018');
CREATE TABLE idfm_hourly_2019 PARTITION OF idfm_hourly_profiles FOR VALUES IN ('2019S1', '2019S2', '2019');
CREATE TABLE idfm_hourly_2020 PARTITION OF idfm_hourly_profiles FOR VALUES IN ('2020S1', '2020S2', '2020');
CREATE TABLE idfm_hourly_2021 PARTITION OF idfm_hourly_profiles FOR VALUES IN ('2021S1', '2021S2', '2021');
CREATE TABLE idfm_hourly_2022 PARTITION OF idfm_hourly_profiles FOR VALUES IN ('2022S1', '2022S2', '2022');
CREATE TABLE idfm_hourly_2023 PARTITION OF idfm_hourly_profiles FOR VALUES IN ('2023S1', '2023S2', '2023');
CREATE TABLE idfm_hourly_2024 PARTITION OF idfm_hourly_profiles FOR VALUES IN ('2024S1', '2024S2', '2024');
CREATE TABLE idfm_hourly_2025 PARTITION OF idfm_hourly_profiles FOR VALUES IN ('2025S1', '2025S2', '2025');
CREATE TABLE idfm_hourly_2026 PARTITION OF idfm_hourly_profiles FOR VALUES IN ('2026S1', '2026S2', '2026');

-- Create a fallback partition for records with invalid date data.
CREATE TABLE idfm_hourly_default PARTITION OF idfm_hourly_profiles DEFAULT;

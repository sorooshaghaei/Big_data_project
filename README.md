# Big_data_project

This repository contains our Big Data course project on **public transport smart-card usage / ridership**.
Goal: build a **reproducible pipeline** that
- aggregates raw validations/entries into a clean time-series fact table
- forecasts passenger traffic for future time slots (hour/day)
- detects **peak periods** (rush hours) and **abnormal surges** (events, disruptions)

Traffic in this project means **validations / entries / ridership counts**, not road traffic speed.

# Datasets

Main dataset (hourly, best for peak detection):
- MTA Subway Hourly Ridership (2020–2024)
  https://data.ny.gov/Transportation/MTA-Subway-Hourly-Ridership-2020-2024/wujg-7c2s  
  CSV download:
  https://data.ny.gov/api/views/wujg-7c2s/rows.csv?accessType=DOWNLOAD

Secondary datasets (daily, good for weekly seasonality / abnormal days):
- Île-de-France Mobilités — Validations sur le réseau de surface (1er trimestre)
  https://data.iledefrance-mobilites.fr/explore/dataset/validations-reseau-surface-nombre-validations-par-jour-1er-trimestre/

- Kaggle — Public transport traffic data in France
  https://www.kaggle.com/datasets/gatandubuc/public-transport-traffic-data-in-france

## What to look for in datasets (selection criteria)?

We should prioritize datasets that clearly contain:
- a timestamp (date or datetime)
- a location identifier (station / station complex / stop / line / zone)
- a count (entries / validations / ridership)

Best-case: hourly data per station (ideal for peak detection).
Acceptable: daily data per station/line across multiple years.

Avoid:
- PDF-only “reports” without raw tables
- network/topology datasets without time-series counts
- road traffic speed/sensor datasets (not our definition of traffic)

## Bibliography

Highly relevant (forecasting / peaks):
- Lablack et al. (2019) ASTIR: Spatio-Temporal Data Mining for Crowd Flow Prediction
  https://ieeexplore.ieee.org/document/8889654
- Kolios et al. (2023) Model-Adaptive Event Triggering for Monitoring Recurrent Mobility Patterns in Public Transport
  https://www.researchgate.net/publication/367633240_Model-Adaptive_Event_Triggering_for_Monitoring_Recurrent_Mobility_Patterns_in_Public_Transport

Useful background (patterns / clustering / smart-card mining):
- Aghabozorgi et al. (2015) Time-series clustering – A decade review
  https://www.researchgate.net/publication/276075711_Time-series_clustering_-_A_decade_review
- Ma et al. (2013) Mining Smart Card Data for Transit Riders’ Travel Patterns
  https://doi.org/10.1016/j.trc.2013.07.010
- Cats (2022) Identifying Human Mobility Patterns Using Smart Card Data
  https://arxiv.org/abs/2208.05352
  
# Authors

Nguyễn Hồ Bảo Khánh, Maksym DOLHOV, Mehdi AGHAEI and Nima DAVARI

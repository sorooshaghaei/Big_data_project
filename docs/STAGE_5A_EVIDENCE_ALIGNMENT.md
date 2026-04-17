# Stage 5A Evidence And Citation Alignment

This document closes `Stage 5A` using static validation only. It maps the
current paper claims in
[`report/transport_analytics_compendium.tex`](../report/transport_analytics_compendium.tex)
to the generated result artifacts under `report/results/` and to the cited
literature already stored in `docs/papers/`.

This note records the result artifacts used for the final paper. Some clean
checkouts may keep the `report/results/` folder structure without committing
every generated csv or json file.

## Quantitative claim map

| Paper claim | Paper location | Evidence file | Evidence |
| --- | --- | --- | --- |
| The workflow produces `12,696` daily observations and `2,003` contributor-level rows. | Abstract, lines 40-41 | `report/results/analysis_summary.json` | `daily_rows = 12696`, `station_fact_rows = 2003` |
| Overall forecasting MAPE is `6.02%`. | Abstract line 42; Forecasting section lines 456-459 | `report/results/forecast_metrics_overall.csv` | `mape = 0.06022102893542031` |
| NYC forecasting MAPE is `5.86%`; Paris forecasting MAPE is `6.94%`. | Abstract lines 42-43; Table 5, lines 462-474; synthesis table lines 622-623 | `report/results/forecast_metrics_by_city.csv` | NYC `0.05861863055976122`, Paris `0.0693919881923371` |
| Paris anomaly rate is `8.96%`; NYC anomaly rate is `0.73%`. | Abstract lines 43-45; anomaly section lines 500-525; synthesis table line 624 | `report/results/anomaly_rates.csv` | NYC `0.007334428024083197`, Paris `0.08958157820836844` |
| Paris average daily demand is about `4.13M`; NYC average daily demand is about `2.63M`. | Abstract lines 45-47; city-structure section lines 536-556; synthesis table line 622 | `report/results/city_structure_summary.csv` | NYC `2628716.4313`, Paris `4127083.0070` |
| Paris weekend/weekday ratio is `0.512`; NYC ratio is `0.584`. | City-structure section lines 544-560 | `report/results/city_structure_summary.csv` | NYC `0.5843825294826577`, Paris `0.5118997052819414` |
| NYC peak month is `2`; Paris peak month is `10`. | Table 7, lines 544-556 | `report/results/city_structure_summary.csv` | NYC `peak_month = 2.0`, Paris `peak_month = 10.0` |
| NYC covers `2020--2024`; Paris covers `2015--2024`; Paris `2025` is excluded. | Data section lines 167-174; Temporal section lines 402-404 | `report/results/temporal_yearly_totals.csv` | NYC years `2020-2024`; Paris years `2015-2024`; no Paris `2025` row |
| NYC total is `643.3M` in 2020, `1,163.3M` in 2023, `1,211.5M` in 2024. | Table 4, lines 429-441 | `report/results/temporal_yearly_totals.csv` | NYC totals `643310841`, `1163346962`, `1211512903` |
| Paris total is `926.0M` in 2020, `1,729.7M` in 2023, `1,024.2M` in 2024. | Table 4, lines 429-441 | `report/results/temporal_yearly_totals.csv` | Paris totals `926003724`, `1729743023`, `1024228946` |
| Forecast split uses `8,336` train rows and `4,276` test rows. | Forecasting section lines 456-458 | `report/results/forecast_metrics_overall.csv` | `train_rows = 8336`, `test_rows = 4276` |
| Overall forecast MAE is `52,909`; RMSE is `156,343`. | Forecasting section lines 457-458 | `report/results/forecast_metrics_overall.csv` | `mae = 52908.8475`, `rmse = 156343.1312` |
| NYC MAE is `29,402`; Paris MAE is `187,446`. | Table 5, lines 462-474 | `report/results/forecast_metrics_by_city.csv` | NYC `29401.7626`, Paris `187446.2521` |
| Top contributors include Saint-Lazare and Times Sq--42 St. | Contributors section lines 564-586; synthesis table line 625 | `report/results/top_contributors.csv` | `SAINT-LAZARE = 432319111`, `Times Sq-42 St ... = 168202157` |

## Literature claim map

| Literature use in paper | Paper location | Citation key | Source in `docs/papers/` |
| --- | --- | --- | --- |
| Smart-card data supports pattern discovery and rider analysis. | Related Work lines 93-102 | `ma2013smartcard`, `long2015jobs`, `cats2022mobility` | `docs/papers/DOLHOV/Mining smart card data for transit riders.pdf`, `docs/papers/DOLHOV/Combining smart card data and household travel survey_compressed.pdf`, `docs/papers/DOLHOV/Identifying Human Mobility Patterns using Smart Card Data.pdf` |
| Topic-modeling and network analysis can reveal richer mobility structure. | Related Work lines 104-111 | `aminpour2024mobility`, `sun2025network` | `docs/papers/KHANH/Unveiling mobility patterns_compressed.pdf`, `docs/papers/KHANH/Optimizing Urban Mobility_compressed.pdf` |
| Graph and spatio-temporal forecasting methods are stronger but heavier than the baseline used here. | Related Work lines 113-122; limitations line 661 | `xie2022graph`, `lablack2019astir` | `docs/papers/DAVARI/2204.02650v1.pdf`, `docs/papers/AGHAEI/ASTIR_Spatio-Temporal_Data_Mining_for_Crowd_Flow_Prediction_compressed.pdf` |
| Event-triggering and monitoring literature motivates anomaly screening. | Related Work lines 124-130 | `kolios2023monitoring` | `docs/papers/AGHAEI/Model-Adaptive_Event_Triggering_for_Monitoring_Recurrent_Mobility_Patterns_in_Public_Transport.pdf` |
| Factor/ridership and socio-economic inference papers mark the boundary of what this project does not attempt. | Related Work lines 132-140 | `he2018ridership`, `chen2025trip`, `kundu2025line` | `docs/papers/DAVARI/AnAnalysisofFactorsInfluencingMetroStation.pdf`, `docs/papers/KHANH/A Two-Stage Trip Inference Model.pdf`, `docs/papers/KHANH/Benefits from a new transit line_compressed.pdf` |

## Support and originality review

### Quantitative support

- All numerical claims checked in the abstract, methods, results, and summary
  tables are traceable to files already present in `report/results/`.
- No quantitative claim reviewed in the paper depends on live PostgreSQL access
  or on a notebook-only intermediate state.
- The paper’s figure references match files present under `report/figures/`:
  - `workflow_diagram.png`
  - `temporal_profiles.png`
  - `forecast_performance.png`
  - `anomalies_and_contributors.png`
  - `city_structure.png`

### Citation support

- Each related-work paragraph uses concrete citations instead of referencing the
  `docs/papers/` directory generically.
- The bibliography entries in the paper correspond to documents already listed
  in `docs/papers/citations.txt` and present in the `docs/papers/` tree.

### Originality review

- The current paper does not contain placeholder references like “Project
  background papers stored under `docs/papers/`.”
- The current paper does not contain stale weather or synthetic-weather
  workflow language.
- A static read-through of the paper did not reveal copied dataset descriptions
  or copied section framing from the local bibliography notes.
- The related-work section is written as a synthesis tied to this project’s
  method choices, not as pasted paper abstracts.

## Stage 5A outcome

`Stage 5A` can be treated as complete from the current static repository state.

What remains after Stage 5A:

- `Stage 6`: formal cleanup confirmation
- `Stage 7`: final submission-readiness validation using existing repo files

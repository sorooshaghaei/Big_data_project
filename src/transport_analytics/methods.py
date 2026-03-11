# Mehdi AGHAEI

"""Stage 1 and Stage 2 analytical methods for the transport project."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .context import infer_city
from .pipeline import PipelineArtifacts


@dataclass
class StageMethod:
    question: str
    method_name: str
    method_family: str
    inputs: str
    outputs: str
    selected: bool = True


def _ensure_dirs(root: Path) -> tuple[Path, Path]:
    results_dir = root / "report" / "results"
    figures_dir = root / "report" / "figures"
    results_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)
    return results_dir, figures_dir


def stage_one_plan() -> pd.DataFrame:
    """Return the Stage 1 method selection table."""
    methods = [
        StageMethod(
            question="How does ridership vary by hour/day/month/year?",
            method_name="Temporal profiling",
            method_family="Descriptive analytics",
            inputs="Daily fact table + hourly profiles",
            outputs="Weekday, monthly, yearly, and hourly summaries",
        ),
        StageMethod(
            question="What is the impact of weather conditions on ridership?",
            method_name="Weather sensitivity regression",
            method_family="Statistical learning",
            inputs="Enriched daily table with weather and calendar context",
            outputs="Correlation table and regression coefficients",
        ),
        StageMethod(
            question="Can we predict future ridership levels?",
            method_name="Lag-based random forest forecasting",
            method_family="Machine learning",
            inputs="Time features, rolling features, and weather context",
            outputs="Holdout predictions and forecast metrics",
        ),
        StageMethod(
            question="Are there anomalies or unusual spikes in validations?",
            method_name="Hybrid anomaly detection",
            method_family="Unsupervised learning + statistics",
            inputs="Daily fact features and rolling z-scores",
            outputs="Anomaly flags and anomaly-rate summary",
        ),
        StageMethod(
            question="Which stations or lines contribute most, and how do Paris and NYC differ structurally?",
            method_name="Contribution ranking and city comparison",
            method_family="Comparative analytics",
            inputs="Station fact table + city-level aggregates",
            outputs="Top contributors and structural comparison table",
        ),
    ]
    return pd.DataFrame([asdict(item) for item in methods])


def temporal_profile_method(artifacts: PipelineArtifacts, results_dir: Path, figures_dir: Path) -> dict[str, pd.DataFrame]:
    """Summarize demand variation by day, month, year, and hour."""
    enriched = artifacts.enriched.copy()
    enriched["city"] = infer_city(enriched["region"])

    weekday_profile = (
        enriched.groupby(["city", "source", "metric_type", "day_of_week"], as_index=False)["value"]
        .mean()
        .rename(columns={"value": "avg_value"})
    )
    monthly_profile = (
        enriched.groupby(["city", "source", "metric_type", "month"], as_index=False)["value"]
        .mean()
        .rename(columns={"value": "avg_value"})
    )
    yearly_totals = (
        enriched.groupby(["city", "source", "metric_type", "year"], as_index=False)["value"]
        .sum()
        .rename(columns={"value": "total_value"})
    )

    nyc_hourly = artifacts.mta_hourly_profile.copy()
    if not nyc_hourly.empty:
        nyc_hourly["city"] = "NYC"
        nyc_hourly = (
            nyc_hourly.groupby(["city", "hour", "hour_label"], as_index=False)["value"]
            .sum()
            .rename(columns={"value": "hourly_total"})
        )

    paris_hourly = artifacts.paris_hourly_profile.copy()
    if not paris_hourly.empty:
        paris_hourly["city"] = "Paris"

    weekday_profile.to_csv(results_dir / "temporal_weekday_profile.csv", index=False)
    monthly_profile.to_csv(results_dir / "temporal_monthly_profile.csv", index=False)
    yearly_totals.to_csv(results_dir / "temporal_yearly_totals.csv", index=False)
    nyc_hourly.to_csv(results_dir / "temporal_nyc_hourly_profile.csv", index=False)
    paris_hourly.to_csv(results_dir / "temporal_paris_hourly_profile.csv", index=False)

    return {
        "weekday_profile": weekday_profile,
        "monthly_profile": monthly_profile,
        "yearly_totals": yearly_totals,
        "nyc_hourly": nyc_hourly,
        "paris_hourly": paris_hourly,
    }


def weather_impact_method(artifacts: PipelineArtifacts, results_dir: Path, figures_dir: Path) -> dict[str, pd.DataFrame]:
    """Estimate weather-demand relationships on city-level totals."""
    enriched = artifacts.enriched.copy()
    enriched["city"] = infer_city(enriched["region"])

    city_daily = (
        enriched.groupby(["date", "city"], as_index=False)
        .agg(
            total_value=("value", "sum"),
            mean_temp_c=("mean_temp_c", "mean"),
            precip_mm=("precip_mm", "mean"),
            wind_kmh=("wind_kmh", "mean"),
            is_weekend=("is_weekend", "max"),
            month=("month", "first"),
        )
        .dropna(subset=["mean_temp_c", "precip_mm", "wind_kmh"])
    )

    coef_rows: list[dict] = []
    corr_rows: list[dict] = []
    predictors = ["mean_temp_c", "precip_mm", "wind_kmh", "is_weekend", "month"]

    for city, city_df in city_daily.groupby("city"):
        if len(city_df) < 10:
            continue
        X = city_df[predictors]
        y = np.log1p(city_df["total_value"])
        model = LinearRegression()
        model.fit(X, y)
        preds = model.predict(X)
        coef_rows.append(
            {
                "city": city,
                "intercept": float(model.intercept_),
                "r2_in_sample": float(model.score(X, y)),
                **{name: float(value) for name, value in zip(predictors, model.coef_, strict=True)},
            }
        )
        corr_rows.append(
            {
                "city": city,
                "corr_temp": float(city_df["total_value"].corr(city_df["mean_temp_c"])),
                "corr_precip": float(city_df["total_value"].corr(city_df["precip_mm"])),
                "corr_wind": float(city_df["total_value"].corr(city_df["wind_kmh"])),
                "row_count": int(len(city_df)),
                "mae_log": float(mean_absolute_error(y, preds)),
            }
        )

    coefficients = pd.DataFrame(coef_rows)
    correlations = pd.DataFrame(corr_rows)
    coefficients.to_csv(results_dir / "weather_regression_coefficients.csv", index=False)
    correlations.to_csv(results_dir / "weather_correlations.csv", index=False)

    return {"coefficients": coefficients, "correlations": correlations}


def forecasting_method(artifacts: PipelineArtifacts, results_dir: Path, figures_dir: Path) -> dict[str, pd.DataFrame]:
    """Train a lag-based random forest forecasting baseline."""
    df = artifacts.enriched.copy()
    df["city"] = infer_city(df["region"])

    feature_cols = [
        "lag_1",
        "lag_7",
        "lag_14",
        "rolling_7_mean",
        "rolling_7_std",
        "rolling_30_mean",
        "rolling_30_std",
        "pct_change_1",
        "day_of_week",
        "month",
        "is_weekend",
        "mean_temp_c",
        "precip_mm",
        "wind_kmh",
    ]
    cat_cols = ["region", "source", "metric_type"]
    model_df = df.dropna(subset=["value", "date", *feature_cols]).copy()

    unique_dates = sorted(model_df["date"].drop_duplicates())
    split_index = max(1, int(len(unique_dates) * 0.8))
    cutoff = unique_dates[split_index - 1]

    train = model_df[model_df["date"] <= cutoff].copy()
    test = model_df[model_df["date"] > cutoff].copy()
    if test.empty:
        raise ValueError("Forecasting split produced an empty test set.")

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", Pipeline([("imputer", SimpleImputer(strategy="median"))]), feature_cols),
            ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
        ]
    )
    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "regressor",
                RandomForestRegressor(
                    n_estimators=220,
                    random_state=42,
                    n_jobs=-1,
                    min_samples_leaf=2,
                ),
            ),
        ]
    )
    model.fit(train[feature_cols + cat_cols], train["value"])
    test = test.copy()
    test["prediction"] = model.predict(test[feature_cols + cat_cols])
    test["abs_pct_error"] = np.where(test["value"] == 0, np.nan, (test["prediction"] - test["value"]).abs() / test["value"])

    overall_metrics = pd.DataFrame(
        [
            {
                "split_cutoff_date": str(cutoff.date()),
                "mae": float(mean_absolute_error(test["value"], test["prediction"])),
                "rmse": float(np.sqrt(mean_squared_error(test["value"], test["prediction"]))),
                "mape": float(np.nanmean(test["abs_pct_error"])),
                "train_rows": int(len(train)),
                "test_rows": int(len(test)),
            }
        ]
    )

    by_city = (
        test.groupby("city", as_index=False)
        .apply(
            lambda g: pd.Series(
                {
                    "mae": float(mean_absolute_error(g["value"], g["prediction"])),
                    "rmse": float(np.sqrt(mean_squared_error(g["value"], g["prediction"]))),
                    "mape": float(np.nanmean(g["abs_pct_error"])),
                    "rows": int(len(g)),
                }
            ),
            include_groups=False,
        )
        .reset_index(drop=True)
    )

    overall_metrics.to_csv(results_dir / "forecast_metrics_overall.csv", index=False)
    by_city.to_csv(results_dir / "forecast_metrics_by_city.csv", index=False)
    test.to_csv(results_dir / "forecast_predictions.csv", index=False)

    return {"overall_metrics": overall_metrics, "by_city": by_city, "predictions": test}


def anomaly_method(artifacts: PipelineArtifacts, results_dir: Path, figures_dir: Path) -> dict[str, pd.DataFrame]:
    """Detect unusual demand observations with a hybrid anomaly rule."""
    df = artifacts.enriched.copy()
    df["city"] = infer_city(df["region"])
    feature_cols = ["value", "lag_1", "lag_7", "rolling_7_mean", "rolling_7_std", "pct_change_1", "zscore_30"]
    cat_cols = ["region", "source"]
    model_df = df.dropna(subset=["date", "value"]).copy()

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "num",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler()),
                    ]
                ),
                feature_cols,
            ),
            ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
        ]
    )
    anomaly_model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("detector", IsolationForest(random_state=42, contamination=0.03)),
        ]
    )
    anomaly_model.fit(model_df[feature_cols + cat_cols])
    model_df["isolation_flag"] = anomaly_model.predict(model_df[feature_cols + cat_cols])
    model_df["is_zscore_anomaly"] = model_df["zscore_30"].abs().ge(2.5)
    model_df["is_anomaly"] = (model_df["isolation_flag"] == -1) | model_df["is_zscore_anomaly"]

    anomalies = model_df.loc[model_df["is_anomaly"]].copy()
    anomalies = anomalies.sort_values(by=["zscore_30", "value"], key=lambda s: s.abs() if s.name == "zscore_30" else s, ascending=False)
    anomaly_rate = (
        model_df.groupby(["city", "source"], as_index=False)["is_anomaly"]
        .mean()
        .rename(columns={"is_anomaly": "anomaly_rate"})
    )

    anomalies.to_csv(results_dir / "anomaly_flags.csv", index=False)
    anomaly_rate.to_csv(results_dir / "anomaly_rates.csv", index=False)

    return {"anomalies": anomalies, "anomaly_rate": anomaly_rate}


def contribution_and_structure_method(
    artifacts: PipelineArtifacts,
    results_dir: Path,
    figures_dir: Path,
) -> dict[str, pd.DataFrame]:
    """Rank top contributors and compare Paris vs NYC structure."""
    station_fact = artifacts.station_fact.copy()
    station_fact["city"] = infer_city(station_fact["region"])

    contributors = (
        station_fact.groupby(["city", "source", "location_name"], as_index=False)["value"]
        .sum()
        .rename(columns={"value": "total_value"})
        .sort_values("total_value", ascending=False)
        .head(20)
    )

    city_daily = artifacts.enriched.copy()
    city_daily["city"] = infer_city(city_daily["region"])
    city_daily = city_daily.groupby(["date", "city"], as_index=False).agg(
        total_value=("value", "sum"),
        is_weekend=("is_weekend", "max"),
        month=("month", "first"),
    )

    city_summary = (
        city_daily.groupby("city", as_index=False)
        .apply(
            lambda g: pd.Series(
                {
                    "avg_daily_value": float(g["total_value"].mean()),
                    "median_daily_value": float(g["total_value"].median()),
                    "std_daily_value": float(g["total_value"].std(ddof=0)),
                    "coeff_variation": float(g["total_value"].std(ddof=0) / g["total_value"].mean()),
                    "weekend_weekday_ratio": float(
                        g.loc[g["is_weekend"] == 1, "total_value"].mean()
                        / g.loc[g["is_weekend"] == 0, "total_value"].mean()
                    ),
                    "peak_month": int(g.groupby("month")["total_value"].mean().idxmax()),
                    "row_count": int(len(g)),
                }
            ),
            include_groups=False,
        )
        .reset_index(drop=True)
    )

    monthly_city = (
        city_daily.groupby(["city", "month"], as_index=False)["total_value"]
        .mean()
        .rename(columns={"total_value": "avg_monthly_value"})
    )

    contributors.to_csv(results_dir / "top_contributors.csv", index=False)
    city_summary.to_csv(results_dir / "city_structure_summary.csv", index=False)
    monthly_city.to_csv(results_dir / "city_monthly_structure.csv", index=False)

    return {"contributors": contributors, "city_summary": city_summary, "monthly_city": monthly_city}


def run_stage_workflow(artifacts: PipelineArtifacts, root: Path) -> dict[str, object]:
    """Run Stage 1 planning outputs and the five selected Stage 2 methods."""
    results_dir, figures_dir = _ensure_dirs(root)

    stage1 = stage_one_plan()
    stage1.to_csv(results_dir / "stage1_method_plan.csv", index=False)

    outputs = {
        "stage1_plan": stage1,
        "temporal": temporal_profile_method(artifacts, results_dir, figures_dir),
        "weather": weather_impact_method(artifacts, results_dir, figures_dir),
        "forecast": forecasting_method(artifacts, results_dir, figures_dir),
        "anomaly": anomaly_method(artifacts, results_dir, figures_dir),
        "comparison": contribution_and_structure_method(artifacts, results_dir, figures_dir),
    }

    summary = {
        "weather_source": artifacts.weather_source,
        "station_fact_rows": int(len(artifacts.station_fact)),
        "daily_rows": int(len(artifacts.daily)),
        "featured_rows": int(len(artifacts.featured)),
        "enriched_rows": int(len(artifacts.enriched)),
        "stage1_selected_methods": int(len(stage1)),
    }
    (results_dir / "analysis_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return outputs

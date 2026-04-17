#Mehdi AGHAEI
# should not be used in the final PostgreSQL-first submission path.
# legacy context helpers kept only for the older local-file workflow

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .context import infer_city
from .legacy_config import ProjectPaths
from .legacy_io import clean_numeric, parse_any_date, read_table_smart

# maps each city to a country code
def infer_country(city: pd.Series) -> pd.Series:
    return np.where(city.eq("Paris"), "FR", "US")

# finds a weekday like the 4th thursday of a month
def _nth_weekday(year: int, month: int, weekday: int, nth: int) -> pd.Timestamp:
    start = pd.Timestamp(year=year, month=month, day=1)
    offset = (weekday - start.weekday()) % 7
    return start + pd.Timedelta(days=offset + 7 * (nth - 1))

# finds the last chosen weekday of a month
def _last_weekday(year: int, month: int, weekday: int) -> pd.Timestamp:
    if month == 12:
        end = pd.Timestamp(year=year + 1, month=1, day=1) - pd.Timedelta(days=1)
    else:
        end = pd.Timestamp(year=year, month=month + 1, day=1) - pd.Timedelta(days=1)
    offset = (end.weekday() - weekday) % 7
    return end - pd.Timedelta(days=offset)

# adds simple calendar columns for each date
def build_calendar_context(date_values: pd.Series, country_values: pd.Series) -> pd.DataFrame:
    base = pd.DataFrame({"date": pd.to_datetime(date_values), "country": country_values.astype(str)})
    out = base.drop_duplicates().sort_values(["country", "date"]).reset_index(drop=True)
    out["year"] = out["date"].dt.year
    out["month"] = out["date"].dt.month
    out["day_of_week"] = out["date"].dt.dayofweek
    out["is_weekend"] = (out["day_of_week"] >= 5).astype(int)
    out["is_holiday"] = 0
    out["holiday_name"] = ""

    fixed = {
        "FR": {
            (1, 1): "New Year",
            (5, 1): "Labour Day",
            (7, 14): "Bastille Day",
            (11, 11): "Armistice Day",
            (12, 25): "Christmas",
        },
        "US": {
            (1, 1): "New Year",
            (7, 4): "Independence Day",
            (12, 25): "Christmas",
        },
    }

    for country, mapping in fixed.items():
        mask = out["country"].eq(country)
        for (month, day), name in mapping.items():
            holiday_mask = mask & out["month"].eq(month) & out["date"].dt.day.eq(day)
            out.loc[holiday_mask, ["is_holiday", "holiday_name"]] = [1, name]

    us_years = sorted(out.loc[out["country"].eq("US"), "year"].unique().tolist())
    for year in us_years:
        thanksgiving = _nth_weekday(year, 11, weekday=3, nth=4)
        memorial_day = _last_weekday(year, 5, weekday=0)
        labor_day = _nth_weekday(year, 9, weekday=0, nth=1)
        mapping = {
            thanksgiving: "Thanksgiving",
            memorial_day: "Memorial Day",
            labor_day: "Labor Day",
        }
        for holiday_date, name in mapping.items():
            mask = out["country"].eq("US") & out["date"].eq(holiday_date)
            out.loc[mask, ["is_holiday", "holiday_name"]] = [1, name]

    return out

# small container for weather data and its source
@dataclass(frozen=True)
class WeatherContextInfo:
    weather: pd.DataFrame
    source_label: str

# creates simple demo weather data
def build_demo_weather_context(daily: pd.DataFrame) -> WeatherContextInfo:
    keys = daily[["date", "region"]].drop_duplicates().copy()
    keys["date"] = pd.to_datetime(keys["date"])
    doy = keys["date"].dt.dayofyear.to_numpy()
    is_paris = keys["region"].eq("Ile-de-France").to_numpy()
    ordinal = (keys["date"].astype("int64") // 86_400_000_000_000).to_numpy()

    noise = np.sin(ordinal / 11.0 + is_paris.astype(int) * 0.7)
    noise_2 = np.cos(ordinal / 7.0 + is_paris.astype(int) * 0.4)

    base_temp = np.where(is_paris, 12.0, 13.5)
    seasonal_temp = 10 * np.sin((doy - 80) * 2 * np.pi / 365.25)
    keys["mean_temp_c"] = np.round(base_temp + seasonal_temp + 2.2 * noise, 2)

    base_precip = np.where(is_paris, 2.8, 3.2)
    keys["precip_mm"] = np.round(np.clip(base_precip + 1.3 * (noise_2 + 1), 0, None), 2)
    keys["wind_kmh"] = np.round(np.clip(14 + 4.5 * noise, 2, None), 2)
    keys["weather_source"] = "synthetic_demo"
    return WeatherContextInfo(weather=keys, source_label="synthetic_demo")

# uses a real weather file or a demo fallback
def load_weather_context(paths: ProjectPaths, daily: pd.DataFrame) -> WeatherContextInfo:
    if paths.weather_daily.exists():
        weather = read_table_smart(paths.weather_daily)
        renamed = weather.rename(
            columns={
                "weather_date": "date",
                "weather_source": "source",
            }
        )
        if "date" not in renamed.columns or "region" not in renamed.columns:
            raise ValueError("weather_daily.csv must include `date` and `region` columns.")
        renamed["date"] = parse_any_date(renamed["date"])
        for col in ["mean_temp_c", "precip_mm", "wind_kmh"]:
            if col in renamed.columns:
                renamed[col] = clean_numeric(renamed[col])
        if "source" not in renamed.columns:
            renamed["source"] = "weather_daily_csv"
        keep = ["date", "region", "mean_temp_c", "precip_mm", "wind_kmh", "source"]
        weather = renamed.reindex(columns=keep)
        weather = weather.rename(columns={"source": "weather_source"})
        weather = weather.dropna(subset=["date", "region"]).drop_duplicates(["date", "region"])
        return WeatherContextInfo(weather=weather, source_label="weather_daily_csv")

    return build_demo_weather_context(daily)

# attaches calendar and weather info to daily data
def enrich_daily_with_context(daily: pd.DataFrame, paths: ProjectPaths) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, str]:
    out = daily.copy()
    out["date"] = pd.to_datetime(out["date"])
    out["city"] = infer_city(out["region"])
    out["country"] = infer_country(out["city"])

    calendar = build_calendar_context(out["date"], out["country"])
    weather_info = load_weather_context(paths, out)

    calendar_merge = calendar[["date", "country", "is_holiday", "holiday_name"]]
    out = out.merge(calendar_merge, on=["date", "country"], how="left")
    out = out.merge(weather_info.weather, on=["date", "region"], how="left")
    return out, calendar, weather_info.weather, weather_info.source_label

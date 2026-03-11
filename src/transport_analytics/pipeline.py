"""Pipeline orchestration for canonical fact-table creation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from .config import ProjectPaths
from .context import enrich_daily_with_context
from .features import add_time_features
from .io import clean_numeric, combine_grouped_frames, iter_table_smart, parse_any_date, read_table_smart


FACT_GROUP_COLS = ["date", "region", "location_id", "location_name", "metric_type", "source"]


@dataclass
class PipelineArtifacts:
    """Materialized outputs produced by the local analytics pipeline."""

    station_fact: pd.DataFrame
    daily: pd.DataFrame
    featured: pd.DataFrame
    enriched: pd.DataFrame
    calendar: pd.DataFrame
    weather: pd.DataFrame
    mta_hourly_profile: pd.DataFrame
    paris_hourly_profile: pd.DataFrame
    weather_source: str


def _chunk_limit(sample_mode: bool) -> int | None:
    return 1 if sample_mode else None


def _load_travel_titles_fact(paths: ProjectPaths, sample_mode: bool) -> pd.DataFrame:
    """Aggregate Kaggle Paris/suburbs validations to daily station level."""
    partials: list[pd.DataFrame] = []
    usecols = ["DATE", "STATION_NAME", "ID_REFA_LDA", "NB_VALID"]
    chunksize = 100_000 if sample_mode else 250_000

    for chunk_idx, chunk in enumerate(iter_table_smart(paths.travel_titles, chunksize=chunksize, usecols=usecols)):
        chunk["date"] = parse_any_date(chunk["DATE"])
        chunk["value"] = clean_numeric(chunk["NB_VALID"])
        chunk["location_id"] = chunk["ID_REFA_LDA"].astype("Int64").astype(str)
        chunk["location_name"] = chunk["STATION_NAME"].fillna("Unknown station")

        grouped = (
            chunk.dropna(subset=["date", "value"])
            .groupby(["date", "location_id", "location_name"], as_index=False)["value"]
            .sum()
        )
        grouped["region"] = "Ile-de-France"
        grouped["metric_type"] = "validations"
        grouped["source"] = "travel_titles_paris"
        partials.append(grouped[FACT_GROUP_COLS + ["value"]])

        if _chunk_limit(sample_mode) is not None and chunk_idx + 1 >= _chunk_limit(sample_mode):
            break

    return combine_grouped_frames(partials, FACT_GROUP_COLS, ["value"])


def _load_idfm_surface_fact(paths: ProjectPaths, sample_mode: bool) -> pd.DataFrame:
    """Aggregate IDFM surface validations to daily line level."""
    partials: list[pd.DataFrame] = []
    usecols = ["JOUR", "ID_GROUPOFLINES", "LIBELLE_LIGNE", "NB_VALD"]
    chunksize = 100_000 if sample_mode else 250_000

    for chunk_idx, chunk in enumerate(iter_table_smart(paths.idfm_surface, chunksize=chunksize, usecols=usecols)):
        chunk["date"] = parse_any_date(chunk["JOUR"])
        chunk["value"] = clean_numeric(chunk["NB_VALD"])
        chunk["location_id"] = chunk["ID_GROUPOFLINES"].astype(str)
        chunk["location_name"] = chunk["LIBELLE_LIGNE"].fillna("Unknown line")

        grouped = (
            chunk.dropna(subset=["date", "value"])
            .groupby(["date", "location_id", "location_name"], as_index=False)["value"]
            .sum()
        )
        grouped["region"] = "Ile-de-France"
        grouped["metric_type"] = "validations"
        grouped["source"] = "idfm_surface"
        partials.append(grouped[FACT_GROUP_COLS + ["value"]])

        if _chunk_limit(sample_mode) is not None and chunk_idx + 1 >= _chunk_limit(sample_mode):
            break

    return combine_grouped_frames(partials, FACT_GROUP_COLS, ["value"])


def _load_idf_nb_fer_fact(paths: ProjectPaths, sample_mode: bool) -> pd.DataFrame:
    """Aggregate Ile-de-France rail validations to daily station level."""
    base = paths.idf_root
    nb_files = sorted(base.glob("data-rf-*/*NB_FER*.txt")) + sorted(base.glob("data-rf-*/*NB_FER*.csv"))
    nb_files += sorted((base / "data-rf-2020" / "data-rf-2020").glob("*NB_FER*.txt"))
    if sample_mode:
        nb_files = nb_files[-4:]

    frames: list[pd.DataFrame] = []
    for fp in nb_files:
        df = read_table_smart(fp)
        df.columns = [c.strip() for c in df.columns]

        date_col = "JOUR" if "JOUR" in df.columns else None
        id_col = next((c for c in ("ID_ZDC", "ID_REFA_LDA", "lda") if c in df.columns), None)
        val_col = "NB_VALD" if "NB_VALD" in df.columns else None
        name_col = "LIBELLE_ARRET" if "LIBELLE_ARRET" in df.columns else None

        if date_col is None or val_col is None:
            continue

        grouped = pd.DataFrame(
            {
                "date": parse_any_date(df[date_col]),
                "location_id": df[id_col].astype(str) if id_col else "unknown",
                "location_name": df[name_col].fillna("Unknown station") if name_col else "Unknown station",
                "value": clean_numeric(df[val_col]),
            }
        )
        grouped = grouped.dropna(subset=["date", "value"]).groupby(["date", "location_id", "location_name"], as_index=False)[
            "value"
        ].sum()
        grouped["region"] = "Ile-de-France"
        grouped["metric_type"] = "validations"
        grouped["source"] = "idf_nb_fer"
        frames.append(grouped[FACT_GROUP_COLS + ["value"]])

    return combine_grouped_frames(frames, FACT_GROUP_COLS, ["value"])


def _load_mta_fact_and_hourly_profile(paths: ProjectPaths, sample_mode: bool) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Aggregate NYC MTA hourly ridership to daily station level and hourly profiles."""
    usecols = ["transit_timestamp", "station_complex_id", "station_complex", "borough", "ridership"]
    daily_partials: list[pd.DataFrame] = []
    hourly_partials: list[pd.DataFrame] = []
    chunksize = 1_000_000 if sample_mode else 1_000_000

    for chunk_idx, chunk in enumerate(iter_table_smart(paths.mta_hourly, chunksize=chunksize, usecols=usecols)):
        ts = pd.to_datetime(chunk["transit_timestamp"], format="%m/%d/%Y %I:%M:%S %p", errors="coerce")
        missing = ts.isna()
        if missing.any():
            ts.loc[missing] = parse_any_date(chunk.loc[missing, "transit_timestamp"])

        chunk["date"] = ts.dt.floor("D")
        chunk["hour"] = ts.dt.hour
        chunk["value"] = clean_numeric(chunk["ridership"])
        chunk["region"] = chunk["borough"].fillna("NYC")
        chunk["location_id"] = chunk["station_complex_id"].astype(str).str.strip()
        chunk["location_name"] = chunk["station_complex"].fillna("Unknown station")

        daily_grouped = (
            chunk.dropna(subset=["date", "value"])
            .groupby(["date", "region", "location_id", "location_name"], as_index=False)["value"]
            .sum()
        )
        daily_grouped["metric_type"] = "ridership"
        daily_grouped["source"] = "mta_hourly_agg_daily"
        daily_partials.append(daily_grouped[FACT_GROUP_COLS + ["value"]])

        hourly_grouped = (
            chunk.dropna(subset=["hour", "value"])
            .groupby(["region", "hour"], as_index=False)["value"]
            .sum()
        )
        hourly_partials.append(hourly_grouped)

        if _chunk_limit(sample_mode) is not None and chunk_idx + 1 >= _chunk_limit(sample_mode):
            break

    daily = combine_grouped_frames(daily_partials, FACT_GROUP_COLS, ["value"])
    hourly = combine_grouped_frames(hourly_partials, ["region", "hour"], ["value"])
    if not hourly.empty:
        hourly["hour_label"] = hourly["hour"].map(lambda h: f"{int(h):02d}:00")
    return daily, hourly


def _load_paris_hourly_profile(paths: ProjectPaths, sample_mode: bool) -> pd.DataFrame:
    """Aggregate Paris validation share profiles from PROFIL_FER files."""
    base = paths.idf_root
    profile_files = sorted(base.glob("data-rf-*/*PROFIL_FER*.txt")) + sorted(base.glob("data-rf-*/*PROFIL_FER*.csv"))
    if sample_mode:
        profile_files = profile_files[-4:]

    frames: list[pd.DataFrame] = []
    for fp in profile_files:
        df = read_table_smart(fp)
        df.columns = [c.strip() for c in df.columns]

        hour_col = "TRNC_HORR_60" if "TRNC_HORR_60" in df.columns else None
        val_col = "pourc_validations" if "pourc_validations" in df.columns else None
        day_col = "CAT_JOUR" if "CAT_JOUR" in df.columns else None
        if hour_col is None or val_col is None:
            continue

        out = pd.DataFrame(
            {
                "day_category": df[day_col].astype(str) if day_col else "all_days",
                "hour_bin": df[hour_col].astype(str),
                "validation_share_pct": clean_numeric(df[val_col]),
            }
        )
        out = out.dropna(subset=["hour_bin", "validation_share_pct"])
        frames.append(out)

    if not frames:
        return pd.DataFrame(columns=["day_category", "hour_bin", "validation_share_pct"])

    combined = pd.concat(frames, ignore_index=True)
    return combined.groupby(["day_category", "hour_bin"], as_index=False)["validation_share_pct"].mean()


def build_station_fact_table(paths: ProjectPaths, sample_mode: bool = True) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Build canonical station/line fact table plus hourly profile helper tables."""
    travel_titles = _load_travel_titles_fact(paths, sample_mode=sample_mode)
    idfm_surface = _load_idfm_surface_fact(paths, sample_mode=sample_mode)
    idf_nb_fer = _load_idf_nb_fer_fact(paths, sample_mode=sample_mode)
    mta_daily, mta_hourly = _load_mta_fact_and_hourly_profile(paths, sample_mode=sample_mode)
    paris_hourly = _load_paris_hourly_profile(paths, sample_mode=sample_mode)

    station_fact = pd.concat([travel_titles, idfm_surface, idf_nb_fer, mta_daily], ignore_index=True)
    station_fact["date"] = pd.to_datetime(station_fact["date"], errors="coerce").dt.floor("D")
    station_fact["value"] = pd.to_numeric(station_fact["value"], errors="coerce")
    station_fact = station_fact.dropna(subset=["date", "value"])
    station_fact = station_fact.groupby(FACT_GROUP_COLS, as_index=False)["value"].sum()
    return station_fact, mta_hourly, paris_hourly


def build_daily_fact_table(station_fact: pd.DataFrame) -> pd.DataFrame:
    """Aggregate canonical fact rows to daily series used in modeling."""
    daily = (
        station_fact.groupby(["date", "region", "source", "metric_type"], as_index=False)["value"]
        .sum()
        .sort_values(["source", "region", "date"])
    )
    return daily.reset_index(drop=True)


def persist_pipeline_outputs(paths: ProjectPaths, artifacts: PipelineArtifacts) -> None:
    """Persist materialized pipeline outputs into `data/processed/`."""
    artifacts.station_fact.to_csv(paths.processed / "station_fact_table.csv", index=False)
    artifacts.daily.to_csv(paths.processed / "daily_fact_table.csv", index=False)
    artifacts.featured.to_csv(paths.processed / "daily_fact_table_featured.csv", index=False)
    artifacts.enriched.to_csv(paths.processed / "daily_fact_table_enriched.csv", index=False)
    artifacts.calendar.to_csv(paths.processed / "dim_calendar.csv", index=False)
    artifacts.weather.to_csv(paths.processed / "dim_weather.csv", index=False)
    artifacts.mta_hourly_profile.to_csv(paths.processed / "nyc_hourly_profile.csv", index=False)
    artifacts.paris_hourly_profile.to_csv(paths.processed / "paris_hourly_profile.csv", index=False)


def run_local_pipeline(root: Path, sample_mode: bool = True) -> PipelineArtifacts:
    """Run local processing and save canonical + enriched tables."""
    paths = ProjectPaths(root=root)

    station_fact, mta_hourly_profile, paris_hourly_profile = build_station_fact_table(paths=paths, sample_mode=sample_mode)
    daily = build_daily_fact_table(station_fact)
    featured = add_time_features(daily)
    enriched, calendar, weather, weather_source = enrich_daily_with_context(featured, paths)

    artifacts = PipelineArtifacts(
        station_fact=station_fact,
        daily=daily,
        featured=featured,
        enriched=enriched,
        calendar=calendar,
        weather=weather,
        mta_hourly_profile=mta_hourly_profile,
        paris_hourly_profile=paris_hourly_profile,
        weather_source=weather_source,
    )
    persist_pipeline_outputs(paths, artifacts)
    return artifacts

"""Pipeline orchestration for canonical fact-table creation."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .config import ProjectPaths
from .features import add_time_features
from .io import clean_numeric, parse_any_date, read_table_smart


def _load_core(paths: ProjectPaths) -> dict[str, pd.DataFrame]:
    """Load core datasets used by most analyses.

    These datasets are moderate in size compared to the full MTA file.
    """
    regularities_fr = pd.read_csv(paths.datasets / "Regularities_by_liaisons_Trains_France.csv")
    travel_titles = pd.read_csv(paths.datasets / "Travel_titles_validations_in_Paris_and_suburbs.csv")
    idfm_surface = read_table_smart(paths.datasets / "idfm_validations_surface.csv")
    tgv_monthly = read_table_smart(paths.idf_data / "regularite-mensuelle-tgv-aqst.csv")

    return {
        "regularities_fr": regularities_fr,
        "travel_titles": travel_titles,
        "idfm_surface": idfm_surface,
        "tgv_monthly": tgv_monthly,
    }


def _load_mta_daily(paths: ProjectPaths, sample_rows: int | None = 300_000) -> pd.DataFrame:
    """Load MTA hourly data and aggregate it to daily station-level values."""
    usecols = [
        "transit_timestamp",
        "station_complex_id",
        "station_complex",
        "borough",
        "ridership",
        "transfers",
    ]
    kwargs = {"usecols": usecols, "low_memory": False}
    if sample_rows is not None:
        # Sample mode keeps local iteration fast.
        kwargs["nrows"] = sample_rows

    mta = pd.read_csv(paths.mta_data / "MTA_Subway_Hourly_Ridership__2020-2024.csv", **kwargs)

    # Normalize key fields used in aggregation.
    # MTA typically uses the explicit format below (month/day/year + 12h clock).
    ts = pd.to_datetime(mta["transit_timestamp"], format="%m/%d/%Y %I:%M:%S %p", errors="coerce")
    missing_ts = ts.isna()
    if missing_ts.any():
        # Fallback parser for any rows that do not match the primary format.
        ts.loc[missing_ts] = parse_any_date(mta.loc[missing_ts, "transit_timestamp"])
    mta["date"] = ts.dt.floor("D")
    mta["ridership"] = pd.to_numeric(mta["ridership"], errors="coerce")
    mta["transfers"] = pd.to_numeric(mta["transfers"], errors="coerce")

    # Daily station-level rollup.
    return (
        mta.dropna(subset=["date"])
        .groupby(["date", "borough", "station_complex_id", "station_complex"], as_index=False)[["ridership", "transfers"]]
        .sum()
    )


def _load_idf_nb_files(paths: ProjectPaths, max_files: int = 6, max_rows: int | None = 250_000) -> pd.DataFrame:
    """Load recent Ile-de-France NB_FER files and normalize schema.

    File format changed across years, so we resolve column names dynamically.
    """
    base = paths.idf_data

    # Collect both txt and csv variants plus nested 2020 folder.
    nb_files = sorted(base.glob("data-rf-*/*NB_FER*.txt")) + sorted(base.glob("data-rf-*/*NB_FER*.csv"))
    nb_files += sorted((base / "data-rf-2020" / "data-rf-2020").glob("*NB_FER*.txt"))
    nb_files = nb_files[-max_files:]

    frames: list[pd.DataFrame] = []
    for fp in nb_files:
        df = read_table_smart(fp, nrows=max_rows)
        df.columns = [c.strip() for c in df.columns]

        # Columns differ by year/version; resolve aliases.
        date_col = "JOUR" if "JOUR" in df.columns else None
        id_col = (
            "ID_ZDC"
            if "ID_ZDC" in df.columns
            else ("ID_REFA_LDA" if "ID_REFA_LDA" in df.columns else ("lda" if "lda" in df.columns else None))
        )
        val_col = "NB_VALD" if "NB_VALD" in df.columns else None

        if date_col is None or val_col is None:
            # Skip files that do not match expected schema.
            continue

        frames.append(
            pd.DataFrame(
                {
                    "date": parse_any_date(df[date_col]),
                    "station_id": df[id_col].astype(str) if id_col else np.nan,
                    "station_name": df.get("LIBELLE_ARRET", np.nan),
                    "ticket_category": df.get("CATEGORIE_TITRE", np.nan),
                    "validations": clean_numeric(df[val_col]),
                    "source_file": fp.name,
                }
            )
        )

    if not frames:
        return pd.DataFrame(columns=["date", "station_id", "station_name", "ticket_category", "validations", "source_file"])
    return pd.concat(frames, ignore_index=True)


def build_canonical_fact_table(paths: ProjectPaths, sample_mode: bool = True) -> pd.DataFrame:
    """Build canonical facts from all available project datasets."""
    core = _load_core(paths)
    travel_titles = core["travel_titles"].copy()
    idfm_surface = core["idfm_surface"].copy()

    # Standardize date/count fields across heterogeneous sources.
    travel_titles["date"] = parse_any_date(travel_titles["DATE"])
    travel_titles["validations"] = clean_numeric(travel_titles["NB_VALID"])

    idfm_surface["date"] = parse_any_date(idfm_surface["JOUR"])
    idfm_surface["validations"] = clean_numeric(idfm_surface["NB_VALD"])

    # Optional sample mode for very large raw files.
    idf_nb = _load_idf_nb_files(
        paths,
        max_files=6 if sample_mode else 100,
        max_rows=250_000 if sample_mode else None,
    )
    mta_daily = _load_mta_daily(paths, sample_rows=300_000 if sample_mode else None)

    # Convert each source to one canonical schema.
    facts = [
        pd.DataFrame(
            {
                "date": travel_titles["date"],
                "region": "Ile-de-France",
                "location_id": travel_titles["ID_REFA_LDA"].astype(str),
                "location_name": travel_titles["STATION_NAME"],
                "metric_type": "validations",
                "value": travel_titles["validations"],
                "source": "travel_titles_paris",
            }
        ),
        pd.DataFrame(
            {
                "date": idfm_surface["date"],
                "region": "Ile-de-France",
                "location_id": idfm_surface.get("ID_GROUPOFLINES", pd.Series([np.nan] * len(idfm_surface))).astype(str),
                "location_name": idfm_surface.get("LIBELLE_LIGNE", pd.Series([np.nan] * len(idfm_surface))),
                "metric_type": "validations",
                "value": idfm_surface["validations"],
                "source": "idfm_surface",
            }
        ),
        pd.DataFrame(
            {
                "date": mta_daily["date"],
                "region": mta_daily["borough"].fillna("NYC"),
                "location_id": mta_daily["station_complex_id"].astype(str),
                "location_name": mta_daily["station_complex"],
                "metric_type": "ridership",
                "value": mta_daily["ridership"],
                "source": "mta_hourly_agg_daily",
            }
        ),
    ]

    # Include IDF station-level validations if available.
    if not idf_nb.empty:
        facts.append(
            pd.DataFrame(
                {
                    "date": idf_nb["date"],
                    "region": "Ile-de-France",
                    "location_id": idf_nb["station_id"].astype(str),
                    "location_name": idf_nb["station_name"],
                    "metric_type": "validations",
                    "value": idf_nb["validations"],
                    "source": "idf_nb_fer",
                }
            )
        )

    # Final canonical table cleanup.
    fact = pd.concat(facts, ignore_index=True)
    fact["date"] = pd.to_datetime(fact["date"], errors="coerce").dt.floor("D")
    fact["value"] = pd.to_numeric(fact["value"], errors="coerce")
    fact = fact.dropna(subset=["date", "value"])
    return fact


def run_local_pipeline(root: Path, sample_mode: bool = True) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Run local processing and save daily + featured tables to data/processed."""
    paths = ProjectPaths(root=root)

    # Build canonical fact table from raw sources.
    fact = build_canonical_fact_table(paths=paths, sample_mode=sample_mode)

    # Create daily aggregates used by modeling/monitoring.
    daily = (
        fact.groupby(["date", "region", "source", "metric_type"], as_index=False)["value"]
        .sum()
        .sort_values(["source", "region", "date"])
    )

    # Add lag/rolling/calendar features.
    featured = add_time_features(daily)

    # Persist outputs for downstream notebooks and SQL loading.
    daily.to_csv(paths.processed / "daily_fact_table.csv", index=False)
    featured.to_csv(paths.processed / "daily_fact_table_featured.csv", index=False)
    return daily, featured

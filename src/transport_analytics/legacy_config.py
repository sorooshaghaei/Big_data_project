#Mehdi AGHAEI
# should not be used in the final PostgreSQL-first submission path.
# legacy paths kept only for the older local-file workflow

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

# keeps the older local-file paths together
@dataclass(frozen=True)
class ProjectPaths:
    root: Path
    datasets: Path = field(init=False)
    data: Path = field(init=False)
    processed: Path = field(init=False)
    report: Path = field(init=False)
    report_results: Path = field(init=False)
    report_figures: Path = field(init=False)
    idf_root: Path = field(init=False)
    mta_data: Path = field(init=False)
    travel_titles: Path = field(init=False)
    idfm_surface: Path = field(init=False)
    regularities_fr: Path = field(init=False)
    mta_hourly: Path = field(init=False)
    weather_daily: Path = field(init=False)

    # fills the common folders once for the older workflow
    def __post_init__(self) -> None:
        root = self.root.resolve()
        data = root / "data"
        report = root / "report"
        processed = data / "processed"
        report_results = report / "results"
        report_figures = report / "figures"

        for folder in (processed, report, report_results, report_figures):
            folder.mkdir(parents=True, exist_ok=True)

        object.__setattr__(self, "root", root)
        object.__setattr__(self, "datasets", root / "datasets")
        object.__setattr__(self, "data", data)
        object.__setattr__(self, "processed", processed)
        object.__setattr__(self, "report", report)
        object.__setattr__(self, "report_results", report_results)
        object.__setattr__(self, "report_figures", report_figures)
        object.__setattr__(self, "idf_root", data / "Ile_de_france")
        object.__setattr__(self, "mta_data", data / "soroosh_MTA")
        object.__setattr__(self, "travel_titles", root / "datasets" / "Travel_titles_validations_in_Paris_and_suburbs.csv")
        object.__setattr__(self, "idfm_surface", root / "datasets" / "idfm_validations_surface.csv")
        object.__setattr__(self, "regularities_fr", root / "datasets" / "Regularities_by_liaisons_Trains_France.csv")
        object.__setattr__(self, "mta_hourly", data / "soroosh_MTA" / "MTA_Subway_Hourly_Ridership__2020-2024.csv")
        object.__setattr__(self, "weather_daily", data / "weather_daily.csv")

"""Configuration objects for paths and PostgreSQL connection."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProjectPaths:
    """Filesystem paths used by the project workflow."""

    root: Path

    @property
    def datasets(self) -> Path:
        return self.root / "datasets"

    @property
    def data(self) -> Path:
        return self.root / "data"

    @property
    def processed(self) -> Path:
        out = self.data / "processed"
        out.mkdir(parents=True, exist_ok=True)
        return out

    @property
    def report(self) -> Path:
        out = self.root / "report"
        out.mkdir(parents=True, exist_ok=True)
        return out

    @property
    def report_results(self) -> Path:
        out = self.report / "results"
        out.mkdir(parents=True, exist_ok=True)
        return out

    @property
    def report_figures(self) -> Path:
        out = self.report / "figures"
        out.mkdir(parents=True, exist_ok=True)
        return out

    @property
    def idf_root(self) -> Path:
        return self.data / "Ile_de_france"

    @property
    def mta_data(self) -> Path:
        return self.data / "soroosh_MTA"

    @property
    def travel_titles(self) -> Path:
        return self.datasets / "Travel_titles_validations_in_Paris_and_suburbs.csv"

    @property
    def idfm_surface(self) -> Path:
        return self.datasets / "idfm_validations_surface.csv"

    @property
    def regularities_fr(self) -> Path:
        return self.datasets / "Regularities_by_liaisons_Trains_France.csv"

    @property
    def mta_hourly(self) -> Path:
        return self.mta_data / "MTA_Subway_Hourly_Ridership__2020-2024.csv"

    @property
    def weather_daily(self) -> Path:
        return self.data / "weather_daily.csv"


@dataclass(frozen=True)
class PostgresConfig:
    """PostgreSQL connection settings."""

    host: str = "34.155.143.75"
    port: int = 5432
    database: str = "transport_analytics"
    user: str = "postgres"
    password: str = "postgres"
    schema: str = "transport"

    @property
    def sqlalchemy_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.database}"
        )

    @classmethod
    def from_env(cls) -> "PostgresConfig":
        return cls(
            host=os.getenv("PGHOST", "34.155.143.75"),
            port=int(os.getenv("PGPORT", "5432")),
            database=os.getenv("PGDATABASE", "transport_analytics"),
            user=os.getenv("PGUSER", "postgres"),
            password=os.getenv("PGPASSWORD", "postgres"),
            schema=os.getenv("PGSCHEMA", "transport"),
        )

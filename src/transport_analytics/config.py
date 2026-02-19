"""Configuration objects for paths and PostgreSQL connection."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProjectPaths:
    """Filesystem paths used by the pipeline.

    Keeping paths in one dataclass avoids hardcoding path strings in
    multiple modules and makes the pipeline easier to reuse.
    """

    # Absolute path to the project root directory.
    root: Path

    @property
    def datasets(self) -> Path:
        # Static/secondary datasets downloaded into /datasets.
        return self.root / "datasets"

    @property
    def data(self) -> Path:
        # Main data directory containing raw and processed data.
        return self.root / "data"

    @property
    def idf_data(self) -> Path:
        # Ile-de-France source datasets.
        return self.data / "Ile_de_france"

    @property
    def mta_data(self) -> Path:
        # NYC MTA source datasets.
        return self.data / "soroosh_MTA"

    @property
    def processed(self) -> Path:
        # Ensure output directory exists before returning it.
        out = self.data / "processed"
        out.mkdir(parents=True, exist_ok=True)
        return out


@dataclass(frozen=True)
class PostgresConfig:
    """PostgreSQL connection settings.

    Defaults follow the shared project PostgreSQL host.
    Prefer using environment variables via `from_env()` so credentials
    are not hardcoded.
    """

    host: str = "34.155.143.75"
    port: int = 5432
    database: str = "transport_analytics"
    user: str = "postgres"
    password: str = "postgres"
    schema: str = "transport"

    @property
    def sqlalchemy_url(self) -> str:
        # SQLAlchemy URL used by create_engine.
        return (
            f"postgresql+psycopg://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.database}"
        )

    @classmethod
    def from_env(cls) -> "PostgresConfig":
        # Read config from standard PG* environment variables.
        return cls(
            host=os.getenv("PGHOST", "34.155.143.75"),
            port=int(os.getenv("PGPORT", "5432")),
            database=os.getenv("PGDATABASE", "transport_analytics"),
            user=os.getenv("PGUSER", "postgres"),
            password=os.getenv("PGPASSWORD", "postgres"),
            schema=os.getenv("PGSCHEMA", "transport"),
        )

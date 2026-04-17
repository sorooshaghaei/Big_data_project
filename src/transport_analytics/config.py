#Mehdi AGHAEI

from __future__ import annotations

import os
from dataclasses import dataclass, field

# keeps the postgres settings together
@dataclass(frozen=True)
class PostgresConfig:
    host: str = "34.155.143.75"
    port: int = 5432
    database: str = "transport"
    user: str = "team"
    password: str = ""
    schema: str = "public"
    sqlalchemy_url: str = field(init=False)

    # prepares the connection url once at startup
    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "sqlalchemy_url",
            f"postgresql+psycopg://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.database}",
        )

    # reads postgres settings from env vars
    @classmethod
    def from_env(cls) -> "PostgresConfig":
        required = ["PGHOST", "PGPORT", "PGDATABASE", "PGUSER", "PGPASSWORD"]
        missing = [key for key in required if not os.getenv(key)]
        if missing:
            missing_list = ", ".join(missing)
            raise ValueError(
                "Missing PostgreSQL environment variables: "
                f"{missing_list}. Copy .env.example to .env, fill it in, and load it before running the workflow."
            )

        return cls(
            host=os.getenv("PGHOST", "34.155.143.75"),
            port=int(os.getenv("PGPORT", "5432")),
            database=os.getenv("PGDATABASE", "transport"),
            user=os.getenv("PGUSER", "team"),
            password=os.getenv("PGPASSWORD", ""),
            schema=os.getenv("PGSCHEMA", "public"),
        )

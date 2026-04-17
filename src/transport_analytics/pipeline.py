#Mehdi AGHAEI

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

# holds the tables used by the official workflow
@dataclass
class PipelineArtifacts:

    station_fact: pd.DataFrame
    daily: pd.DataFrame
    featured: pd.DataFrame
    enriched: pd.DataFrame
    calendar: pd.DataFrame
    weather: pd.DataFrame
    mta_hourly_profile: pd.DataFrame
    paris_hourly_profile: pd.DataFrame
    weather_source: str

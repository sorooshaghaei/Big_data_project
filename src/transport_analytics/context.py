#Mehdi AGHAEI

from __future__ import annotations

import numpy as np
import pandas as pd

# maps each region to a city name
def infer_city(region: pd.Series) -> pd.Series:
    return np.where(region.eq("Ile-de-France"), "Paris", "NYC")

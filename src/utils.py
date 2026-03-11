# Mehdi AGHAEI
"""Compatibility layer around new package utilities."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from transport_analytics.io import read_table_smart


def load_data(path: str | Path, nrows: int | None = None) -> pd.DataFrame:
    """Backward-compatible loader used by older scripts/notebooks.

    Parameters
    ----------
    path:
        Input file path.
    nrows:
        Optional sample-size limit for faster experimentation.
    """
    # Delegate real loading logic to the reusable I/O helper.
    return read_table_smart(Path(path), nrows=nrows)

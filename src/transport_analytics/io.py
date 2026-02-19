"""Input/output helpers for mixed-format transport datasets."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def detect_separator(file_path: Path) -> str:
    """Infer delimiter from the header line.

    Many project files use different separators across years
    (`,`, `;`, or tab). This helper keeps loading logic robust.
    """
    header = file_path.open("rb").readline().decode("latin1", errors="ignore")
    candidates = {",": header.count(","), ";": header.count(";"), "\t": header.count("\t")}
    return max(candidates, key=candidates.get)


def read_table_smart(file_path: Path, nrows: int | None = None) -> pd.DataFrame:
    """Read CSV/TXT using inferred delimiter and fallback encodings.

    `nrows` allows sample-mode loading for large files.
    """
    sep = detect_separator(file_path)
    encodings = ["utf-8-sig", "utf-8", "latin1", "cp1252", "utf-16"]
    last_error: Exception | None = None

    # Try common encodings in order until one succeeds.
    for enc in encodings:
        try:
            return pd.read_csv(file_path, sep=sep, encoding=enc, nrows=nrows, low_memory=False)
        except Exception as exc:  # pragma: no cover - fallback behavior
            last_error = exc

    raise RuntimeError(f"Unable to read {file_path}: {last_error}")


def clean_numeric(series: pd.Series) -> pd.Series:
    """Normalize mixed numeric strings to float.

    Handles spaces as thousand separators, comma decimal separators,
    and domain-specific values such as "Less than 5".
    """
    s = series.astype(str).str.strip()

    # Remove non-breaking spaces and regular spaces used in thousands formatting.
    s = s.str.replace("\u00a0", "", regex=False)
    s = s.str.replace("\u202f", "", regex=False)
    s = s.str.replace(" ", "", regex=False)

    # Convert European decimal notation to dot notation.
    s = s.str.replace(",", ".", regex=False)

    # Domain normalization used in IDFM data.
    s = s.str.replace("Less than 5", "2", regex=False)

    # Normalize missing tokens before numeric conversion.
    s = s.replace({"": np.nan, "nan": np.nan, "None": np.nan, "?": np.nan})
    return pd.to_numeric(s, errors="coerce")


def parse_any_date(series: pd.Series) -> pd.Series:
    """Parse mixed date formats with explicit fast-paths first."""
    s = series.astype(str).str.strip()

    # Fast paths for the most common formats in this project.
    parsed = pd.to_datetime(s, format="%Y-%m-%d", errors="coerce")

    missing = parsed.isna()
    if missing.any():
        parsed.loc[missing] = pd.to_datetime(s[missing], format="%d/%m/%Y", errors="coerce")

    missing = parsed.isna()
    if missing.any():
        parsed.loc[missing] = pd.to_datetime(s[missing], format="%d/%m/%y", errors="coerce")

    # Final fallback for any remaining uncommon patterns.
    missing = parsed.isna()
    if missing.any():
        parsed.loc[missing] = pd.to_datetime(s[missing], errors="coerce", dayfirst=True)

    return parsed

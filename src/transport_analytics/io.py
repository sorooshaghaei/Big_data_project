# Mehdi AGHAEI
"""Input/output helpers for mixed-format transport datasets."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

DEFAULT_ENCODINGS = ("utf-8-sig", "utf-8", "latin1", "cp1252", "utf-16")


def detect_separator(file_path: Path) -> str:
    """Infer delimiter from the header line."""
    header = file_path.open("rb").readline().decode("latin1", errors="ignore")
    candidates = {",": header.count(","), ";": header.count(";"), "\t": header.count("\t")}
    return max(candidates, key=candidates.get)


def _read_csv_with_fallback(file_path: Path, **kwargs) -> pd.DataFrame:
    """Read a CSV-like file using fallback encodings."""
    sep = kwargs.pop("sep", detect_separator(file_path))
    last_error: Exception | None = None

    for enc in DEFAULT_ENCODINGS:
        try:
            return pd.read_csv(file_path, sep=sep, encoding=enc, low_memory=False, **kwargs)
        except Exception as exc:  # pragma: no cover - fallback behavior
            last_error = exc

    raise RuntimeError(f"Unable to read {file_path}: {last_error}")


def read_table_smart(
    file_path: Path,
    nrows: int | None = None,
    usecols: list[str] | None = None,
) -> pd.DataFrame:
    """Read CSV/TXT using inferred delimiter and fallback encodings."""
    return _read_csv_with_fallback(file_path, nrows=nrows, usecols=usecols)


def iter_table_smart(
    file_path: Path,
    *,
    chunksize: int,
    usecols: list[str] | None = None,
    nrows: int | None = None,
):
    """Yield CSV/TXT chunks using fallback encodings."""
    sep = detect_separator(file_path)
    last_error: Exception | None = None

    for enc in DEFAULT_ENCODINGS:
        try:
            reader = pd.read_csv(
                file_path,
                sep=sep,
                encoding=enc,
                usecols=usecols,
                chunksize=chunksize,
                nrows=nrows,
                low_memory=False,
            )
            for chunk in reader:
                yield chunk
            return
        except Exception as exc:  # pragma: no cover - fallback behavior
            last_error = exc

    raise RuntimeError(f"Unable to iterate over {file_path}: {last_error}")


def clean_numeric(series: pd.Series) -> pd.Series:
    """Normalize mixed numeric strings to float."""
    s = series.astype(str).str.strip()

    s = s.str.replace("\u00a0", "", regex=False)
    s = s.str.replace("\u202f", "", regex=False)
    s = s.str.replace(" ", "", regex=False)
    s = s.str.replace(",", ".", regex=False)
    s = s.str.replace("Less than 5", "2", regex=False)
    s = s.replace({"": np.nan, "nan": np.nan, "None": np.nan, "?": np.nan})
    return pd.to_numeric(s, errors="coerce")


def parse_any_date(series: pd.Series) -> pd.Series:
    """Parse mixed date formats with explicit fast-paths first."""
    s = series.astype(str).str.strip()
    parsed = pd.to_datetime(s, format="%Y-%m-%d", errors="coerce")

    missing = parsed.isna()
    if missing.any():
        parsed.loc[missing] = pd.to_datetime(s[missing], format="%d/%m/%Y", errors="coerce")

    missing = parsed.isna()
    if missing.any():
        parsed.loc[missing] = pd.to_datetime(s[missing], format="%d/%m/%y", errors="coerce")

    missing = parsed.isna()
    if missing.any():
        parsed.loc[missing] = pd.to_datetime(s[missing], errors="coerce", dayfirst=True)

    return parsed


def combine_grouped_frames(
    frames: list[pd.DataFrame],
    group_cols: list[str],
    value_cols: list[str],
) -> pd.DataFrame:
    """Combine partially grouped frames into one grouped frame."""
    if not frames:
        return pd.DataFrame(columns=[*group_cols, *value_cols])

    combined = pd.concat(frames, ignore_index=True)
    agg_map = {col: "sum" for col in value_cols}
    return combined.groupby(group_cols, as_index=False).agg(agg_map)

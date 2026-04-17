#Mehdi AGHAEI
# should not be used in the final PostgreSQL-first submission path.
# legacy raw-file readers kept only for the older local-file workflow

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

DEFAULT_ENCODINGS = ("utf-8-sig", "utf-8", "latin1", "cp1252", "utf-16")

# guesses the separator from the first line
def detect_separator(file_path: Path) -> str:
    header = file_path.open("rb").readline().decode("latin1", errors="ignore")
    candidates = {",": header.count(","), ";": header.count(";"), "\t": header.count("\t")}
    return max(candidates, key=candidates.get)

# tries common encodings until the file opens
def _read_csv_with_fallback(file_path: Path, **kwargs) -> pd.DataFrame:
    sep = kwargs.pop("sep", detect_separator(file_path))
    last_error: Exception | None = None

    for enc in DEFAULT_ENCODINGS:
        try:
            return pd.read_csv(file_path, sep=sep, encoding=enc, low_memory=False, **kwargs)
        except Exception as exc:
            last_error = exc

    raise RuntimeError(f"Unable to read {file_path}: {last_error}")

# opens one table with simple defaults
def read_table_smart(
    file_path: Path,
    nrows: int | None = None,
    usecols: list[str] | None = None,
) -> pd.DataFrame:
    return _read_csv_with_fallback(file_path, nrows=nrows, usecols=usecols)

# streams a table in small pieces
def iter_table_smart(
    file_path: Path,
    *,
    chunksize: int,
    usecols: list[str] | None = None,
    nrows: int | None = None,
):
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
        except Exception as exc:
            last_error = exc

    raise RuntimeError(f"Unable to iterate over {file_path}: {last_error}")

# cleans messy number text
def clean_numeric(series: pd.Series) -> pd.Series:
    s = series.astype(str).str.strip()

    s = s.str.replace("\u00a0", "", regex=False)
    s = s.str.replace("\u202f", "", regex=False)
    s = s.str.replace(" ", "", regex=False)
    s = s.str.replace(",", ".", regex=False)
    s = s.str.replace("Less than 5", "2", regex=False)
    s = s.replace({"": np.nan, "nan": np.nan, "None": np.nan, "?": np.nan})
    return pd.to_numeric(s, errors="coerce")

# parses dates written in mixed formats
def parse_any_date(series: pd.Series) -> pd.Series:
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

# merges grouped chunks into one table
def combine_grouped_frames(
    frames: list[pd.DataFrame],
    group_cols: list[str],
    value_cols: list[str],
) -> pd.DataFrame:
    if not frames:
        return pd.DataFrame(columns=[*group_cols, *value_cols])

    combined = pd.concat(frames, ignore_index=True)
    agg_map = {col: "sum" for col in value_cols}
    return combined.groupby(group_cols, as_index=False).agg(agg_map)

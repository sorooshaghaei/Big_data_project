"""Reusable transport analytics package exports.

This module provides the public API surface so notebook and script code
can import from one place instead of internal submodules.
"""

# Configuration objects used by scripts and notebooks.
from .config import PostgresConfig, ProjectPaths

# Feature-engineering entry point used after aggregation.
from .features import add_time_features

# Pipeline orchestration helpers.
from .pipeline import build_canonical_fact_table, run_local_pipeline

# Explicit export list for clean imports and static analysis.
__all__ = [
    "PostgresConfig",
    "ProjectPaths",
    "add_time_features",
    "build_canonical_fact_table",
    "run_local_pipeline",
]

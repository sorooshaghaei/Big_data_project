"""Compatibility entry point for baseline pipeline runs.

This script is intentionally small: it keeps the old entry point while
routing execution to the new reusable package.
"""

from __future__ import annotations

from pathlib import Path

from transport_analytics.pipeline import run_local_pipeline


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[1]
    artifacts = run_local_pipeline(root=project_root, sample_mode=True)
    print("Pipeline done")
    print("station rows:", len(artifacts.station_fact))
    print("daily rows:", len(artifacts.daily))
    print("featured rows:", len(artifacts.featured))
    print("enriched rows:", len(artifacts.enriched))

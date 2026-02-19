"""Compatibility entry point for baseline pipeline runs.

This script is intentionally small: it keeps the old entry point while
routing execution to the new reusable package.
"""

from __future__ import annotations

from pathlib import Path

from transport_analytics.pipeline import run_local_pipeline


if __name__ == "__main__":
    # Resolve project root from this file location.
    project_root = Path(__file__).resolve().parents[1]

    # Run in sample mode by default for quick iteration.
    daily, featured = run_local_pipeline(root=project_root, sample_mode=True)

    # Print compact execution summary.
    print("Pipeline done")
    print("daily rows:", len(daily))
    print("featured rows:", len(featured))

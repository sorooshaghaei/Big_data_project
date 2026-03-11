#!/usr/bin/env python3
"""Run the cleaned transport analytics workflow end to end."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Stage 1 + Stage 2 transport analytics workflow.")
    parser.add_argument("--sample", action="store_true", help="Use a reduced subset of the raw data.")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    os.environ.setdefault("MPLCONFIGDIR", "/tmp/mpl")
    sys.path.insert(0, str(root / "src"))

    from transport_analytics.methods import run_stage_workflow
    from transport_analytics.pipeline import run_local_pipeline

    artifacts = run_local_pipeline(root=root, sample_mode=args.sample)
    outputs = run_stage_workflow(artifacts, root=root)

    print("Workflow complete")
    print("sample_mode:", args.sample)
    print("station_fact_rows:", len(artifacts.station_fact))
    print("daily_rows:", len(artifacts.daily))
    print("selected_methods:", len(outputs["stage1_plan"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

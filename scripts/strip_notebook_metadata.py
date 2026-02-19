#!/usr/bin/env python3
"""Normalize Jupyter notebooks by stripping volatile metadata.

Usage:
  - Clean filter (stdin -> stdout):
      python3 scripts/strip_notebook_metadata.py clean
  - Diff textconv (file -> stdout):
      python3 scripts/strip_notebook_metadata.py textconv <path>
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _normalize_metadata(nb: dict) -> dict:
    """Keep only stable notebook metadata fields.

    Why:
    - Avoid noisy diffs caused by local Jupyter/kernel environment changes.
    - Preserve only metadata needed for opening/running the notebook.
    """
    meta = nb.get("metadata") or {}

    # Keep only minimal top-level metadata.
    normalized_top = {}
    kernelspec = meta.get("kernelspec") or {}
    if kernelspec:
        ks = {}
        if "name" in kernelspec:
            ks["name"] = kernelspec["name"]
        # `display_name` is required by notebook schema; keep it stable.
        ks["display_name"] = "Python 3"
        if ks:
            normalized_top["kernelspec"] = ks

    language_info = meta.get("language_info") or {}
    if language_info and "name" in language_info:
        normalized_top["language_info"] = {"name": language_info["name"]}

    nb["metadata"] = normalized_top

    # Strip per-cell metadata except tags (tags are often semantically useful).
    for cell in nb.get("cells", []):
        cell_meta = cell.get("metadata") or {}
        normalized_cell_meta = {}
        tags = cell_meta.get("tags")
        if tags:
            normalized_cell_meta["tags"] = tags
        cell["metadata"] = normalized_cell_meta

    return nb


def _loads_notebook(raw: str) -> dict:
    """Parse notebook JSON string."""
    return json.loads(raw)


def _dumps_notebook(nb: dict) -> str:
    """Serialize notebook with stable formatting."""
    return json.dumps(nb, ensure_ascii=False, indent=1) + "\n"


def clean_from_stdin() -> int:
    """Git clean-filter entry point (reads notebook content from stdin)."""
    raw = sys.stdin.read()
    if not raw.strip():
        return 0

    try:
        nb = _loads_notebook(raw)
    except Exception:
        # If input is not valid JSON, return it unchanged.
        sys.stdout.write(raw)
        return 0

    nb = _normalize_metadata(nb)
    sys.stdout.write(_dumps_notebook(nb))
    return 0


def textconv_from_path(path: str) -> int:
    """Git textconv entry point (used to make notebook diffs readable/stable)."""
    p = Path(path)
    raw = p.read_text(encoding="utf-8", errors="ignore")

    try:
        nb = _loads_notebook(raw)
    except Exception:
        # If file is not valid notebook JSON, print raw content.
        sys.stdout.write(raw)
        return 0

    nb = _normalize_metadata(nb)
    sys.stdout.write(_dumps_notebook(nb))
    return 0


def main() -> int:
    """Command-line entry point."""
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    # Clean-filter mode used by git on checkout/add.
    sub.add_parser("clean")

    # Text conversion mode used by git diff viewer.
    p_textconv = sub.add_parser("textconv")
    p_textconv.add_argument("path")

    args = parser.parse_args()

    if args.cmd == "clean":
        return clean_from_stdin()
    if args.cmd == "textconv":
        return textconv_from_path(args.path)

    return 1


if __name__ == "__main__":
    raise SystemExit(main())

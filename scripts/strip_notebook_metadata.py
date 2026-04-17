#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# keeps only the notebook metadata we want to keep
def _normalize_metadata(nb: dict) -> dict:
    meta = nb.get("metadata") or {}

    normalized_top = {}
    kernelspec = meta.get("kernelspec") or {}
    if kernelspec:
        ks = {}
        if "name" in kernelspec:
            ks["name"] = kernelspec["name"]

        ks["display_name"] = "Python 3"
        if ks:
            normalized_top["kernelspec"] = ks

    language_info = meta.get("language_info") or {}
    if language_info and "name" in language_info:
        normalized_top["language_info"] = {"name": language_info["name"]}

    nb["metadata"] = normalized_top

    for cell in nb.get("cells", []):
        cell_meta = cell.get("metadata") or {}
        normalized_cell_meta = {}
        tags = cell_meta.get("tags")
        if tags:
            normalized_cell_meta["tags"] = tags
        cell["metadata"] = normalized_cell_meta

    return nb

# reads notebook text into json
def _loads_notebook(raw: str) -> dict:
    return json.loads(raw)

# writes notebook json back to text
def _dumps_notebook(nb: dict) -> str:
    return json.dumps(nb, ensure_ascii=False, indent=1) + "\n"

# cleans a notebook passed through stdin
def clean_from_stdin() -> int:
    raw = sys.stdin.read()
    if not raw.strip():
        return 0

    try:
        nb = _loads_notebook(raw)
    except Exception:

        sys.stdout.write(raw)
        return 0

    nb = _normalize_metadata(nb)
    sys.stdout.write(_dumps_notebook(nb))
    return 0

# shows git a cleaner notebook view
def textconv_from_path(path: str) -> int:
    p = Path(path)
    raw = p.read_text(encoding="utf-8", errors="ignore")

    try:
        nb = _loads_notebook(raw)
    except Exception:

        sys.stdout.write(raw)
        return 0

    nb = _normalize_metadata(nb)
    sys.stdout.write(_dumps_notebook(nb))
    return 0

# handles the notebook cleaner command
def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("clean")

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

#!/bin/bash

# Fail fast on errors, undefined vars, and failed pipelines.
set -euo pipefail

# -----------------------------------------------------------------------------
# Setup script for notebook metadata filters in this repository.
#
# Why this exists:
# - Jupyter often writes local machine metadata into .ipynb files.
# - That metadata creates noisy diffs and confusing merge conflicts.
# - This script configures local git filters so notebook metadata is cleaned
#   automatically when notebooks are added to git.
#
# Usage:
#   bash scripts/setup_git_filters.sh
#   bash scripts/setup_git_filters.sh --normalize
#
# --normalize:
#   Also rewrites currently tracked notebooks using the cleaner so all existing
#   notebook files follow the same format.
# -----------------------------------------------------------------------------

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

NORMALIZE=false
if [[ "${1:-}" == "--normalize" ]]; then
  NORMALIZE=true
fi

# Check that required commands exist.
if ! command -v git >/dev/null 2>&1; then
  echo "Error: git is not installed or not in PATH."
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "Error: python3 is not installed or not in PATH."
  exit 1
fi

# Move into repo root so git config is local to this project.
cd "$REPO_ROOT"

# Validate this is a git repository.
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Error: $REPO_ROOT is not a git repository."
  exit 1
fi

# Validate cleaner script exists.
if [[ ! -f "scripts/strip_notebook_metadata.py" ]]; then
  echo "Error: scripts/strip_notebook_metadata.py was not found."
  exit 1
fi

# Configure local (repository-level) git filter and diff settings.
# This does NOT change global git config.
git config filter.nbstrip.clean "python3 scripts/strip_notebook_metadata.py clean"
git config filter.nbstrip.smudge cat
git config filter.nbstrip.required true
git config diff.nbstrip.textconv "python3 scripts/strip_notebook_metadata.py textconv"
git config diff.nbstrip.cachetextconv true

echo "Configured local notebook metadata filter."

# Optional: normalize currently tracked notebooks.
if [[ "$NORMALIZE" == "true" ]]; then
  echo "Normalizing tracked notebooks..."

  while IFS= read -r nb_path; do
    [[ -z "$nb_path" ]] && continue

    tmp_file="${nb_path}.tmp_nbstrip"
    python3 scripts/strip_notebook_metadata.py clean < "$nb_path" > "$tmp_file"
    mv "$tmp_file" "$nb_path"
    echo "  normalized: $nb_path"
  done < <(git ls-files '*.ipynb')

  echo "Notebook normalization complete."
fi

# Print a quick summary so beginners can verify setup.
echo
echo "Verification:"
echo "  filter.clean:  $(git config --get filter.nbstrip.clean)"
echo "  diff.textconv: $(git config --get diff.nbstrip.textconv)"

echo
echo "Next steps:"
echo "  1) Keep .ipynb files tracked in git."
echo "  2) Stage notebook changes normally: git add notebooks/*.ipynb"
echo "  3) Optional once per clone: bash scripts/setup_git_filters.sh --normalize"

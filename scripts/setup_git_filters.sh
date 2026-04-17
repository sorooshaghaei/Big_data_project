#!/bin/bash
# script sets up the notebook git filter
# it removes noisy notebook metadata before git stores the file
# use --normalize if you also want to clean tracked notebooks now

# stops right away if something goes wrong
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

NORMALIZE=false
if [[ "${1:-}" == "--normalize" ]]; then
  NORMALIZE=true
fi

# checks that git and python3 are installed
if ! command -v git >/dev/null 2>&1; then
  echo "Error: git is not installed or not in PATH."
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "Error: python3 is not installed or not in PATH."
  exit 1
fi

# moves to the repo so git config stays local
cd "$REPO_ROOT"

# checks that this folder is a git repo
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Error: $REPO_ROOT is not a git repository."
  exit 1
fi

# checks that the notebook cleaner script exists
if [[ ! -f "scripts/strip_notebook_metadata.py" ]]; then
  echo "Error: scripts/strip_notebook_metadata.py was not found."
  exit 1
fi

# sets the local git filter and diff rules
# only changes git settings for this repo
git config filter.nbstrip.clean "python3 scripts/strip_notebook_metadata.py clean"
git config filter.nbstrip.smudge cat
git config filter.nbstrip.required true
git config diff.nbstrip.textconv "python3 scripts/strip_notebook_metadata.py textconv"
git config diff.nbstrip.cachetextconv true

echo "Configured local notebook metadata filter."

# can also clean notebooks that are already tracked
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

# prints a quick check at the end
echo
echo "Verification:"
echo "  filter.clean:  $(git config --get filter.nbstrip.clean)"
echo "  diff.textconv: $(git config --get diff.nbstrip.textconv)"

echo
echo "Next steps:"
echo "  1) Keep .ipynb files tracked in git."
echo "  2) Stage notebook changes normally: git add notebooks/*.ipynb"
echo "  3) Optional once per clone: bash scripts/setup_git_filters.sh --normalize"

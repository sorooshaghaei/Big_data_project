# Notebook Metadata Filter Setup (For Teammates)

If you are new to Git and notebooks, run this once after cloning the repository.

## Why this is needed

Jupyter notebooks (`.ipynb`) can save machine-specific metadata (kernel display name, local environment hints, etc.).
That metadata creates noisy diffs and can make merges harder.

This project includes a cleaner script that keeps notebook metadata minimal and stable.

## One-command setup

From the project root:

```bash
bash scripts/setup_git_filters.sh
```

This configures **local git settings for this repository only**.
It does not change your global git config.

## Optional: normalize all existing tracked notebooks

```bash
bash scripts/setup_git_filters.sh --normalize
```

Use this when you first join the project to align notebook formatting with the team standard.

## How to work normally after setup

```bash
git add notebooks/*.ipynb
git commit -m "Update analysis notebook"
```

No extra steps are needed. The filter is applied automatically.

## Quick check

```bash
git config --get filter.nbstrip.clean
git config --get diff.nbstrip.textconv
```

You should see commands that reference:
- `scripts/strip_notebook_metadata.py clean`
- `scripts/strip_notebook_metadata.py textconv`

## Troubleshooting

- If `python3` is missing: install Python 3 first.
- If command fails: make sure you run it inside the repo root.
- If notebooks still look noisy: rerun with `--normalize`.

#!/bin/bash

# Exit on first error, fail on unset vars, and fail on pipeline errors.
set -euo pipefail

# -----------------------------------------------------------------------------
# This script downloads project datasets and keeps only the required files.
# Prerequisites:
#   - curl
#   - kaggle CLI configured (`kaggle.json` credentials)
#   - unzip
# -----------------------------------------------------------------------------

# Resolve paths relative to this script location.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="$SCRIPT_DIR/datasets"
KAGGLE_SLUG="gatandubuc/public-transport-traffic-data-in-france"

# Create destination directory if missing.
mkdir -p "$TARGET_DIR"

echo "--- Step 1: Downloading IDFM dataset ---"

# Official API export URL for IDFM validations dataset.
IDFM_API_URL="https://data.iledefrance-mobilites.fr/api/explore/v2.1/catalog/datasets/validations-reseau-surface-nombre-validations-par-jour-1er-trimestre/exports/csv?use_labels=true&csv_separator=%3B"

# Download CSV (follow redirects with -L).
curl -L -o "$TARGET_DIR/idfm_validations_surface.csv" "$IDFM_API_URL"

echo "--- Step 2: Downloading Kaggle dataset ---"

# Download the Kaggle archive into /datasets.
kaggle datasets download -d "$KAGGLE_SLUG" -p "$TARGET_DIR"

echo "--- Step 3: Unpacking and filtering Kaggle files ---"
KAGGLE_ZIP="$TARGET_DIR/public-transport-traffic-data-in-france.zip"

if [ -f "$KAGGLE_ZIP" ]; then
    # Extract in a temporary folder to avoid polluting /datasets.
    mkdir -p "$TARGET_DIR/temp_kaggle"
    unzip -q -o "$KAGGLE_ZIP" -d "$TARGET_DIR/temp_kaggle"

    # Move only the two files used in this project.
    mv "$TARGET_DIR/temp_kaggle/Travel_titles_validations_in_Paris_and_suburbs.csv" "$TARGET_DIR/"
    mv "$TARGET_DIR/temp_kaggle/Regularities_by_liaisons_Trains_France.csv" "$TARGET_DIR/"

    # Cleanup temporary artifacts.
    rm "$KAGGLE_ZIP"
    rm -rf "$TARGET_DIR/temp_kaggle"
    echo "Successfully extracted and filtered Kaggle files."
else
    echo "Error: Kaggle zip file not found."
fi

echo "--- Step 4: Generating citations.txt ---"

# Generate a simple provenance file for downloaded datasets.
cat <<EOF > "$TARGET_DIR/citations.txt"
Dataset 1: Validations sur le réseau de surface (1er trimestre)
Link: https://data.iledefrance-mobilites.fr/explore/dataset/validations-reseau-surface-nombre-validations-par-jour-1er-trimestre/

Dataset 2: Public transport traffic data in France
Link: https://www.kaggle.com/datasets/gatandubuc/public-transport-traffic-data-in-france
EOF

echo "Done. Files are ready in: $TARGET_DIR"
ls -lh "$TARGET_DIR"

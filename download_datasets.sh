#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="$SCRIPT_DIR/datasets"
KAGGLE_SLUG="gatandubuc/public-transport-traffic-data-in-france"

# Create directory
mkdir -p "$TARGET_DIR"

echo "--- Step 1: Downloading IDFM dataset ---"
# Using the stable API export link (v2.1)
IDFM_API_URL="https://data.iledefrance-mobilites.fr/api/explore/v2.1/catalog/datasets/validations-reseau-surface-nombre-validations-par-jour-1er-trimestre/exports/csv?use_labels=true&csv_separator=%3B"

# Using curl with -L to follow redirects and -o to save
curl -L -o "$TARGET_DIR/idfm_validations_surface.csv" "$IDFM_API_URL"

echo "--- Step 2: Downloading Kaggle dataset ---"
# Downloading via the Kaggle CLI
kaggle datasets download -d "$KAGGLE_SLUG" -p "$TARGET_DIR"

echo "--- Step 3: Unpacking and Filtering Kaggle Files ---"
KAGGLE_ZIP="$TARGET_DIR/public-transport-traffic-data-in-france.zip"

if [ -f "$KAGGLE_ZIP" ]; then
    # Create a temp folder for extraction
    mkdir -p "$TARGET_DIR/temp_kaggle"
    unzip -q -o "$KAGGLE_ZIP" -d "$TARGET_DIR/temp_kaggle"
    
    # Move ONLY the requested files to the /datasets folder
    mv "$TARGET_DIR/temp_kaggle/Travel_titles_validations_in_Paris_and_suburbs.csv" "$TARGET_DIR/"
    mv "$TARGET_DIR/temp_kaggle/Regularities_by_liaisons_Trains_France.csv" "$TARGET_DIR/"
    
    # Clean up zip and temp folder
    rm "$KAGGLE_ZIP"
    rm -rf "$TARGET_DIR/temp_kaggle"
    echo "Successfully extracted and filtered Kaggle files."
else
    echo "❌ Error: Kaggle zip file not found."
fi

echo "--- Step 4: Generating citations.txt ---"
cat <<EOF > "$TARGET_DIR/citations.txt"
Dataset 1: Validations sur le réseau de surface (1er trimestre)
Link: https://data.iledefrance-mobilites.fr/explore/dataset/validations-reseau-surface-nombre-validations-par-jour-1er-trimestre/

Dataset 2: Public transport traffic data in France
Link: https://www.kaggle.com/datasets/gatandubuc/public-transport-traffic-data-in-france
EOF

echo "✅ Done! Your files are ready in: $TARGET_DIR"
ls -lh "$TARGET_DIR"
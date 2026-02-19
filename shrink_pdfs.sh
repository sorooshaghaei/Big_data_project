#!/bin/bash

# Exit on first error, fail on unset vars, and fail on pipeline errors.
set -euo pipefail

# -----------------------------------------------------------------------------
# Compress every PDF in the repository (except already compressed files).
# Output files are written as *_compressed.pdf next to originals.
# -----------------------------------------------------------------------------

# Target maximum size in KB (2048 KB = 2 MB).
TARGET_KB=2048

# Find all PDFs excluding existing compressed outputs.
find . -type f -iname "*.pdf" ! -name "*_compressed.pdf" | while read -r file; do
    # Build output filename from input path.
    base_name="${file%.*}"
    out_file="${base_name}_compressed.pdf"

    # Skip file if compressed version already exists.
    if [ -f "$out_file" ]; then
        echo "Skipping: $out_file already exists."
        continue
    fi

    # Skip files already under target size.
    actual_size=$(du -k "$file" | cut -f1)
    if [ "$actual_size" -le "$TARGET_KB" ]; then
        echo "Already under 2MB: $file"
        continue
    fi

    echo "Compressing: $file"

    # First attempt: medium compression profile.
    gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/ebook \
       -dNOPAUSE -dQUIET -dBATCH -sOutputFile="$out_file" "$file"

    if [ -f "$out_file" ]; then
        new_size=$(du -k "$out_file" | cut -f1)

        # Second attempt: stronger compression profile if still too large.
        if [ "$new_size" -gt "$TARGET_KB" ]; then
            echo "Still above target (${new_size} KB). Retrying with stronger compression..."
            gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/screen \
               -dNOPAUSE -dQUIET -dBATCH -sOutputFile="$out_file" "$file"
            new_size=$(du -k "$out_file" | cut -f1)
        fi

        echo "Done: $out_file (${new_size} KB)"
    else
        echo "Error: Could not process $file"
    fi

    echo "--------------------------------"
done

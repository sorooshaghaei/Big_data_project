#!/bin/bash
# script compresses pdf files in the repo
# it saves a new _compressed file next to each one

# stops right away if a command fails
set -euo pipefail

# target size in kb
TARGET_KB=2048

# looks through pdf files that are not compressed yet
find . -type f -iname "*.pdf" ! -name "*_compressed.pdf" | while read -r file; do
    # makes the new compressed file name
    base_name="${file%.*}"
    out_file="${base_name}_compressed.pdf"

    # skips the file if a compressed copy is already there
    if [ -f "$out_file" ]; then
        echo "Skipping: $out_file already exists."
        continue
    fi

    # skips files that are already small enough
    actual_size=$(du -k "$file" | cut -f1)
    if [ "$actual_size" -le "$TARGET_KB" ]; then
        echo "Already under 2MB: $file"
        continue
    fi

    echo "Compressing: $file"

    # tries medium compression first
    gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/ebook \
       -dNOPAUSE -dQUIET -dBATCH -sOutputFile="$out_file" "$file"

    if [ -f "$out_file" ]; then
        new_size=$(du -k "$out_file" | cut -f1)

        # tries stronger compression if the file is still too big
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

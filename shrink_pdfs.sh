#!/bin/bash

# Target size in Kilobytes (2048 KB = 2MB)
TARGET_KB=2048

# Find all PDFs, excluding ones we already compressed
find . -type f -iname "*.pdf" ! -name "*_compressed.pdf" | while read -r file; do
    # Create the new filename: path/to/filename_compressed.pdf
    base_name="${file%.*}"
    out_file="${base_name}_compressed.pdf"
    
    # 1. Check if the compressed version already exists
    if [ -f "$out_file" ]; then
        echo "⏭️  Skipping: $out_file already exists."
        continue
    fi

    # 2. Check if original is already small enough
    actual_size=$(du -k "$file" | cut -f1)
    if [ "$actual_size" -le "$TARGET_KB" ]; then
        echo "✅ Already under 2MB: $file ($(expr $actual_size / 1024) MB). Skipping."
        continue
    fi

    echo "🚀 Compressing: $file ($(expr $actual_size / 1024) MB)"
    
    # Try Medium Quality (150 DPI)
    gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/ebook \
       -dNOPAUSE -dQUIET -dBATCH -sOutputFile="$out_file" "$file"
    
    if [ -f "$out_file" ]; then
        new_size=$(du -k "$out_file" | cut -f1)
        
        # If still > 2MB, try Low Quality (72 DPI)
        if [ "$new_size" -gt "$TARGET_KB" ]; then
            echo "⚠️  Still over 2MB ($new_size KB). Retrying with max compression..."
            gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/screen \
               -dNOPAUSE -dQUIET -dBATCH -sOutputFile="$out_file" "$file"
            new_size=$(du -k "$out_file" | cut -f1)
        fi
        
        echo "✨ Done: $out_file ($new_size KB)"
    else
        echo "❌ Error: Could not process $file."
    fi
    echo "--------------------------------"
done
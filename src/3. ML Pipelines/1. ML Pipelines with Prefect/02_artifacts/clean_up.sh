#!/bin/bash
# Clean up intermediate and output artifacts
# Preserves input data in 01_input/

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DATA_DIR="$SCRIPT_DIR/data"

echo "Cleaning up artifacts..."

# Remove intermediate files
rm -f "$DATA_DIR/02_intermediate"/*.csv
echo "  Cleared 02_intermediate/"

# Remove output files
rm -f "$DATA_DIR/03_output"/*.csv
echo "  Cleared 03_output/"

echo "Done! Input data in 01_input/ preserved."

#!/bin/bash
# Simple runner script for translate-pptx
# Usage: ./run.sh <input.pptx> <target_language> [model]

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Add src directory to PYTHONPATH
export PYTHONPATH="${SCRIPT_DIR}/src:${PYTHONPATH}"

# Run the Python module
python3 -m translate_pptx test.pptx English


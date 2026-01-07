#!/bin/bash

# ==================================================
# Pipeline runner script
#
# Usage:
#   ./scripts/run_single_pipeline.sh <path_to_pipeline> <runs> [input_strings]
#
# Parameters:
#   <path_to_pipeline>  - Path to the Python pipeline file (relative to project root)
#   <runs>              - Number of times to run the pipeline
#   [input_strings]     - Optional: newline-separated inputs for interactive prompts
#                         Use $'\n' to separate multiple inputs
#
# Examples:
#   ./scripts/run_single_pipeline.sh examples/trip_planner/pipeline.py 3
#   ./scripts/run_single_pipeline.sh examples/input_checker_pipeline.py 3 "Paris"
#   ./scripts/run_single_pipeline.sh examples/input_checker_pipeline.py 3 $'Paris\n5 days\nbudget'
#
# Output:
#   - Real-time terminal output during execution
#   - Logs are handled by Python's logging system
# ==============================================

# Get project root (parent directory of where this script is located)
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Input validation
if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Error: Pipeline path and runs are required."
    echo ""
    echo "Usage: $0 <path_to_pipeline> <runs> [input_strings]"
    echo ""
    echo "Examples:"
    echo "  $0 examples/trip_planner/pipeline.py 3"
    echo "  $0 examples/conditioning_pipeline.py 5"
    exit 1
fi

PIPELINE_PATH="$1"
RUNS="$2"
INPUT_STRINGS="$3"

# Validate pipeline file exists
if [ ! -f "$PIPELINE_PATH" ]; then
    echo "Error: Pipeline file not found: $PIPELINE_PATH"
    exit 1
fi

# Extract pipeline name for display
PIPELINE_NAME=$(basename "$PIPELINE_PATH" .py)

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Running pipeline: $PIPELINE_PATH"
echo "Number of runs: $RUNS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

for ((i = 1; i <= RUNS; i++)); do
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Run $i of $RUNS"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    if [ -n "$INPUT_STRINGS" ]; then
        poetry run python3 -u "$PIPELINE_PATH" 2>&1 <<< "$INPUT_STRINGS"
    else
        poetry run python3 -u "$PIPELINE_PATH" 2>&1
    fi
    
    echo ""
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "All $RUNS runs completed."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

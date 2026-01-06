#!/bin/bash

# ==================================================
# Real-time logging script for a single pipeline run
#
# Usage:
#   ./scripts/run_single_pipeline.sh <path_to_pipeline> <log_folder> <runs> [input_strings]
#
# Parameters:
#   <path_to_pipeline>  - Path to the Python pipeline file (relative to project root)
#   <log_folder>        - Subfolder name inside logs/ directory
#   <runs>              - Number of times to run the pipeline
#   [input_strings]     - Optional: newline-separated inputs for interactive prompts
#                         Use $'\n' to separate multiple inputs
#
# Examples:
#   ./scripts/run_single_pipeline.sh examples/trip_planner/pipeline.py trip_planner 3
#   ./scripts/run_single_pipeline.sh examples/input_checker_pipeline.py input_checker 3 "Paris"
#   ./scripts/run_single_pipeline.sh examples/input_checker_pipeline.py input_checker 3 $'Paris\n5 days\nbudget'
#
# Output:
#   - Real-time terminal output during execution
#   - Logs saved to: logs/<log_folder>/<pipeline_name>_run_<n>_<timestamp>.log
# ==============================================

# Get project root (parent directory of where this script is located)
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Input validation
if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ]; then
    echo "Error: All three parameters are required."
    echo ""
    echo "Usage: $0 <path_to_pipeline> <log_folder> <runs>"
    echo ""
    echo "Examples:"
    echo "  $0 examples/trip_planner/pipeline.py trip_planner 3"
    echo "  $0 examples/conditioning_pipeline.py conditioning 5"
    echo ""
    echo "Logs will be saved to: logs/<log_folder>/"
    exit 1
fi

PIPELINE_PATH="$1"
LOG_SUBDIR="$2"
RUNS="$3"
INPUT_STRINGS="$4"

# Full log directory path
LOG_DIR="$PROJECT_ROOT/logs/$LOG_SUBDIR"

# Validate pipeline file exists
if [ ! -f "$PIPELINE_PATH" ]; then
    echo "Error: Pipeline file not found: $PIPELINE_PATH"
    exit 1
fi

# Extract pipeline name for log file naming
PIPELINE_NAME=$(basename "$PIPELINE_PATH" .py)

mkdir -p "$LOG_DIR"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Running pipeline: $PIPELINE_PATH"
echo "Log directory: $LOG_DIR"
echo "Number of runs: $RUNS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

for ((i = 1; i <= RUNS; i++)); do
    TIMESTAMP=$(date +'%d_%m_%y__%H_%M_%S')
    LOG_FILE="$LOG_DIR/${PIPELINE_NAME}_run_${i}_${TIMESTAMP}.log"

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Run $i of $RUNS → $LOG_FILE"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    if [ -n "$INPUT_STRINGS" ]; then
        poetry run python3 -u "$PIPELINE_PATH" 2>&1 <<< "$INPUT_STRINGS" | tee "$LOG_FILE"
    else
        poetry run python3 "$PIPELINE_PATH" 2>&1 | tee "$LOG_FILE"
    fi
    
    echo ""
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "All $RUNS runs completed."
echo "Logs saved in: $LOG_DIR"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

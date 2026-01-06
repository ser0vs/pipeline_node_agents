#!/bin/bash

# =============================================================
# Run all smoke pipelines and save logs (smoke tests)
#
# Usage: ./run_smoke_pipelines.sh [number_of_runs_per_pipeline]
# =============================================================

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

START_DATE=$(date -d "+3 days" +"%d %B %Y")
END_DATE=$(date -d "+10 days" +"%d %B %Y")

echo "╔══════════════════════════════════════════╗"
echo "║          Running Smoke Pipelines         ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# Number of runs per pipeline (default: 1)
RUNS=${1:-1}

echo "Runs per pipeline: $RUNS"
echo ""

SINGLE_PIPELINE_SCRIPT="$PROJECT_ROOT/scripts/run_single_pipeline.sh"


# echo "▶ Running Random Mean Pipeline..."
# "$SINGLE_PIPELINE_SCRIPT" "$PROJECT_ROOT/examples/random_mean_pipeline.py" random_mean "$RUNS"
# echo ""

# echo "▶ Running First Conditioning Pipeline..."
# "$SINGLE_PIPELINE_SCRIPT" "$PROJECT_ROOT/examples/conditioning_pipeline.py" first_conditioning "$RUNS"
# echo ""

# echo "▶ Running Input Checker Pipeline..."
# "$SINGLE_PIPELINE_SCRIPT" "$PROJECT_ROOT/examples/input_checker_pipeline.py" input_checker "$RUNS" "Munich, Vienna, Zurich"
# echo ""

# echo "▶ Running Search and Summarize Pipeline..."
# "$SINGLE_PIPELINE_SCRIPT" "$PROJECT_ROOT/examples/search_and_summarize.py" search_and_summarize "$RUNS"
# echo ""

echo "▶ Running Trip Planner Pipeline..."
"$SINGLE_PIPELINE_SCRIPT" "$PROJECT_ROOT/examples/trip_planner/pipeline.py" trip_planner "$RUNS" $'Madrid, Dubai\n'"${START_DATE}"$'\n'"${END_DATE}"
echo ""


echo "╔══════════════════════════════════════════╗"
echo "║         All Pipelines Completed!         ║"
echo "╚══════════════════════════════════════════╝"
echo ""
echo "Logs saved in: $PROJECT_ROOT/logs/"
ls -la "$PROJECT_ROOT/logs/"

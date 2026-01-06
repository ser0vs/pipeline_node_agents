#!/bin/bash

# ==============================================
# Run all example pipelines and save logs
#
# Usage: ./run_all_examples.sh [number_of_runs_per_example]
# ==============================================

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "╔══════════════════════════════════════════╗"
echo "║       Running All Example Pipelines      ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# Number of runs per example (default: 1)
RUNS=${1:-1}

echo "Runs per example: $RUNS"
echo ""

echo "▶ Running First Conditioning Pipeline..."
"$PROJECT_ROOT/run_with_final_logs.sh" examples/first_conditining_pipeline.py first_conditioning "$RUNS"
echo ""

echo "▶ Running Input Checker Pipeline..."
"$PROJECT_ROOT/run_with_final_logs.sh" examples/input_checker_pipeline.py input_checker "$RUNS" "Munich, Vienna, Zurich"
echo ""

if [ -f "$PROJECT_ROOT/examples/random_mean_pipeline.py" ]; then
    echo "▶ Running Random Mean Pipeline..."
    "$PROJECT_ROOT/run_with_final_logs.sh" examples/random_mean_pipeline.py random_mean "$RUNS"
    echo ""
fi


echo "▶ Running Trip Planner Pipeline..."
"$PROJECT_ROOT/run_with_final_logs.sh" examples/trip_planner/pipeline.py trip_planner "$RUNS"
echo ""


echo "╔══════════════════════════════════════════╗"
echo "║         All Examples Completed!          ║"
echo "╚══════════════════════════════════════════╝"
echo ""
echo "Logs saved in: $PROJECT_ROOT/logs/"
ls -la "$PROJECT_ROOT/logs/"

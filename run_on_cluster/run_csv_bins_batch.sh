#!/bin/bash

# CSV Bin Batch Runner (using bin IDs - row indices)
# Usage: ./run_csv_bins_batch.sh scenario_folder scenario_name [csv_file] [bin_ids...]
#
# Examples:
#   ./run_csv_bins_batch.sh scenarios testcase                     # Run all bins
#   ./run_csv_bins_batch.sh scenarios testcase input_table.csv     # Run all bins with specific CSV
#   ./run_csv_bins_batch.sh scenarios testcase input_table.csv 0 1 2  # Run specific bin IDs

set -e

# Check if we have at least 2 arguments
if [ $# -lt 2 ]; then
    echo "Usage: $0 scenario_folder scenario_name [csv_file] [bin_ids...]"
    echo ""
    echo "Note: bin_ids are row indices (0-based) in the CSV file"
    echo ""
    echo "Examples:"
    echo "  $0 scenarios testcase                        # Run all bins"
    echo "  $0 scenarios testcase input_table.csv        # Run all bins with specific CSV"
    echo "  $0 scenarios testcase input_table.csv 0 1 2  # Run specific bin IDs"
    exit 1
fi

SCENARIO_FOLDER=$1
SCENARIO_NAME=$2

# Default CSV file
CSV_FILE="input_table.csv"

# Check if third argument is a CSV file or bin ID
if [ $# -gt 2 ]; then
    if [[ $3 == *.csv ]]; then
        CSV_FILE=$3
        shift 3  # Remove first 3 arguments, remaining are bin IDs
    else
        shift 2  # Remove first 2 arguments, remaining are bin IDs (starting from $3)
    fi
else
    shift 2  # Remove first 2 arguments
fi

BIN_IDS=("$@")

echo "Running CSV bins with scenario: $SCENARIO_NAME"
echo "CSV file: $CSV_FILE"

# Check if CSV file exists
if [ ! -f "$CSV_FILE" ]; then
    echo "Error: CSV file '$CSV_FILE' not found!"
    exit 1
fi

# If no specific bin IDs provided, create a sequence from 0 to (number of data rows - 1)
if [ ${#BIN_IDS[@]} -eq 0 ]; then
    echo "No specific bin IDs provided, generating all row indices from CSV..."
    # Count data rows (excluding header)
    NUM_ROWS=$(tail -n +2 "$CSV_FILE" | wc -l)
    BIN_IDS=($(seq 0 $((NUM_ROWS-1))))
    echo "Found $NUM_ROWS data rows, bin IDs: ${BIN_IDS[@]}"
fi

# Create results directory
mkdir -p "results_$SCENARIO_NAME"

echo "Starting batch processing of ${#BIN_IDS[@]} bins..."
echo "=========================================="

SUCCESSFUL_RUNS=0
FAILED_RUNS=0
FAILED_BINS=()

for bin_id in "${BIN_IDS[@]}"; do
    echo ""
    echo "Processing bin ID $bin_id..."
    echo "----------------------------------------"
    
    if python run_csv_bin.py "$bin_id" "$SCENARIO_FOLDER" "$SCENARIO_NAME" "$CSV_FILE"; then
        echo "✓ Successfully completed bin ID $bin_id"
        ((SUCCESSFUL_RUNS++))
    else
        echo "✗ Failed to process bin ID $bin_id"
        ((FAILED_RUNS++))
        FAILED_BINS+=($bin_id)
    fi
done

echo ""
echo "=========================================="
echo "Batch processing complete!"
echo "Successful runs: $SUCCESSFUL_RUNS"
echo "Failed runs: $FAILED_RUNS"

if [ $FAILED_RUNS -gt 0 ]; then
    echo "Failed bin IDs: ${FAILED_BINS[@]}"
    echo ""
    echo "To retry failed bin IDs:"
    echo "$0 $SCENARIO_FOLDER $SCENARIO_NAME $CSV_FILE ${FAILED_BINS[@]}"
fi

echo ""
echo "Results saved in: results_$SCENARIO_NAME/"

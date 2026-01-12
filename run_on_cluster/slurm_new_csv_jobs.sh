#!/bin/bash
#SBATCH --job-name=new_csv_bin_job
#SBATCH --output=logs/new_csv_bin_%j.out  # Log file for each job
#SBATCH --error=logs/new_csv_bin_%j.err   # Error log
#SBATCH --time=1:00:00           # Adjust time limit
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1         # Adjust CPU usage
#SBATCH --mem=1gb                 # Adjust memory
#SBATCH --partition=rigel        # Adjust partition name

# New CSV Bin SLURM Job Submitter (using new_mb_model)
# Usage: 
#   ./slurm_new_csv_jobs.sh                                    # Use default configuration
#   ./slurm_new_csv_jobs.sh scenario_name                      # Run all bins with custom scenario
#   ./slurm_new_csv_jobs.sh scenario_name "bin_id1 bin_id2"    # Run specific bin IDs with custom scenario
#
# Examples:
#   ./slurm_new_csv_jobs.sh                                    # Default: do_nothing_K scenario, all bins
#   ./slurm_new_csv_jobs.sh capability_test_K                  # Run all bins with capability_test_K scenario
#   ./slurm_new_csv_jobs.sh do_nothing_K "1 2 5 10"             # Run bin IDs 1,2,5,10 with do_nothing_K scenario

# Load modules (if required)


# Activate virtual environment
module load IMAS
source /home/ITER/llealsa/miniconda3/etc/profile.d/conda.sh
conda activate PFC-TT
export PATH="/home/ITER/llealsa/miniconda3/envs/PFC-TT/bin:$PATH"

unset PYTHONPATH
export PYTHONNOUSERSITE=1

module unload SciPy-bundle        2>/dev/null
module unload Python-bundle-PyPI  2>/dev/null
module unload Python              2>/dev/null
module unload numpy               2>/dev/null
module unload mpi4py              2>/dev/null
module unload scifem              2>/dev/null

# Load other modules

# Default configuration
DEFAULT_SCENARIO_FOLDER="scenarios"
DEFAULT_SCENARIO_NAME="do_nothing_K"
DEFAULT_CSV_FILE="input_files/input_table.csv"

# Parse command line arguments
if [ $# -eq 0 ]; then
    # No arguments: use defaults
    SCENARIO_FOLDER="$DEFAULT_SCENARIO_FOLDER"
    SCENARIO_NAME="$DEFAULT_SCENARIO_NAME"
    CSV_FILE="$DEFAULT_CSV_FILE"
    BIN_IDS=""
    echo "Using default configuration:"
elif [ $# -eq 1 ]; then
    # One argument: custom scenario, all bins
    SCENARIO_FOLDER="$DEFAULT_SCENARIO_FOLDER"
    SCENARIO_NAME="$1"
    CSV_FILE="$DEFAULT_CSV_FILE"
    BIN_IDS=""
    echo "Using custom scenario with all bins:"
elif [ $# -eq 2 ]; then
    # Two arguments: custom scenario and specific bin IDs
    SCENARIO_FOLDER="$DEFAULT_SCENARIO_FOLDER"
    SCENARIO_NAME="$1"
    CSV_FILE="$DEFAULT_CSV_FILE"
    BIN_IDS="$2"
    echo "Using custom scenario with specific bin IDs:"
else
    echo "Usage: $0 [scenario_name] [\"bin_id1 bin_id2 ...\"]"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Default: do_nothing_K scenario, all bins"
    echo "  $0 capability_test_K                  # All bins with capability_test_K scenario"
    echo "  $0 do_nothing_K \"1 2 5 10\"            # Bin IDs 1,2,5,10 with do_nothing_K scenario"
    exit 1
fi

# Check if CSV file exists
if [ ! -f "$CSV_FILE" ]; then
    echo "Error: CSV file '$CSV_FILE' not found!"
    exit 1
fi

echo "  Scenario folder: $SCENARIO_FOLDER"
echo "  Scenario name: $SCENARIO_NAME"
echo "  CSV file: $CSV_FILE"

# Determine which bin IDs to run
if [ -z "$BIN_IDS" ]; then
    # No specific bin IDs provided, run all bins
    # Count data rows (excluding header)
    NUM_ROWS=$(tail -n +2 "$CSV_FILE" | wc -l)
    # Start from bin_id=1 (row index 1, which is the first data row after header)
    BIN_IDS_ARRAY=($(seq 1 $NUM_ROWS))
    echo "  Bin IDs: ALL (${BIN_IDS_ARRAY[@]})"
    echo "  Total bins: $NUM_ROWS"
else
    # Specific bin IDs provided
    BIN_IDS_ARRAY=($BIN_IDS)
    echo "  Bin IDs: ${BIN_IDS_ARRAY[@]}"
    echo "  Total bins: ${#BIN_IDS_ARRAY[@]}"
fi

# Create logs directory if it doesn't exist
mkdir -p logs

echo ""
echo "Submitting jobs to SLURM cluster (using new_mb_model)..."
echo "=========================================="

# Loop over specified bin IDs
for bin_id in "${BIN_IDS_ARRAY[@]}"; do
    # Submit a new job for each bin ID
    sbatch <<EOF
#!/bin/bash
#SBATCH --job-name=new_csv_${bin_id}
#SBATCH --output=logs/new_csv_bin_${bin_id}_%j.out
#SBATCH --error=logs/new_csv_bin_${bin_id}_%j.err
#SBATCH --time=300:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=1gb
#SBATCH --partition=sirius

# Load modules and activate environment

module load IMAS
source /home/ITER/llealsa/miniconda3/etc/profile.d/conda.sh
conda activate PFC-TT
export PATH="/home/ITER/llealsa/miniconda3/envs/PFC-TT/bin:$PATH"

unset PYTHONPATH
export PYTHONNOUSERSITE=1

module unload SciPy-bundle        2>/dev/null
module unload Python-bundle-PyPI  2>/dev/null
module unload Python              2>/dev/null
module unload numpy               2>/dev/null
module unload mpi4py              2>/dev/null
module unload scifem              2>/dev/null



# Run the Python script with new_mb_model

# Run CSV bin script with user-site disabled
PYTHONNOUSERSITE=1 python -s run_on_cluster/run_new_csv_bin.py $bin_id $SCENARIO_FOLDER $SCENARIO_NAME $CSV_FILE


EOF
    echo "Submitted job for bin ID: $bin_id"
done

echo ""
echo "=========================================="
echo "All new CSV bin jobs submitted!"
# Print the active conda environment if available, otherwise provide Python executable and prefix
if [ -n "$CONDA_DEFAULT_ENV" ]; then
    echo "  Conda environment: $CONDA_DEFAULT_ENV"
else
    echo "  Conda environment: (not set)"
    echo -n "  Python executable: "
    which python 2>/dev/null || echo "not found"
    PY_PREFIX=$(python -c 'import sys; print(sys.prefix)' 2>/dev/null || echo 'n/a')
    echo "  Python sys.prefix: $PY_PREFIX"
fi
echo "  Scenario: $SCENARIO_NAME"
echo "  Jobs submitted: ${#BIN_IDS_ARRAY[@]}"
echo "  Using: new_mb_model (dynamic FESTIM model builder)"
echo ""
echo "Monitor jobs with: squeue -u \$USER"
echo "Check logs in: logs/new_csv_bin_*"
echo "Cancel all jobs: scancel -u \$USER"

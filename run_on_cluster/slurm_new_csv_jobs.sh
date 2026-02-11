#!/bin/bash
#SBATCH --job-name=new_csv_bin_job
#SBATCH --output=logs/new_csv_bin_%j.out  # Log file for each job
#SBATCH --error=logs/new_csv_bin_%j.err   # Error log
#SBATCH --time=1:00:00           # Adjust time limit
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1         # Adjust CPU usage
#SBATCH --mem=1gb                 # Adjust memory
#SBATCH --partition=sirius        # Adjust partition name

# New CSV Bin SLURM Job Submitter (using new_mb_model)
# Usage: 
#   ./slurm_new_csv_jobs.sh scenario_name                                      # Run all bins with custom scenario (default input folder)
#   ./slurm_new_csv_jobs.sh scenario_name "n-m, p-q, r-s..."                   # Run specific bin ranges with custom scenario
#   ./slurm_new_csv_jobs.sh --input-dir /path/to/folder scenario_name          # Run all bins with input folder
#   ./slurm_new_csv_jobs.sh --input-dir /path/to/folder scenario_name "1-5"    # Run specific bins with input folder
#
# Examples:
#   ./slurm_new_csv_jobs.sh just_glow                          # Run all bins with just_glow scenario (uses input_files/)
#   ./slurm_new_csv_jobs.sh just_glow "1-5"                    # Run bins 1 to 5 with just_glow scenario
#   ./slurm_new_csv_jobs.sh just_glow "1-5, 10-15, 20-22"      # Run bins 1-5, 10-15, 20-22 with just_glow scenario
#   ./slurm_new_csv_jobs.sh --input-dir my_configs/scenario_v2 my_scenario    # Run all bins using files from my_configs/scenario_v2/
#   ./slurm_new_csv_jobs.sh --input-dir my_configs/scenario_v2 my_scenario "1-10"  # Run bins 1-10 with input folder

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
DEFAULT_INPUT_DIR="input_files"

# Parse command line arguments
if [ $# -eq 0 ]; then
    echo "Usage: $0 scenario_name [\"n-m, p-q, r-s...\"]"
    echo "   or: $0 --input-dir <folder> scenario_name [\"n-m, p-q, r-s...\"]"
    echo ""
    echo "Examples:"
    echo "  $0 just_glow                                      # Run all bins with just_glow scenario (default input_files/ folder)"
    echo "  $0 just_glow \"1-5\"                               # Run bins 1 to 5 with just_glow scenario"
    echo "  $0 just_glow \"1-5, 10-15, 20-22\"                # Run bins 1-5, 10-15, 20-22 with just_glow scenario"
    echo "  $0 just_glow \"1 5 9\"                             # Run individual bins 1, 5, 9"
    echo "  $0 --input-dir my_configs/v2 my_scenario          # Run all bins using input folder: my_configs/v2/"
    echo "  $0 --input-dir my_configs/v2 my_scenario \"1-10\"  # Run bins 1-10 using input folder: my_configs/v2/"
    exit 1
fi

# Check for --input-dir flag
INPUT_DIR="$DEFAULT_INPUT_DIR"
SCENARIO_START_INDEX=1

if [ "$1" = "--input-dir" ] || [ "$1" = "-i" ]; then
    if [ $# -lt 3 ]; then
        echo "Error: --input-dir requires a folder path and scenario name"
        echo "Usage: $0 --input-dir <folder> scenario_name [bin_specification]"
        exit 1
    fi
    INPUT_DIR="$2"
    SCENARIO_START_INDEX=3
fi

# Validate input directory
if [ ! -d "$INPUT_DIR" ]; then
    echo "Error: Input directory '$INPUT_DIR' not found!"
    exit 1
fi

# Find the input files (CSV, materials, mesh, scenario) in the input directory
CSV_FILE=$(find "$INPUT_DIR" -maxdepth 1 -name "input_table.csv" -o -name "*bin*.csv" 2>/dev/null | head -1)
if [ -z "$CSV_FILE" ] || [ ! -f "$CSV_FILE" ]; then
    echo "Error: No input_table.csv or bin CSV file found in '$INPUT_DIR'!"
    echo "  Please ensure your input folder contains input_table.csv"
    exit 1
fi

MATERIALS_FILE=$(find "$INPUT_DIR" -maxdepth 1 -name "materials.csv" 2>/dev/null | head -1)
MESH_FILE=$(find "$INPUT_DIR" -maxdepth 1 -name "mesh.py" 2>/dev/null | head -1)

# First argument (after --input-dir if present) is scenario name (required)
SCENARIO_FOLDER="$INPUT_DIR"
SCENARIO_NAME="${!SCENARIO_START_INDEX}"
BIN_SPEC="${@:$((SCENARIO_START_INDEX + 1))}"  # Everything after scenario name

if [ -z "$SCENARIO_NAME" ]; then
    echo "Error: Scenario name is required!"
    exit 1
fi

# Check if CSV file exists
if [ ! -f "$CSV_FILE" ]; then
    echo "Error: CSV file '$CSV_FILE' not found!"
    exit 1
fi

echo "Using input directory:"
echo "  Input folder: $INPUT_DIR"
echo "  CSV file: $CSV_FILE"
if [ -n "$MATERIALS_FILE" ] && [ -f "$MATERIALS_FILE" ]; then
    echo "  Materials file: $MATERIALS_FILE"
fi
if [ -n "$MESH_FILE" ] && [ -f "$MESH_FILE" ]; then
    echo "  Mesh file: $MESH_FILE"
fi
echo "  Scenario name: $SCENARIO_NAME"

# Function to expand bin specifications into individual bin IDs
expand_bin_spec() {
    local spec="$1"
    local bins=()
    
    # Handle comma-separated ranges and individual numbers
    # Replace commas with spaces and process each token
    spec=$(echo "$spec" | tr ',' ' ')
    
    for token in $spec; do
        # Remove whitespace
        token=$(echo "$token" | xargs)
        
        if [[ $token =~ ^([0-9]+)-([0-9]+)$ ]]; then
            # Range format: "n-m"
            start=${BASH_REMATCH[1]}
            end=${BASH_REMATCH[2]}
            for ((i=start; i<=end; i++)); do
                bins+=($i)
            done
        elif [[ $token =~ ^[0-9]+$ ]]; then
            # Individual number
            bins+=($token)
        else
            echo "Error: Invalid bin specification '$token'. Use format like '1-5', '10', or '1-5, 10, 15-20'"
            exit 1
        fi
    done
    
    # Remove duplicates and sort
    printf '%s\n' "${bins[@]}" | sort -n | uniq
}

# Determine which bin IDs to run
if [ -z "$BIN_SPEC" ]; then
    # No specific bin IDs provided, run all bins
    # Count data rows (excluding header)
    NUM_ROWS=$(tail -n +2 "$CSV_FILE" | wc -l)
    # Start from bin_id=1 (row index 1, which is the first data row after header)
    BIN_IDS_ARRAY=($(seq 1 $NUM_ROWS))
    echo "  Bin IDs: ALL (1 to $NUM_ROWS)"
    echo "  Total bins: $NUM_ROWS"
else
    # Parse bin specifications and expand ranges
    BIN_IDS_OUTPUT=$(expand_bin_spec "$BIN_SPEC")
    BIN_IDS_ARRAY=($BIN_IDS_OUTPUT)
    echo "  Bin specification: $BIN_SPEC"
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
PYTHONNOUSERSITE=1 python -s run_on_cluster/run_new_csv_bin.py $bin_id $SCENARIO_FOLDER $SCENARIO_NAME $CSV_FILE --input-dir $INPUT_DIR


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

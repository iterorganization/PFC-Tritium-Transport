#!/bin/bash
#SBATCH --job-name=new_csv_bin_job
#SBATCH --output=logs/new_csv_bin_%j.out
#SBATCH --error=logs/new_csv_bin_%j.err
#SBATCH --time=300:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=1gb
#SBATCH --partition=sirius

# New CSV Bin SLURM Job Submitter
# Usage: ./slurm_new_csv_bin input_files
# 
# Where input_files folder contains:
#   - input_table.csv (bin definitions)
#   - materials.csv (material properties)
#   - mesh.py (mesh definition)
#   - scenario_*.py (scenario file - any name ending in .py except mesh.py)

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

# Parse command line arguments
if [ $# -eq 0 ]; then
    echo "Usage: $0 input_files [bin_specification]"
    echo ""
    echo "Where input_files is a folder containing:"
    echo "  - input_table.csv"
    echo "  - materials.csv"
    echo "  - mesh.py"
    echo "  - scenario_*.py (or any .py file except mesh.py)"
    echo ""
    echo "Examples:"
    echo "  $0 input_files                  # Run all bins"
    echo "  $0 input_files \"1-5\"            # Run bins 1 to 5"
    echo "  $0 input_files \"1-5, 10-15\"     # Run bins 1-5 and 10-15"
    exit 1
fi

INPUT_DIR="$1"
BIN_SPEC="${@:2}"  # Everything after input_dir

# Validate input directory exists
if [ ! -d "$INPUT_DIR" ]; then
    echo "Error: Input directory '$INPUT_DIR' not found!"
    exit 1
fi

# Check for required files
if [ ! -f "$INPUT_DIR/input_table.csv" ]; then
    echo "Error: $INPUT_DIR/input_table.csv not found!"
    exit 1
fi

if [ ! -f "$INPUT_DIR/materials.csv" ]; then
    echo "Error: $INPUT_DIR/materials.csv not found!"
    exit 1
fi

if [ ! -f "$INPUT_DIR/mesh.py" ]; then
    echo "Error: $INPUT_DIR/mesh.py not found!"
    exit 1
fi

# Find the scenario file (any .py file except mesh.py)
SCENARIO_FILE=$(find "$INPUT_DIR" -maxdepth 1 -type f -name "*.py" ! -name "mesh.py" | head -1)
if [ -z "$SCENARIO_FILE" ] || [ ! -f "$SCENARIO_FILE" ]; then
    echo "Error: No scenario .py file found in '$INPUT_DIR' (excluding mesh.py)!"
    exit 1
fi

# Extract scenario name from filename (without .py extension)
SCENARIO_NAME=$(basename "$SCENARIO_FILE" .py)

CSV_FILE="$INPUT_DIR/input_table.csv"
SCENARIO_FOLDER="$INPUT_DIR"

echo "Input Configuration:"
echo "  Input folder: $INPUT_DIR"
echo "  CSV file: $CSV_FILE"
echo "  Materials file: $INPUT_DIR/materials.csv"
echo "  Mesh file: $INPUT_DIR/mesh.py"
echo "  Scenario file: $SCENARIO_FILE"
echo "  Scenario name: $SCENARIO_NAME"

# Function to expand bin specifications into individual bin IDs
expand_bin_spec() {
    local spec="$1"
    local bins=()
    
    # Handle comma-separated ranges and individual numbers
    spec=$(echo "$spec" | tr ',' ' ')
    
    for token in $spec; do
        token=$(echo "$token" | xargs)
        
        if [[ $token =~ ^([0-9]+)-([0-9]+)$ ]]; then
            start=${BASH_REMATCH[1]}
            end=${BASH_REMATCH[2]}
            for ((i=start; i<=end; i++)); do
                bins+=($i)
            done
        elif [[ $token =~ ^[0-9]+$ ]]; then
            bins+=($token)
        else
            echo "Error: Invalid bin specification '$token'. Use format like '1-5', '10', or '1-5, 10, 15-20'"
            exit 1
        fi
    done
    
    printf '%s\n' "${bins[@]}" | sort -n | uniq
}

# Determine which bin IDs to run
if [ -z "$BIN_SPEC" ]; then
    NUM_ROWS=$(tail -n +2 "$CSV_FILE" | wc -l)
    BIN_IDS_ARRAY=($(seq 1 $NUM_ROWS))
    echo "  Bin specification: ALL"
    echo "  Total bins: $NUM_ROWS"
else
    BIN_IDS_OUTPUT=$(expand_bin_spec "$BIN_SPEC")
    BIN_IDS_ARRAY=($BIN_IDS_OUTPUT)
    echo "  Bin specification: $BIN_SPEC"
    echo "  Total bins: ${#BIN_IDS_ARRAY[@]}"
fi

# Create logs directory
mkdir -p logs

echo ""
echo "Submitting jobs to SLURM cluster..."
echo "=========================================="

# Loop over specified bin IDs
for bin_id in "${BIN_IDS_ARRAY[@]}"; do
    sbatch <<EOF
#!/bin/bash
#SBATCH --job-name=csv_${bin_id}
#SBATCH --output=logs/new_csv_bin_${bin_id}_%j.out
#SBATCH --error=logs/new_csv_bin_${bin_id}_%j.err
#SBATCH --time=300:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=1gb
#SBATCH --partition=sirius

module load IMAS
source /home/ITER/llealsa/miniconda3/etc/profile.d/conda.sh
conda activate PFC-TT
export PATH="/home/ITER/llealsa/miniconda3/envs/PFC-TT/bin:\$PATH"

unset PYTHONPATH
export PYTHONNOUSERSITE=1

module unload SciPy-bundle        2>/dev/null
module unload Python-bundle-PyPI  2>/dev/null
module unload Python              2>/dev/null
module unload numpy               2>/dev/null
module unload mpi4py              2>/dev/null
module unload scifem              2>/dev/null

PYTHONNOUSERSITE=1 python -s run_on_cluster/run_new_csv_bin.py $bin_id $SCENARIO_FOLDER $SCENARIO_NAME $CSV_FILE --input-dir $INPUT_DIR

EOF
    echo "Submitted job for bin ID: $bin_id"
done

echo ""
echo "=========================================="
echo "All jobs submitted!"
echo "  Input folder: $INPUT_DIR"
echo "  Scenario: $SCENARIO_NAME"
echo "  Jobs submitted: ${#BIN_IDS_ARRAY[@]}"
echo ""
echo "Monitor: squeue -u \$USER"
echo "Cancel: scancel -u \$USER"

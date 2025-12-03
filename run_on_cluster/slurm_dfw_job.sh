#!/bin/bash
#SBATCH --job-name=bin_job
#SBATCH --output=logs/bin_%j.out  # Log file for each job
#SBATCH --error=logs/bin_%j.err   # Error log
#SBATCH --time=1:00:00           # Adjust time limit
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1         # Adjust CPU usage
#SBATCH --mem=1gb                 # Adjust memory
#SBATCH --partition=sirius       # Adjust partition name

# Load modules (if required)


# Activate virtual environment
module load IMAS
source /home/ITER/llealsa/miniconda3/etc/profile.d/conda.sh
conda activate festim-fenicsx
export PATH="/home/ITER/llealsa/miniconda3/envs/festim-fenicsx/bin:$PATH"

unset PYTHONPATH
export PYTHONNOUSERSITE=1

module unload SciPy-bundle        2>/dev/null
module unload Python-bundle-PyPI  2>/dev/null
module unload Python              2>/dev/null
module unload numpy               2>/dev/null
module unload mpi4py              2>/dev/null
module unload scifem              2>/dev/null

# Loop over bins and modes
for i in 9 13 14; do  # First wall bins
    modes=('shadowed')

    for mode in "${modes[@]}"; do
        # Submit a new job for each combination of i and mode
        sbatch <<EOF
#!/bin/bash
#SBATCH --job-name=bin_${i}_dfw
#SBATCH --output=logs/bin_${i}_dfw_%j.out
#SBATCH --error=logs/bin_${i}_dfw_%j.err
#SBATCH --time=50:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=1gb
#SBATCH --partition=sirius

# Load modules and activate environment

module load IMAS
source /home/ITER/llealsa/miniconda3/etc/profile.d/conda.sh
conda activate festim-fenicsx
export PATH="/home/ITER/llealsa/miniconda3/envs/festim-fenicsx/bin:$PATH"

unset PYTHONPATH
export PYTHONNOUSERSITE=1

module unload SciPy-bundle        2>/dev/null
module unload Python-bundle-PyPI  2>/dev/null
module unload Python              2>/dev/null
module unload numpy               2>/dev/null
module unload mpi4py              2>/dev/null
module unload scifem              2>/dev/null


# Run the Python script
python run_on_cluster/run_dfw_bin.py $i $mode iter_scenarios capability_test
EOF
    done
done
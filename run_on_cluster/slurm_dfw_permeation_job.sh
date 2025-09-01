#!/bin/bash
#SBATCH --job-name=bin_job
#SBATCH --output=logs/bin_%j.out  # Log file for each job
#SBATCH --error=logs/bin_%j.err   # Error log
#SBATCH --time=1:00:00           # Adjust time limit
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1         # Adjust CPU usage
#SBATCH --mem=1gb                 # Adjust memory
#SBATCH --partition=sirius       # Adjust partition name

# Loop over bins and modes
for i in 13 14; do  # First wall bins
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
module load Python
source myenv/bin/activate

# Run the Python script
python run_on_cluster/run_dfw_bin.py $i $mode iter_scenarios benchmark 
EOF
    done
done
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
module load IMAS
# module load FESTIM

# Activate virtual environment
source myenv/bin/activate

# Load other modules
ml foss
ml SciPy-bundle 
ml mpi4py
ml tqdm
ml scifem
ml dolfinx/0.9.0-foss-2023b

# Install correct FESTIM version
python -m pip install --ignore-installed git+https://github.com/festim-dev/FESTIM@d1b71deed2d0998159b99591951493bffa1f5ca8

# Install correct HISP version 
python -m pip install git+https://github.com/festim-dev/hisp@fix-b-bins

# Loop over bins and modes
for i in $(seq 10 16); do  # (0 17) First wall bins
    case $i in 
        13|14|16|17)
            modes=('shadowed' 'shadowed' 'wetted')
            ;;
        *)
            modes=('shadowed' 'shadowed' 'low_wetted' 'high_wetted')
            ;;
    esac

    for mode in "${modes[@]}"; do
        # Submit a new job for each combination of i and mode
        sbatch <<EOF
#!/bin/bash
#SBATCH --job-name=bin_${i}_${mode}
#SBATCH --output=logs/bin_${i}_${mode}_%j.out
#SBATCH --error=logs/bin_${i}_${mode}_%j.err
#SBATCH --time=300:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=1gb
#SBATCH --partition=sirius

# Load modules and activate environment
module load IMAS
source myenv/bin/activate
ml foss
ml SciPy-bundle 
ml mpi4py
ml tqdm
ml scifem
ml dolfinx/0.9.0-foss-2023b

# Run the Python script
python run_on_cluster/run_wall_bin.py $i $mode iter_scenarios capability_test
EOF
    done
done
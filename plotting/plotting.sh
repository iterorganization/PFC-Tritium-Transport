#!/bin/bash
#SBATCH --job-name=totalinvprocess
#SBATCH --output=totalinvprocess.out # Log file for each job
#SBATCH --error=totalinvprocess.err   # Error log
#SBATCH --time=300:00:00           # Adjust time limit
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1         # Adjust CPU usage
#SBATCH --mem=1gb                 # Adjust memory
#SBATCH --partition=gen10         # Adjust partition name

# Load modules (if required)
module load IMAS
# module load FESTIM

# Activate virtual environment
source myenv/bin/activate
# print(plotly. --version)

# Load other modules
ml foss
ml SciPy-bundle 
ml mpi4py
ml tqdm
ml scifem
ml dolfinx/0.9.0-foss-2023b

python plotting/post_process_data.py
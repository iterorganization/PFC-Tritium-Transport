#!/bin/bash
#SBATCH --job-name=plotting
#SBATCH --output=plot.out  # Log file for each job
#SBATCH --error=plot.err   # Error log
#SBATCH --time=100:00:00           # Adjust time limit
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1         # Adjust CPU usage
#SBATCH --mem=1gb                 # Adjust memory
#SBATCH --partition=gen10         # Adjust partition name

# Load modules (if required)
module load IMAS

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
python -m pip install git+https://github.com/kaelyndunnell/hisp@fix-b-bins

# Plot Results
python cycle_parallel_plot.py
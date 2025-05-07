#!/bin/bash
#SBATCH --job-name=bin_job
#SBATCH --output=logs/bin_%j.out  # Log file for each job
#SBATCH --error=logs/bin_%j.err   # Error log
#SBATCH --time=1:00:00           # Adjust time limit
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1         # Adjust CPU usage
#SBATCH --mem=1gb                 # Adjust memory
#SBATCH --partition=gen10         # Adjust partition name

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
python -m pip install git+https://github.com/kaelyndunnell/hisp@fix-b-bins

# Run festim for given bin
# python run_on_cluster/run_div_bin.py 18 iter_scenarios testcase

# Loop over bins and submit separate jobs
for i in $(seq 18 62); do  # Div wall bins
    # Create a temporary job script for each i
    cat <<EOF > job_${i}.sh
#!/bin/bash
#SBATCH --job-name=bin_${i}
#SBATCH --output=logs/bin_${i}_%j.out
#SBATCH --error=logs/bin_${i}_%j.err
#SBATCH --time=300:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=1gb
#SBATCH --partition=gen10

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
python run_on_cluster/run_div_bin.py $i iter_scenarios just_glow
EOF

    # Submit the job script
    sbatch job_${i}.sh

    # Optionally, remove the temporary job script after submission
    rm job_${i}.sh
done
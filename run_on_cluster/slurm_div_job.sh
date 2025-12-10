#!/bin/bash --login
#SBATCH --job-name=bin_job
#SBATCH --output=logs/bin_%j.out
#SBATCH --error=logs/bin_%j.err
#SBATCH --time=1:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=1gb
#SBATCH --partition=sirius

module load IMAS
source /home/ITER/llealsa/miniconda3/etc/profile.d/conda.sh
conda activate festim-fenicsx

unset PYTHONPATH
export PYTHONNOUSERSITE=1
module unload SciPy-bundle        2>/dev/null
module unload Python-bundle-PyPI  2>/dev/null
module unload Python              2>/dev/null
module unload numpy               2>/dev/null
module unload mpi4py              2>/dev/null
module unload scifem              2>/dev/null

# Loop over bins and submit separate jobs
for i in $(seq 18 61); do
#for i in 47; do
    cat <<EOF > job_${i}.sh
#!/bin/bash --login
#SBATCH --job-name=bin_${i}
#SBATCH --output=logs/bin_${i}_%j.out
#SBATCH --error=logs/bin_${i}_%j.err
#SBATCH --time=300:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=1gb
#SBATCH --partition=sirius

module load IMAS
source /home/ITER/llealsa/miniconda3/etc/profile.d/conda.sh
conda activate festim-fenicsx
unset PYTHONPATH
export PYTHONNOUSERSITE=1
module unload SciPy-bundle        2>/dev/null
module unload Python-bundle-PyPI  2>/dev/null
module unload Python              2>/dev/null
module unload numpy               2>/dev/null
module unload mpi4py              2>/dev/null
module unload scifem              2>/dev/null

# Run the actual job
python run_on_cluster/run_div_bin.py ${i} iter_scenarios just_glow_K
EOF

    sbatch --export=NONE job_${i}.sh
    rm job_${i}.sh
done

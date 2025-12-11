#!/bin/bash --login
#SBATCH --job-name=create_env
#SBATCH --output=logs/create_env_%j.out
#SBATCH --error=logs/create_env_%j.err
#SBATCH --time=01:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=2gb
#SBATCH --partition=sirius

module load IMAS
source /home/ITER/llealsa/miniconda3/etc/profile.d/conda.sh

echo "Creating Conda environment from YAML..."
conda env create -f /home/ITER/llealsa/festim-fenicsx.yml

echo "Verifying FESTIM version..."

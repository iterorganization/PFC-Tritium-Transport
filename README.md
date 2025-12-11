# PFC-Tritium-Transport

This repository contains `hisp` scripts and plasma data tailored for ITER.

---

## ⚠️ Important Note
This setup has been **modified to run with FESTIM v2.0-beta** and **dolfinx v0.10.0** for compatibility with the latest features.

---

## How to Install

### 1. Clone this repository
```bash
git clone --branch alleal https://github.com/AdriaLlealS/PFC-Tritium-Transport.git
```

### 2. Recreate the Python environment
We use **conda** for reproducibility. Download the `festim-fenicsx.yml` file from this repository and run:
```bash
conda env create -f festim-fenicsx.yml
conda activate festim-fenicsx
```

This will install:
- **FESTIM v2.0-beta** (from GitHub)
- **dolfinx v0.10.0**
- All required dependencies

---

### 3. Install custom HISP version
We use a specific branch of HISP which will remain static until significant improvements are made. 
To avoid FESTIM version conflicts, we install HISP **without dependencies**:
```bash
pip install --no-deps git+https://github.com/AdriaLlealS/hisp.git@fix-b-bins
```

---

## How to Run
Prepare your batch job `job.sh` in the `run_on_cluster` folder. Then:
```bash
sh run_on_cluster/job.sh
```
Make sure to load the IMAS module and activate the conda environment on your .sh file with:
```bash
module load IMAS
source <your-conda-installation-path>
conda activate festim-fenicsx
```
Replace <your-conda-installation-path> with the path to your own conda installation. For example:
```bash
source /opt/miniconda3/etc/profile.d/conda.sh'
```
--


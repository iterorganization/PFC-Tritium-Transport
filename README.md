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
We use a specific branch of HISP from your fork:
```bash
pip install git+https://github.com/AdriaLlealS/hisp.git@fix-b-bins
```
This ensures the exact commit from your branch is installed.

---

## How to Run
Prepare your batch job `job.sh` in the `run_on_cluster` folder. Then:
```bash
sh run_on_cluster/job.sh
```

--


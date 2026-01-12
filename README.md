# PFC-Tritium-Transport

The purpose of this repository is to obtain Hydrogen inventory estimations in the Plasma Facing Components in custom reactor and plasma scenarios. For now, it relies on HISP in order to run FESTIM simulations from which the inventory will be calculated. In the future this repository will be further developed to be able to work with different Hydrogen transport codes at user's preference. 

---

## How to Install

### 1. Clone this repository
```bash
git clone --branch alleal https://github.com/AdriaLlealS/PFC-Tritium-Transport.git
```

### 2. Recreate the Python environment
We use **conda** for reproducibility. Make sure the file `PFC-T-T.yml` was correctly downloaded from this repository and run:
```bash
conda env create -f PFC-T-T.yml
conda activate PFC-T-T
```

This will install:
- **FESTIM v2.0-beta.1**
- **dolfinx v0.10.0**
- All required dependencies

---

### 3. Install custom HISP version
We use a specific branch of HISP which will remain static until significant improvements are made. 
To avoid FESTIM version conflicts, we install HISP **without dependencies**:
```bash
pip install --no-deps git+https://github.com/AdriaLlealS/hisp.git@PFCTT-input-table
```

---

## How to Run

Brief summary:

- Prepare the **input table** (`input_table.csv`) describing all bins you want to simulate. Required columns (exact headers):
	- `Bin number`, `Z_start (m)`, `R_start (m)`, `Z_end (m)`, `R_end (m)`,
	- `Material`, `Thickness (m)`, `Cu thickness (m)`, `mode`,
	- `S. Area parent bin (m^2)`, `Surface area (m^2)`, `f (ion flux fraction)`, `location`.
	Optional simulation columns accepted (case-sensitive): `BC Plasma Facing Surface`, `BC rear surface`, `Coolant Temp. (K)`, `rtol`, `atol`, `FP max. stepsize (s)`, `Max. stepsize no FP (s)`.

- Provide the **binned flux data** required by the pulses/scenarios you will run. Place these in the `data/` folder (or adjust paths in the runner). Typical file names used by the code:
	- `Binned_Flux_Data.dat` (FP)
	- `Binned_Flux_Data_just_D_pulse.dat` (FP_D)
	- `ICWC_data.dat` (ICWC)
	- `GDC_data.dat` (GDC)
	Also supply any ROSP/RISP wall data referenced by your scenarios.

- Create or select **scenario files** in `scenarios/` (e.g. `10FPdays.py`, `10FPdays_baking.py`). Each scenario module should expose a `scenario` object built from `Scenario`/`Pulse` definitions.

Before running, activate the `PFC-T-T` conda environment (and make sure the correct version of HISP has been installed).

Run capabilities

- This repository includes example submitters for running many bins. In particular there is a SLURM submitter `run_on_cluster/slurm_csv_jobs.sh` which demonstrates how to submit single-bin or multi-bin jobs to a cluster. Example usages:

```bash
# submit a single bin (example: bin id 3) with scenario '10FPdays'
./run_on_cluster/slurm_csv_jobs.sh 10FPdays "3"

# submit all bins for a scenario (default behavior)
./run_on_cluster/slurm_csv_jobs.sh 10FPdays

# submit a list/range of bin ids
./run_on_cluster/slurm_csv_jobs.sh 10FPdays "1 2 5 10"
```

- Important: the provided `slurm_csv_jobs.sh` scripts are tailored to ITER's SCDCC (Scientific Division Computer Cluster) and include site-specific module loads, partitions and paths. If you are running on a different system, create a cluster submit script appropriate for your scheduler/environment (copy the example and adapt environment activation, modules, partitions and any filesystem paths).

- `run_csv_bin.py` is the per-bin runner used by the submitters: it loads the CSV reactor, builds a `Model` for each bin and writes results to `results_<scenario>/`.

- Column header names are matched exactly and are case-sensitive. If your table uses different headers, either rename columns or adapt `csv_bin_loader.py`.

- Ensure your binned flux data matches the pulse types used by your scenarios and that file paths are correct.



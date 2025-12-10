# CSV Bin Runner Usage Guide

This guide explains how to use the new CSV bin runner scripts that work with the CSV-based bin system.

## Files

- `run_csv_bin.py`: Run a single CSV bin by its ID (row index in input table)
- `run_csv_bins_batch.sh`: Batch runner for multiple CSV bins (local execution)
- `slurm_csv_jobs.sh`: SLURM cluster job submission script for all CSV bins

## Key Concepts

- **bin_ID**: The row index (0-based) in the input_table.csv file - this uniquely identifies each bin
- **bin_number**: The actual bin number which can have duplicates (multiple rows can have the same bin_number)
- Each row in the CSV represents one simulation run with specific parameters

## Usage Examples

### Single Bin Execution

```bash
# Run bin ID 0 (first row after header) with testcase scenario
python run_csv_bin.py 0 iter_scenarios testcase input_table.csv

# Run bin ID 5 with custom CSV file
python run_csv_bin.py 5 iter_scenarios my_scenario custom_bins.csv
```

### Batch Execution

```bash
# Run all bins in input_table.csv
./run_csv_bins_batch.sh iter_scenarios testcase

# Run all bins with custom CSV file
./run_csv_bins_batch.sh iter_scenarios testcase my_bins.csv

# Run specific bin IDs (0, 2, 4)
./run_csv_bins_batch.sh iter_scenarios testcase input_table.csv 0 2 4

# Run range of bin IDs
./run_csv_bins_batch.sh iter_scenarios testcase input_table.csv {0..9}
```

### SLURM Cluster Execution

The `slurm_csv_jobs.sh` script offers flexible execution options:

#### Option 1: Default Configuration
```bash
# Submit all bins using default scenario (just_glow_K)
./slurm_csv_jobs.sh
```

#### Option 2: Custom Scenario (All Bins)
```bash
# Submit all bins with a custom scenario
./slurm_csv_jobs.sh capability_test_K
./slurm_csv_jobs.sh benchmark
./slurm_csv_jobs.sh my_custom_scenario
```

#### Option 3: Custom Scenario + Specific Bin IDs
```bash
# Submit only specific bin IDs with custom scenario
./slurm_csv_jobs.sh just_glow_K "0 1 5 10"
./slurm_csv_jobs.sh capability_test_K "0 2 4 6 8"
./slurm_csv_jobs.sh benchmark "15 20 25"
```

#### Job Management
```bash
# Monitor submitted jobs
squeue -u $USER

# Check job status and logs
ls logs/csv_bin_*

# Cancel all jobs if needed
scancel -u $USER
```

## Output Files

Results are saved as JSON files with naming convention:
```
results_{scenario_name}/csv_bin_id_{bin_id}_num_{bin_number}_{material}_{mode}.json
```

For example:
```
results_testcase/csv_bin_id_0_num_1_W_wetted.json
results_testcase/csv_bin_id_1_num_1_W_shadowed.json
```

## Output Data Structure

Each JSON file contains:
- **Simulation quantities**: concentration, flux, etc. with time series data
- **Temperature**: Surface temperature (x=0) values
- **Bin metadata**: bin_ID, bin_number, material, location, thickness, etc.
- **Configuration**: tolerance settings, boundary conditions, stepsize limits
- **Time**: simulation time points

## Advantages of bin_ID System

1. **Unique identification**: Each row has a unique ID regardless of bin_number duplicates
2. **Direct CSV mapping**: bin_ID corresponds exactly to row position in CSV
3. **Parallel processing**: Different bin_IDs can be run simultaneously
4. **Configuration control**: Each bin_ID has its own tolerance and parameter settings

## Cluster Configuration

The `slurm_csv_jobs.sh` script is configured for the ITER cluster environment with:

- **Partition**: sirius
- **Resources**: 1 CPU, 1GB memory per job
- **Runtime**: 300 hours maximum
- **Environment**: FESTIM-FenicsX conda environment with IMAS modules
- **Python isolation**: User-site packages disabled for reproducibility

### SLURM Script Usage Modes

The script supports three usage modes:

1. **Default mode**: `./slurm_csv_jobs.sh`
   - Uses default scenario: `just_glow_K`
   - Runs all bins from `input_table.csv`

2. **Custom scenario mode**: `./slurm_csv_jobs.sh <scenario_name>`
   - Uses specified scenario from `iter_scenarios/` folder
   - Runs all bins from `input_table.csv`

3. **Custom scenario + specific bins**: `./slurm_csv_jobs.sh <scenario_name> "<bin_ids>"`
   - Uses specified scenario
   - Runs only the specified bin IDs (space-separated)

### Customizing Default Configuration

To change the default settings, edit these variables in `slurm_csv_jobs.sh`:

```bash
# Default configuration
DEFAULT_SCENARIO_FOLDER="iter_scenarios"
DEFAULT_SCENARIO_NAME="just_glow_K"        # Change default scenario here
DEFAULT_CSV_FILE="input_table.csv"         # Change default CSV file here
```

## Scenario Setup

Make sure your scenario file is properly configured in the scenario folder:
```python
# Example scenario file: iter_scenarios/testcase.py
from hisp.scenario import Scenario

scenario = Scenario(
    name="testcase",
    pulse_schedule=[
        ("FP", 0, 400),     # Full Power pulse
        ("FP_D", 400, 800), # Deuterium-only pulse
    ]
)
```

## Troubleshooting

- **CSV file not found**: Ensure the CSV file path is correct
- **bin_ID not found**: Check that the bin_ID exists in the CSV (0-based indexing)
- **Import errors**: Make sure the CSV bin classes are in the Python path
- **Scenario errors**: Verify the scenario file exists and is properly formatted
- **SLURM issues**: Check cluster status with `sinfo` and job logs in `logs/csv_bin_*`
- **Module conflicts**: The script automatically unloads conflicting Python modules
- **Memory errors**: Increase memory allocation in SLURM script if needed (`--mem=2gb`)
- **Invalid bin IDs**: Ensure bin IDs are space-separated and within valid range (0 to N-1)
- **Script permissions**: Make sure the script is executable: `chmod +x slurm_csv_jobs.sh`

### Common Usage Patterns

```bash
# Quick test with a few bins
./slurm_csv_jobs.sh testcase "0 1 2"

# Production run with all bins
./slurm_csv_jobs.sh production_scenario

# Debug specific problematic bins
./slurm_csv_jobs.sh debug_scenario "15 23 31"

# Run different material types (assuming you know which bin IDs correspond to which materials)
./slurm_csv_jobs.sh material_study "0 5 10 15 20"  # W bins
./slurm_csv_jobs.sh material_study "1 6 11 16 21"  # B bins
```

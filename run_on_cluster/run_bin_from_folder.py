#!/usr/bin/env python
"""
Run a single bin simulation locally from an input folder.

Usage:
    python run_on_cluster/run_bin_from_folder.py <input_folder> <bin_id>

Examples:
    python run_on_cluster/run_bin_from_folder.py DT1_5 1       # Run bin_id 1 (first row)
    python run_on_cluster/run_bin_from_folder.py DT1_5 33      # Run bin_id 33
    python run_on_cluster/run_bin_from_folder.py DT1_2000 10   # Run bin_id 10 from DT1_2000

The input folder must contain:
    - input_table.csv   (bin definitions)
    - materials.csv     (material properties)
    - mesh.py           (mesh configuration)
    - <scenario>.py     (any .py file except mesh.py → used as scenario)

Results are saved to <input_folder>/results_<folder_name>/
"""

import os
import sys
import glob
import argparse

# ---------------------------------------------------------------------------
# Path setup (same as run_new_csv_bin.py)
# ---------------------------------------------------------------------------
if "PFC_TT_PATH" not in os.environ and "HISP_PFC_TT_PATH" not in os.environ:
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    os.environ["PFC_TT_PATH"] = repo_root

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, parent_dir)

hisp_src = os.path.abspath(os.path.join(parent_dir, "hisp", "src"))
if hisp_src not in sys.path:
    sys.path.insert(0, hisp_src)


def find_scenario_file(input_dir: str) -> str:
    """Find the scenario .py file in input_dir (any .py except mesh.py)."""
    py_files = glob.glob(os.path.join(input_dir, "*.py"))
    candidates = [f for f in py_files if os.path.basename(f) != "mesh.py"]
    if not candidates:
        raise FileNotFoundError(
            f"No scenario .py file found in '{input_dir}' (excluding mesh.py)"
        )
    if len(candidates) > 1:
        names = [os.path.basename(f) for f in candidates]
        print(f"[WARN] Multiple scenario candidates: {names}. Using {names[0]}")
    return candidates[0]


def main():
    parser = argparse.ArgumentParser(
        description="Run a single bin simulation locally from an input folder",
        usage="%(prog)s input_folder bin_id",
    )
    parser.add_argument("input_folder", help="Path to the input folder (e.g. DT1_5)")
    parser.add_argument("bin_id", type=int, help="Bin ID (1-based row number in input_table.csv)")
    args = parser.parse_args()

    input_dir = args.input_folder
    bin_id = args.bin_id

    # ---- Validate required files ----
    required = ["input_table.csv", "materials.csv", "mesh.py"]
    for fname in required:
        fpath = os.path.join(input_dir, fname)
        if not os.path.exists(fpath):
            print(f"Error: {fpath} not found!")
            sys.exit(1)

    csv_file = os.path.join(input_dir, "input_table.csv")
    scenario_file = find_scenario_file(input_dir)
    scenario_name = os.path.splitext(os.path.basename(scenario_file))[0]

    print("=" * 60)
    print("Run Single Bin from Folder (local)")
    print("=" * 60)
    print(f"  Input folder : {input_dir}")
    print(f"  CSV file     : {csv_file}")
    print(f"  Scenario     : {scenario_name}")
    print(f"  Bin ID (row) : {bin_id}")
    print("=" * 60)

    # ---- Build the same argv that slurm_folder_jobs.sh would pass ----
    # run_new_csv_bin.py expects: bin_id  scenario_folder  scenario_name  csv_file  --input-dir INPUT_DIR
    sys.argv = [
        "run_on_cluster/run_new_csv_bin.py",
        str(bin_id),
        input_dir,          # scenario_folder
        scenario_name,       # scenario_name
        csv_file,            # csv_file
        "--input-dir", input_dir,
    ]

    # ---- Execute the runner script (same as SLURM would) ----
    runner_path = os.path.join(os.path.dirname(__file__), "run_new_csv_bin.py")
    runner_path = os.path.abspath(runner_path)

    # Use runpy to execute it as __main__ so it behaves identically
    import runpy
    runpy.run_path(runner_path, run_name="__main__")


if __name__ == "__main__":
    main()

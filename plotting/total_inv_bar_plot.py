
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tritium inventory per bin (bar plot)

- Loads wall surface areas and divertor geometry-derived areas
- Scans JSON result files, accumulates per-bin Tritium inventory over time
- Converts to grams and plots a bar chart at a chosen snapshot time
  (either total per bin or stacked Tungsten vs Boron per bin)

Assumptions:
- Wall surface CSV columns: "Slow", "Stot", "Shigh"
- Divertor geometry CSV columns: "R_Start","R_End","Z_Start","Z_End"
- JSON files contain:
    - "t": list of times [s]
    - Other keys with dicts containing "data": list of values over time
      Tritium inventories have "T" in the key.
      Wall sub-bins identified via key name containing "shadow", "low", or "high".
- Divertor bin IDs are offset by +18 to align with wall indexing.
"""

# -----------------------
# User-configurable settings (edit these)
# -----------------------

from pathlib import Path

# Input/output paths
RESULTS_DIR = Path("../results_do_nothing_K")  # Directory with JSON files
INPUT_TABLE_CSV = Path("../input_files/input_table.csv")  # Input table with bin configuration
PLOTS_DIR = Path("./plots_do_nothing_K")

# Time settings
TARGET_INTERVAL = 100.0                     # seconds (build common time grid every ~100s)
SNAPSHOT_TIME = None                        # e.g., 36000 for 10h; None => use last time point

# Plot options
STACKED = True                             # True: stacked bars (W vs B); False: single total column
SMOOTH_WINDOW = 1                           # Moving average window applied before snapshot (>=1)
FIGSIZE = (12.0, 6.0)                       # Figure size (width, height)

# -----------------------
# Imports
# -----------------------

import json
import csv
import re
import numpy as np
import matplotlib.pyplot as plt


# -----------------------
# Helper functions
# -----------------------

def parse_filename(stem: str):
    """Parse CSV bin filename to extract bin number, component, and mode.
    
    Expected format: csv_bin_id_{id}_num_{bin_number}_{material}_{mode}.json
    where bin_number determines if it's wall (1-18) or divertor (19+)
    
    Returns: (component, bin_number, mode)
    """
    # Extract bin_number (the actual ITER bin number, not the CSV row id)
    num_match = re.search(r"_num_(\d+)", stem)
    if not num_match:
        return None, None, None
    
    bin_number = int(num_match.group(1))
    
    # Determine component based on bin number
    # Bins 1-18 are first wall, 19+ are divertor
    component = "wall" if bin_number <= 18 else "divertor"
    
    # Extract mode from filename
    mode = None
    if "high_wetted" in stem:
        mode = "high"
    elif "low_wetted" in stem:
        mode = "low"
    elif "shadowed" in stem or "shadow" in stem:
        mode = "shadow"
    elif "wetted" in stem:
        mode = "high"  # default wetted to high
    
    return component, bin_number, mode


def get_material(data: dict):
    """Infer material from JSON content via trap counts (heuristic from your script)."""
    traps = [k for k in data.keys() if "trap" in k.lower()]
    return "Tungsten" if len(traps) == 4 else "Boron"


def load_surface_data_from_input_table(csv_path: Path):
    """Load surface area data from input_table.csv
    
    Returns a dict mapping bin_number to a dict with:
        - Stot: total surface area
        - Shigh: high wetted surface area
        - Slow: low wetted surface area
        - Sshadow: shadowed surface area
    """
    surface_data = {}
    
    with open(csv_path, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            bin_num = int(row["Bin number"])
            mode = row["mode"]
            surface_area = float(row["Surface area (m^2)"])
            location = row["location"]
            
            # Skip divertor bins
            if location.upper() in ["DIV", "DIVERTOR"]:
                continue
            
            # Initialize bin data if not present
            if bin_num not in surface_data:
                parent_area = float(row["S. Area parent bin (m^2)"])
                surface_data[bin_num] = {
                    "Stot": parent_area,
                    "Shigh": 0.0,
                    "Slow": 0.0,
                    "Sshadow": 0.0
                }
            
            # Assign area based on mode
            if "high" in mode.lower():
                surface_data[bin_num]["Shigh"] = surface_area
            elif "low" in mode.lower():
                surface_data[bin_num]["Slow"] = surface_area
            elif "shadow" in mode.lower():
                surface_data[bin_num]["Sshadow"] = surface_area
            elif mode.lower() == "wetted":
                # For simple "wetted" mode, treat as high wetted
                surface_data[bin_num]["Shigh"] = surface_area
    
    return surface_data


def load_divertor_areas_from_input_table(csv_path: Path):
    """Load divertor bin areas from input_table.csv"""
    divertor_areas = {}
    
    with open(csv_path, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            bin_num = int(row["Bin number"])
            location = row["location"]
            surface_area = float(row["Surface area (m^2)"])
            
            # Only process divertor bins
            if location.upper() in ["DIV", "DIVERTOR"]:
                divertor_areas[bin_num] = surface_area
    
    return divertor_areas


def find_nearest_index(array: np.ndarray, value: float) -> int:
    """Index of nearest value in array."""
    return int(np.abs(array - value).argmin())


def moving_average(data: np.ndarray, window_size: int) -> np.ndarray:
    """Centered moving average with padding to preserve length."""
    if window_size <= 1:
        return data
    smoothed = np.convolve(data, np.ones(window_size) / window_size, mode="valid")
    pad_width = (len(data) - len(smoothed)) // 2
    if len(smoothed) > 0:
        result = np.pad(
            smoothed,
            (pad_width, len(data) - len(smoothed) - pad_width),
            mode="edge",
        )
    else:
        result = data.copy()
    return result


# -----------------------
# Main
# -----------------------

def main():
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    # Load area data from input_table.csv
    surface_data = load_surface_data_from_input_table(INPUT_TABLE_CSV)
    divertor_areas = load_divertor_areas_from_input_table(INPUT_TABLE_CSV)

    # Collect JSON result files
    json_files = sorted(RESULTS_DIR.glob("*.json"))
    if not json_files:
        print(f"[WARN] No JSON files found in {RESULTS_DIR.resolve()}")
        return

    # Build common time grid (every TARGET_INTERVAL seconds)
    max_time = 0.0
    for jf in json_files:
        with open(jf, "r") as f:
            data = json.load(f)
        if "t" in data and len(data["t"]) > 0:
            max_time = max(max_time, float(max(data["t"])))
    if max_time <= 0.0:
        print("[WARN] No valid time data found in JSON files.")
        return

    target_times = np.arange(0.0, max_time + TARGET_INTERVAL, TARGET_INTERVAL, dtype=float)

    # Global totals (kept for completeness; not required for bar plot)
    W_totals_wall = np.zeros_like(target_times, dtype=float)
    B_totals_wall = np.zeros_like(target_times, dtype=float)
    W_totals_div = np.zeros_like(target_times, dtype=float)
    B_totals_div = np.zeros_like(target_times, dtype=float)

    # Per-bin time series (to build bar plot at snapshot)
    bin_W: dict[int, np.ndarray] = {}
    bin_B: dict[int, np.ndarray] = {}

    # Process each JSON file
    for jf in json_files:
        with open(jf, "r") as f:
            data = json.load(f)

        if "t" not in data:
            continue

        t_array = np.array(data["t"], dtype=float)
        component, bin_id, mode = parse_filename(jf.stem)
        if bin_id is None:
            # skip files that don't encode a bin id
            continue

        material = get_material(data)

        if component == "wall":
            surf = surface_data.get(bin_id)
            if not surf:
                # unknown wall bin id in surface table
                continue

            # Determine area from mode (each JSON file represents one mode)
            if mode == "high":
                area = surf["Shigh"]
            elif mode == "low":
                area = surf["Slow"]
            elif mode == "shadow":
                area = surf["Sshadow"]
            else:
                area = surf["Stot"]  # fallback

            # Sum inventory for Tritium keys
            for key, values in data.items():
                if key == "t" or "flux" in key.lower():
                    continue
                if isinstance(values, dict) and "data" in values:
                    arr = np.array(values["data"], dtype=float)
                    if "T" in key:  # Tritium inventory
                        for i, target_t in enumerate(target_times):
                            idx = find_nearest_index(t_array, target_t)
                            inv_val = arr[idx]  # inventory at nearest time
                            val = inv_val * area  # scale by area

                            if material == "Tungsten":
                                W_totals_wall[i] += val
                                if bin_id not in bin_W:
                                    bin_W[bin_id] = np.zeros_like(target_times, dtype=float)
                                bin_W[bin_id][i] += val
                            else:
                                B_totals_wall[i] += val
                                if bin_id not in bin_B:
                                    bin_B[bin_id] = np.zeros_like(target_times, dtype=float)
                                bin_B[bin_id][i] += val

        elif component == "divertor":
            area = divertor_areas.get(bin_id)
            if not area:
                # unknown divertor bin id in geometry
                continue

            # Sum inventory for Tritium keys (no sub-bins for divertor)
            for key, values in data.items():
                if key == "t" or "flux" in key.lower():
                    continue
                if isinstance(values, dict) and "data" in values:
                    arr = np.array(values["data"], dtype=float)
                    if "T" in key:  # Tritium inventory
                        for i, target_t in enumerate(target_times):
                            idx = find_nearest_index(t_array, target_t)
                            inv_val = arr[idx]
                            val = inv_val * area

                            if material == "Tungsten":
                                W_totals_div[i] += val
                                if bin_id not in bin_W:
                                    bin_W[bin_id] = np.zeros_like(target_times, dtype=float)
                                bin_W[bin_id][i] += val
                            else:
                                B_totals_div[i] += val
                                if bin_id not in bin_B:
                                    bin_B[bin_id] = np.zeros_like(target_times, dtype=float)
                                bin_B[bin_id][i] += val

    # Optional smoothing of per-bin series before snapshot
    if SMOOTH_WINDOW > 1:
        for b in list(bin_W.keys()):
            bin_W[b] = moving_average(bin_W[b], SMOOTH_WINDOW)
        for b in list(bin_B.keys()):
            bin_B[b] = moving_average(bin_B[b], SMOOTH_WINDOW)

    # Choose snapshot index
    if SNAPSHOT_TIME is not None:
        snapshot_idx = find_nearest_index(target_times, float(SNAPSHOT_TIME))
    else:
        snapshot_idx = len(target_times) - 1  # last time point

    # Convert to grams
    avogadro = 6.02214076e23  # atoms/mol
    tritium_mass = 3.0160492  # g/mol

    # Determine all possible bin IDs from surface data and divertor data
    wall_bin_ids = set(surface_data.keys())
    divertor_bin_ids = set(divertor_areas.keys())
    all_possible_bins = sorted(wall_bin_ids | divertor_bin_ids)
    
    if not all_possible_bins:
        print("[WARN] No valid bin data found.")
        return

    # Gather bins and compute W, B, total in grams at snapshot
    # Include ALL possible bins, even those with no data (they'll show as 0)
    W_g, B_g, Total_g = [], [], []
    for b in all_possible_bins:
        if b in bin_W:
            w_val = bin_W[b][snapshot_idx]
        else:
            w_val = 0.0
            
        if b in bin_B:
            b_val = bin_B[b][snapshot_idx]
        else:
            b_val = 0.0
            
        w_g = tritium_mass * w_val / avogadro
        b_g = tritium_mass * b_val / avogadro
        W_g.append(w_g)
        B_g.append(b_g)
        Total_g.append(w_g + b_g)

    # -----------------------
    # Plot: bar chart per bin
    # -----------------------
    
    x = np.arange(len(all_possible_bins))                     # positions for bars
    
    if STACKED:
        fig, ax = plt.subplots(figsize=FIGSIZE)
        
        # For bins with no data, show a small gray bar
        W_plot = [max(w, 1e-3) if w == 0 and b == 0 else w for w, b in zip(W_g, B_g)]
        B_plot = [max(b, 1e-3) if w == 0 and b == 0 else b for w, b in zip(W_g, B_g)]
        
        # Plot bars with different colors for data vs no-data bins
        has_data = [w > 0 or b > 0 for w, b in zip(W_g, B_g)]
        
        # Separate data and no-data bins for proper legend
        for i, x_pos in enumerate(x):
            if has_data[i]:
                ax.bar(x_pos, W_plot[i], color="tab:blue", alpha=0.95, 
                      label="T in Tungsten" if i == 0 or not any(has_data[:i]) else "")
                ax.bar(x_pos, B_plot[i], bottom=W_plot[i], color="tab:green", alpha=0.95,
                      label="T in Boron" if i == 0 or not any(has_data[:i]) else "")
            else:
                ax.bar(x_pos, W_plot[i], color="lightgray", alpha=0.5,
                      label="No data" if not any([not has_data[j] for j in range(i)]) else "")
        
        # Title without time
        ax.set_title("Tritium retained at the end of the scenario per bin and material")
        out_name = PLOTS_DIR / "tritium_inventory_per_bin_stacked.png"
    else:
        fig, ax = plt.subplots(figsize=FIGSIZE)
        # For bins with no data, show a small gray bar
        Total_plot = [max(t, 1e-3) if t == 0 else t for t in Total_g]
        has_data = [t > 0 for t in Total_g]
        
        # Plot bars with different colors for data vs no-data bins
        for i, x_pos in enumerate(x):
            if has_data[i]:
                ax.bar(x_pos, Total_plot[i], color="tab:purple", alpha=0.9,
                      label="Total T (W+B)" if i == 0 or not any(has_data[:i]) else "")
            else:
                ax.bar(x_pos, Total_plot[i], color="lightgray", alpha=0.5,
                      label="No data" if not any([not has_data[j] for j in range(i)]) else "")
        
        ax.set_title("Tritium retained at the end of the scenario per bin and material")
        out_name = PLOTS_DIR / "tritium_inventory_per_bin_total.png"
    
    # Use actual bin numbers for x-axis labels (already 1-based from input_table.csv)
    tick_idx = x[::2]                 # every 2 bins
    tick_labels = [str(all_possible_bins[i]) for i in range(0, len(all_possible_bins), 2)]
    
    ax.set_xticks(tick_idx)
    ax.set_xticklabels(tick_labels, rotation=0)
    
    ax.set_xlabel("Bin number")
    ax.set_ylabel("Tritium Inventory (g)")
    ax.set_yscale("log")
    ax.set_ylim(bottom=3e-4)  # Set minimum y-axis value
    ax.grid(axis="y", linestyle="--", linewidth=0.6)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_name, dpi=300)
    print(f"[OK] Saved bar plot: {out_name.resolve()}")



if __name__ == "__main__":
    main()

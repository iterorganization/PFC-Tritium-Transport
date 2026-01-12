
import json
import csv
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import re

# -------- CONFIG --------
RESULTS_DIR = Path("../results_do_nothing_K")  # Directory with JSON files
INPUT_TABLE_CSV = Path("../input_files/input_table.csv")  # Input table with bin configuration
PLOTS_DIR = Path("./plots_do_nothing_K")
FIGSIZE = (6, 8)  # Taller figure for two subplots
LEFT_XLIM_HOURS = 0.001
RIGHT_XLIM_HOURS = 250
TARGET_INTERVAL = 100  # seconds
# -------------------------.

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

def get_material(data):
    traps = [k for k in data.keys() if "trap" in k.lower()]
    return "Tungsten" if len(traps) == 4 else "Boron"

def load_surface_data_from_input_table(csv_path):
    """Load surface area data from input_table.csv
    
    Returns a dict mapping bin_number to a dict with:
        - Stot: total surface area
        - Shigh: high wetted surface area
        - Slow: low wetted surface area
        - Sshadow: shadowed surface area
    """
    surface_data = {}
    
    with open(csv_path, "r") as f:
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

def load_divertor_areas_from_input_table(csv_path):
    """Load divertor bin areas from input_table.csv"""
    divertor_areas = {}
    
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            bin_num = int(row["Bin number"])
            location = row["location"]
            surface_area = float(row["Surface area (m^2)"])
            
            # Only process divertor bins
            if location.upper() in ["DIV", "DIVERTOR"]:
                divertor_areas[bin_num] = surface_area
    
    return divertor_areas

def find_nearest_index(array, value):
    return int(np.abs(array - value).argmin())

def moving_average(data, window_size):
    """Calculate moving average with specified window size, handling boundaries properly"""
    if window_size <= 1:
        return data
    
    # Use valid mode to avoid boundary effects, then pad the result
    smoothed = np.convolve(data, np.ones(window_size)/window_size, mode='valid')
    
    # Calculate how many points we lost on each side
    pad_width = (len(data) - len(smoothed)) // 2
    
    # Pad the beginning and end to maintain original length
    # Use the first and last smoothed values for padding
    if len(smoothed) > 0:
        result = np.pad(smoothed, (pad_width, len(data) - len(smoothed) - pad_width), 
                       mode='edge')
    else:
        result = data.copy()
    
    return result

def main():
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    surface_data = load_surface_data_from_input_table(INPUT_TABLE_CSV)
    divertor_areas = load_divertor_areas_from_input_table(INPUT_TABLE_CSV)
    json_files = sorted(RESULTS_DIR.glob("*.json"))
    if not json_files:
        print(f"[WARN] No JSON files found in {RESULTS_DIR.resolve()}")
        return

    # Build a common time grid (every ~100s)
    max_time = 0
    for jf in json_files:
        with open(jf, "r") as f:
            data = json.load(f)
        if "t" in data:
            max_time = max(max_time, max(data["t"]))

    target_times = np.arange(0, max_time + TARGET_INTERVAL, TARGET_INTERVAL)

    # Initialize totals for wall bins
    W_totals_wall = np.zeros_like(target_times, dtype=float)
    B_totals_wall = np.zeros_like(target_times, dtype=float)
    
    # Initialize totals for divertor bins
    W_totals_div = np.zeros_like(target_times, dtype=float)
    B_totals_div = np.zeros_like(target_times, dtype=float)

    for jf in json_files:
        with open(jf, "r") as f:
            data = json.load(f)

        if "t" not in data:
            continue

        t_array = np.array(data["t"], dtype=float)
        component, bin_id, mode = parse_filename(jf.stem)
        if bin_id is None:
            continue

        material = get_material(data)

        if component == "wall":
            # Wall bin processing - each JSON file is one mode of one bin
            surf = surface_data.get(bin_id)
            if not surf or mode is None:
                continue

            # Get area based on mode from filename
            if mode == "shadow":
                area = surf["Sshadow"]
            elif mode == "low":
                area = surf["Slow"]
            elif mode == "high":
                area = surf["Shigh"]
            else:
                area = surf["Stot"]  # fallback

            # Sum inventory for ALL Tritium keys in this file
            for key, values in data.items():
                if key == "t" or "flux" in key.lower():
                    continue
                if isinstance(values, dict) and "data" in values:
                    arr = np.array(values["data"], dtype=float)
                    if "T" in key:  # Tritium inventory
                        for i, target_t in enumerate(target_times):
                            idx = find_nearest_index(t_array, target_t)
                            inv_val = arr[idx]

                            if material == "Tungsten":
                                W_totals_wall[i] += inv_val * area
                            else:
                                B_totals_wall[i] += inv_val * area

        elif component == "divertor":
            # Divertor bin processing
            area = divertor_areas.get(bin_id)
            if not area:
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

                            if material == "Tungsten":
                                W_totals_div[i] += inv_val * area
                            else:
                                B_totals_div[i] += inv_val * area

    # Convert time to hours
    times_hours = target_times / 3600.0
    avogadro = 6.02214076e23  # atoms/mol
    tritium_mass = 3.0160492  # g/mol

    # Apply moving average for smoothing
 

    # Calculate total inventories (W + B) for analysis
    total_wall_inventory = W_totals_wall + B_totals_wall
    total_div_inventory = W_totals_div + B_totals_div

    # Create subplot layout
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=FIGSIZE, sharex=True)
    
    # Top plot: Divertor inventory
    ax1.plot(times_hours, tritium_mass*W_totals_div/avogadro, label="Total T in Tungsten", color="tab:blue", linewidth=2)
    ax1.plot(times_hours, tritium_mass*B_totals_div/avogadro, label="Total T in Boron", color="tab:green", linewidth=2)
    ax1.plot(times_hours, tritium_mass*total_div_inventory/avogadro, label="Total T", color="black", linewidth=2)
    ax1.set_xscale("log")
    ax1.set_xlim(left=times_hours[0] if times_hours[0] > 0 else times_hours[1], right=times_hours[-1])  # Start from first non-zero time
    ax1.set_ylabel("Total Tritium Inventory (g)")
    ax1.set_title("Tritium Inventory in the Divertor")
    ax1.grid(which="both", linestyle="--", linewidth=0.5)
    ax1.legend()
    
    # Bottom plot: Wall inventory
    ax2.plot(times_hours, tritium_mass*W_totals_wall/avogadro, label="Total T in Tungsten", color="tab:blue", linewidth=2)
    ax2.plot(times_hours, tritium_mass*B_totals_wall/avogadro, label="Total T in Boron", color="tab:green", linewidth=2)
    ax2.plot(times_hours, tritium_mass*total_wall_inventory/avogadro, label="Total T", color="black", linewidth=2)
    ax2.set_xscale("log")
    ax2.set_xlim(left=times_hours[0] if times_hours[0] > 0 else times_hours[1], right=times_hours[-1])  # Start from first non-zero time
    ax2.set_xlabel("Time (hours)")
    ax2.set_ylabel("Total Tritium Inventory (g)")
    ax2.set_title("Tritium Inventory in the First Wall")
    ax2.grid(which="both", linestyle="--", linewidth=0.5)
    ax2.legend()
    
    plt.tight_layout()

    out_png = PLOTS_DIR / "total_inventory_combined.png"
    fig.savefig(out_png, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(f"[OK] Saved {out_png.name}")

if __name__ == "__main__":
    main()

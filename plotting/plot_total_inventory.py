
import json
import csv
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import re

# -------- CONFIG --------
RESULTS_DIR = Path("../Results_do_nothing_complete")  # Directory with JSON files
INPUT_TABLE_CSV = Path("../input_files/input_table.csv")  # Input table with bin configuration
PLOTS_DIR = Path("./plots_do_nothing_complete")
FIGSIZE = (6, 8)  # Taller figure for two subplots
LEFT_XLIM_HOURS = 0.001
RIGHT_XLIM_HOURS = 250
TARGET_INTERVAL = 100  # seconds
# -------------------------.

def parse_filename(stem: str):
    """Parse bin filename to extract bin number, component, and mode.
    
    Supports two formats:
    1. New format: id_{id}_bin_num_{bin_number}_{material}_{mode}.json
    2. Old format: wall_bin_{bin_number}_sub_bin_{mode}.json or div_bin_{bin_number}.json
    
    Returns: (component, bin_number, mode)
    """
    # Try new format first: _num_(\d+)
    num_match = re.search(r"_num_(\d+)", stem)
    
    # If not found, try old format: wall_bin_(\d+) or div_bin_(\d+)
    if not num_match:
        wall_match = re.search(r"wall_bin_(\d+)", stem)
        div_match = re.search(r"div_bin_(\d+)", stem)
        
        if wall_match:
            bin_number = int(wall_match.group(1))
            component = "wall"
        elif div_match:
            bin_number = int(div_match.group(1))
            component = "divertor"
        else:
            return None, None, None
    else:
        bin_number = int(num_match.group(1))
        # Determine component based on bin number
        # Bins 1-18 are first wall, 19+ are divertor
        component = "wall" if bin_number <= 18 else "divertor"
    
    # Extract mode from filename
    mode = None
    if "high_wetted" in stem or "highwetted" in stem:
        mode = "high"
    elif "low_wetted" in stem or "lowwetted" in stem:
        mode = "low"
    elif "shadowed" in stem or "shadow" in stem:
        mode = "shadow"
    elif "wetted" in stem:
        mode = "high"  # default wetted to high
    elif "sub_bin" in stem and component == "wall":
        # Old format: wall_bin_{N}_sub_bin_{mode}
        sub_match = re.search(r"sub_bin_(\w+)", stem)
        if sub_match:
            mode_str = sub_match.group(1)
            if "shadow" in mode_str:
                mode = "shadow"
            elif "low" in mode_str:
                mode = "low"
            else:
                mode = "high"
    
    # For divertor bins in old format, mode defaults to None (no sub-bins)
    
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

    # Track which bins are being processed
    processed_bins = set()
    skipped_files = []
    processed_files = []
    
    print(f"\n[INFO] Found {len(json_files)} total JSON files (including sub-bins)")
    
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

    files_processed_count = 0
    
    for jf in json_files:
        with open(jf, "r") as f:
            data = json.load(f)

        if "t" not in data:
            continue

        t_array = np.array(data["t"], dtype=float)
        component, bin_id, mode = parse_filename(jf.stem)
        if bin_id is None:
            skipped_files.append((jf.name, "Failed to parse filename"))
            continue

        material = get_material(data)
        processed_bins.add(bin_id)

        if component == "wall":
            # Wall bin processing - each JSON file is one mode of one bin
            surf = surface_data.get(bin_id)
            if not surf or mode is None:
                skipped_files.append((jf.name, f"Missing surface data or mode (bin {bin_id}, mode {mode})"))
                continue

            files_processed_count += 1
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

            files_processed_count += 1
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

    # Print diagnostic information
    print("\n" + "="*80)
    print("BIN PROCESSING DIAGNOSTIC")
    print("="*80)
    print(f"Total JSON files found: {len(json_files)}")
    print(f"Files successfully processed: {files_processed_count}")
    print(f"Unique bins (parent) involved: {len(processed_bins)}")
    print(f"Bins: {sorted(processed_bins)}")
    
    if skipped_files:
        print(f"\nSkipped {len(skipped_files)} files:")
        for fname, reason in skipped_files[:10]:  # Show first 10
            print(f"  - {fname}: {reason}")
        if len(skipped_files) > 10:
            print(f"  ... and {len(skipped_files) - 10} more")
    
    # Check for missing bins (should be 1-62)
    all_expected_bins = set(range(1, 63))
    missing_bins = all_expected_bins - processed_bins
    if missing_bins:
        print(f"\n[WARNING] Missing bins: {sorted(missing_bins)}")
    else:
        print(f"\n[OK] All 62 bins (1-62) were processed!")
    print("="*80 + "\n")

    # Apply moving average for smoothing
 

    # Calculate total inventories (W + B) for analysis
    total_wall_inventory = W_totals_wall + B_totals_wall
    total_div_inventory = W_totals_div + B_totals_div
    
    # Print tritium mass in each bin at the final time point
    print("\n" + "="*80)
    print("TRITIUM MASS STORED IN EACH BIN (at final time)")
    print("="*80)
    final_time_idx = -1  # Last time point
    
    for jf in json_files:
        with open(jf, "r") as f:
            data = json.load(f)
        
        if "t" not in data:
            continue
        
        component, bin_id, mode = parse_filename(jf.stem)
        if bin_id is None:
            continue
        
        material = get_material(data)
        
        if component == "wall":
            surf = surface_data.get(bin_id)
            if not surf or mode is None:
                continue
            
            # Get area based on mode
            if mode == "shadow":
                area = surf["Sshadow"]
            elif mode == "low":
                area = surf["Slow"]
            elif mode == "high":
                area = surf["Shigh"]
            else:
                area = surf["Stot"]
            
            # Sum tritium inventory for final time
            final_inventory_atoms = 0.0
            for key, values in data.items():
                if key == "t" or "flux" in key.lower():
                    continue
                if isinstance(values, dict) and "data" in values:
                    arr = np.array(values["data"], dtype=float)
                    if "T" in key:
                        final_inventory_atoms += arr[final_time_idx]
            
            # Convert to mass
            final_mass_grams = (final_inventory_atoms * area * tritium_mass) / avogadro
            
            print(f"Wall Bin {bin_id:2d} ({material:8s}, {mode:6s}): "
                  f"Inventory = {final_inventory_atoms:.6e} atoms, "
                  f"Area = {area:.6e} m², "
                  f"Total T mass = {final_mass_grams:.6e} g")
        
        elif component == "divertor":
            area = divertor_areas.get(bin_id)
            if not area:
                continue
            
            # Sum tritium inventory for final time
            final_inventory_atoms = 0.0
            for key, values in data.items():
                if key == "t" or "flux" in key.lower():
                    continue
                if isinstance(values, dict) and "data" in values:
                    arr = np.array(values["data"], dtype=float)
                    if "T" in key:
                        final_inventory_atoms += arr[final_time_idx]
            
            # Convert to mass
            final_mass_grams = (final_inventory_atoms * area * tritium_mass) / avogadro
            
            print(f"Divertor Bin {bin_id:2d} ({material:8s}): "
                  f"Inventory = {final_inventory_atoms:.6e} atoms, "
                  f"Area = {area:.6e} m², "
                  f"Total T mass = {final_mass_grams:.6e} g")
    
    print("="*80 + "\n")
    
    # Verification: Total inventory at final time point
    print("="*80)
    print("TOTAL INVENTORY VERIFICATION (at final time)")
    print("="*80)
    final_W_wall_mass = tritium_mass * W_totals_wall[-1] / avogadro
    final_B_wall_mass = tritium_mass * B_totals_wall[-1] / avogadro
    final_W_div_mass = tritium_mass * W_totals_div[-1] / avogadro
    final_B_div_mass = tritium_mass * B_totals_div[-1] / avogadro
    
    print(f"First Wall - Tungsten: {final_W_wall_mass:.6e} g")
    print(f"First Wall - Boron:    {final_B_wall_mass:.6e} g")
    print(f"First Wall - TOTAL:    {final_W_wall_mass + final_B_wall_mass:.6e} g")
    print(f"Divertor - Tungsten:   {final_W_div_mass:.6e} g")
    print(f"Divertor - Boron:      {final_B_div_mass:.6e} g")
    print(f"Divertor - TOTAL:      {final_W_div_mass + final_B_div_mass:.6e} g")
    print(f"\nGRAND TOTAL TRITIUM:   {final_W_wall_mass + final_B_wall_mass + final_W_div_mass + final_B_div_mass:.6e} g")
    print("="*80 + "\n")

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

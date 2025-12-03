
import json
import csv
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import re

# -------- CONFIG --------
RESULTS_DIR = Path("../results_capability_test_2")  # Directory with JSON files
CSV_FILE = Path("/home/ITER/llealsa/AdriaLlealS/PFC-Tritium-Transport/iter_bins/Wetted_Frac_Bin_Data.csv")         # CSV file with bin surface data
DIVERTOR_BIN_FILE = Path("/home/ITER/llealsa/AdriaLlealS/PFC-Tritium-Transport/iter_bins/iter_bins.dat")  # Divertor bin geometry data
PLOTS_DIR = Path("./plots_capability_test_2")
FIGSIZE = (6, 8)  # Taller figure for two subplots
LEFT_XLIM_HOURS = 0.001
RIGHT_XLIM_HOURS = 250
TARGET_INTERVAL = 100  # seconds
MOVING_AVERAGE_WINDOW = 0  # Window size for moving average smoothing
# -------------------------.

def parse_filename(stem: str):
    component = "wall" if "wall" in stem else "divertor"
    bin_match = re.search(r"bin[_\-\s]?(\d+)", stem)
    bin_id = int(bin_match.group(1)) if bin_match else None
    return component, bin_id

def get_material(data):
    traps = [k for k in data.keys() if "trap" in k.lower()]
    return "Tungsten" if len(traps) == 4 else "Boron"

def load_surface_data(csv_path):
    surface_data = {}
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            surface_data[idx] = {
                "Slow": float(row["Slow"]),
                "Stot": float(row["Stot"]),
                "Shigh": float(row["Shigh"])
            }
    return surface_data

def load_divertor_bin_data(dat_path):
    """Load divertor bin geometry data and calculate areas"""
    divertor_areas = {}
    with open(dat_path, "r") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            # Calculate area: A = pi * abs(R_start + R_End) * abs(Z_End - Z_Start)
            r_start = float(row["R_Start"])
            r_end = float(row["R_End"])
            z_start = float(row["Z_Start"])
            z_end = float(row["Z_End"])
            
            area = np.pi * abs(r_start + r_end) * abs(z_end - z_start)
            divertor_areas[idx + 18] = area  # Divertor bins start at index 18
    
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

    surface_data = load_surface_data(CSV_FILE)
    divertor_areas = load_divertor_bin_data(DIVERTOR_BIN_FILE)
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
        component, bin_id = parse_filename(jf.stem)
        if bin_id is None:
            continue

        material = get_material(data)

        if component == "wall":
            # Wall bin processing
            surf = surface_data.get(bin_id)
            if not surf:
                continue

            # Areas for wall bins
            slow_area = surf["Slow"]
            shigh_area = surf["Shigh"]
            shadow_area = surf["Stot"] - shigh_area - slow_area

            # Sum inventory for Tritium keys
            for key, values in data.items():
                if key == "t" or "flux" in key.lower():
                    continue
                if isinstance(values, dict) and "data" in values:
                    arr = np.array(values["data"], dtype=float)
                    if "T" in key:  # Tritium inventory
                        for i, target_t in enumerate(target_times):
                            idx = find_nearest_index(t_array, target_t)
                            inv_val = arr[idx]
                            # Assign area based on sub-bin type
                            if "shadow" in key.lower():
                                area = shadow_area
                            elif "low" in key.lower():
                                area = slow_area
                            elif "high" in key.lower():
                                area = shigh_area
                            else:
                                area = surf["Stot"]  # fallback

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

    # Debug: Check initial values before smoothing
    print(f"[DEBUG] Raw values at first few time points:")
    print(f"  Times (hours): {times_hours[:5]}")
    print(f"  W_wall (g): {tritium_mass * W_totals_wall[:5] / avogadro}")
    print(f"  B_wall (g): {tritium_mass * B_totals_wall[:5] / avogadro}")
    print(f"  W_div (g): {tritium_mass * W_totals_div[:5] / avogadro}")
    print(f"  B_div (g): {tritium_mass * B_totals_div[:5] / avogadro}")

    # Apply moving average for smoothing
    W_totals_wall_smooth = moving_average(W_totals_wall, MOVING_AVERAGE_WINDOW)
    B_totals_wall_smooth = moving_average(B_totals_wall, MOVING_AVERAGE_WINDOW)
    total_wall_smooth = moving_average(W_totals_wall + B_totals_wall, MOVING_AVERAGE_WINDOW)
    
    W_totals_div_smooth = moving_average(W_totals_div, MOVING_AVERAGE_WINDOW)
    B_totals_div_smooth = moving_average(B_totals_div, MOVING_AVERAGE_WINDOW)
    total_div_smooth = moving_average(W_totals_div + B_totals_div, MOVING_AVERAGE_WINDOW)

    # Debug: Check values after smoothing
    #print(f"[DEBUG] Smoothed values at first few time points:")
    #print(f"  W_wall_smooth (g): {tritium_mass * W_totals_wall_smooth[:5] / avogadro}")
    #print(f"  B_wall_smooth (g): {tritium_mass * B_totals_wall_smooth[:5] / avogadro}")
    #print(f"  W_div_smooth (g): {tritium_mass * W_totals_div_smooth[:5] / avogadro}")
    #print(f"  B_div_smooth (g): {tritium_mass * B_totals_div_smooth[:5] / avogadro}")

    # Calculate total inventories (W + B) for analysis
    total_wall_inventory = W_totals_wall_smooth + B_totals_wall_smooth
    total_div_inventory = W_totals_div_smooth + B_totals_div_smooth

    # Convert to grams for analysis
    total_wall_inventory_g = tritium_mass * total_wall_inventory / avogadro
    total_div_inventory_g = tritium_mass * total_div_inventory / avogadro

    # Calculate ratios: inventory at last time / maximum inventory
    wall_last_value = total_wall_inventory_g[-1]
    wall_max_value = max(total_wall_inventory_g)
    wall_ratio = wall_last_value / wall_max_value if wall_max_value > 0 else 0

    div_last_value = total_div_inventory_g[-1]
    div_max_value = max(total_div_inventory_g)
    div_ratio = div_last_value / div_max_value if div_max_value > 0 else 0

    print(f"[ANALYSIS] Wall inventory:")
    print(f"  Last time inventory: {wall_last_value:.6e} g")
    print(f"  Maximum inventory: {wall_max_value:.6e} g")
    print(f"  Ratio (last/max): {wall_ratio:.4f}")

    print(f"[ANALYSIS] Divertor inventory:")
    print(f"  Last time inventory: {div_last_value:.6e} g")
    print(f"  Maximum inventory: {div_max_value:.6e} g")
    print(f"  Ratio (last/max): {div_ratio:.4f}")

    # Create subplot layout
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=FIGSIZE, sharex=True)
    
    # Top plot: Divertor inventory
    ax1.plot(times_hours, tritium_mass*W_totals_div_smooth/avogadro, label="Total T in Tungsten", color="tab:blue", linewidth=2)
    ax1.plot(times_hours, tritium_mass*B_totals_div_smooth/avogadro, label="Total T in Boron", color="tab:green", linewidth=2)
    ax1.plot(times_hours, tritium_mass*total_div_smooth/avogadro, label="Total T", color="black", linewidth=2)
    ax1.set_xscale("log")
    ax1.set_xlim(left=times_hours[0] if times_hours[0] > 0 else times_hours[1], right=times_hours[-1])  # Start from first non-zero time
    ax1.set_ylabel("Total Tritium Inventory (g)")
    ax1.set_title("Tritium Inventory in the Divertor")
    ax1.grid(which="both", linestyle="--", linewidth=0.5)
    ax1.legend()
    
    # Bottom plot: Wall inventory
    ax2.plot(times_hours, tritium_mass*W_totals_wall_smooth/avogadro, label="Total T in Tungsten", color="tab:blue", linewidth=2)
    ax2.plot(times_hours, tritium_mass*B_totals_wall_smooth/avogadro, label="Total T in Boron", color="tab:green", linewidth=2)
    ax2.plot(times_hours, tritium_mass*total_wall_smooth/avogadro, label="Total T", color="black", linewidth=2)
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

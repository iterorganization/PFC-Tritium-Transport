import sys
import os
from pathlib import Path

# Add the iter_bins directory to Python path and change working directory
iter_bins_path = Path("/home/ITER/llealsa/AdriaLlealS/PFC-Tritium-Transport-dolfinx10/iter_bins")
project_root = Path("/home/ITER/llealsa/AdriaLlealS/PFC-Tritium-Transport-dolfinx10")
sys.path.insert(0, str(iter_bins_path))
sys.path.insert(0, str(project_root))

# Save current directory and change to iter_bins directory for import
original_cwd = os.getcwd()
os.chdir(iter_bins_path)

try:
    from make_iter_bins import my_reactor, Div_bins, total_fw_bins, FW_bins
finally:
    # Change to project root for scenario import
    os.chdir(project_root)

try:
    from scenarios.do_nothing import scenario as scenario
finally:
    # Restore original working directory
    os.chdir(original_cwd)

from matplotlib.colors import LogNorm
import matplotlib.pyplot as plt
import json
import numpy as np
import math

# Constants
AVOGADROS_CONST = 6.02214076e23
D_AMU = 2.01410177811  # Atomic mass unit for Deuterium
T_AMU = 3.0160492779  # Atomic mass unit for Tritium

# Results directory path
results_dir = Path("/home/ITER/llealsa/AdriaLlealS/PFC-Tritium-Transport-dolfinx10/results_do_nothing")

final_time = (
    scenario.get_maximum_time() - 1
)  # last milestone is two seconds before end of waiting period


def calculate_bin_surface_area(bin_start_point, bin_end_point, bin_length):
    avg_r_coord = 0.5 * abs(bin_start_point[0] + bin_end_point[0])
    return 2 * math.pi * avg_r_coord * bin_length


def load_and_process_bin_data(file_path, final_time):
    try:
        with open(file_path, "r") as file:
            bin_data = json.load(file)
    except FileNotFoundError:
        print(f"Warning: File not found {file_path}, setting inventory to 0")
        return 0.0, 0.0

    sub_data_D = 0
    sub_data_T = 0

    # Get the time array from the top level
    if "t" not in bin_data:
        print(f"Warning: No time array found in {file_path}")
        return 0.0, 0.0
    
    time = np.array(bin_data["t"])
    
    if len(time) == 0:
        print(f"Warning: Empty time array in {file_path}")
        return 0.0, 0.0

    # Find the closest time to final_time
    time_diffs = np.abs(time - float(final_time))
    closest_idx = np.argmin(time_diffs)
    
    print(f"  Processing {file_path}")
    print(f"  Time array length: {len(time)}, closest time: {time[closest_idx]:.1f}, target: {final_time}")

    # Process each species data
    for name, value in bin_data.items():
        if name in ["bin_index", "parent_bin_index", "mode", "temperature_at_x0", "t"]:
            continue

        # Skip if value is not a dictionary or doesn't have expected structure
        if not isinstance(value, dict) or "data" not in value:
            continue

        data = np.array(value["data"])
        
        # Skip if data array is empty
        if len(data) == 0:
            print(f"    {name}: empty data array")
            continue

        # Use the data at the closest time point
        if closest_idx < len(data):
            if "D" in name:
                contribution = data[closest_idx] / AVOGADROS_CONST * D_AMU
                sub_data_D += contribution
                if contribution > 0:
                    print(f"    {name}: D contribution = {contribution:.2e} (raw: {data[closest_idx]:.2e})")
            elif "T" in name:
                contribution = data[closest_idx] / AVOGADROS_CONST * T_AMU
                sub_data_T += contribution
                if contribution > 0:
                    print(f"    {name}: T contribution = {contribution:.2e} (raw: {data[closest_idx]:.2e})")
        else:
            print(f"    {name}: time index {closest_idx} out of range for data length {len(data)}")

    return sub_data_D, sub_data_T


# initialize dicts for plotting
bin_dict_D = {}
bin_dict_T = {}

# first wall bins
for i in range(18):
    print(f'Loading Bin {i}.')
    all_sub_bins_D = 0
    all_sub_bins_T = 0
    bin_length = FW_bins.get_bin(i).length

    # Handle different bin types
    if i in [13, 14, 16, 17]:
        # shadowed and wetted sub-bins
        for mode in ["shadowed", "wetted"]:
            file_path = results_dir / f"wall_bin_{i}_sub_bin_{mode}.json"
            # if mode == "shadowed":
            #     bin_surf_area = FW_bins.get_bin(i).shadowed_subbin.surface_area
            # elif mode == "wetted":
            #     bin_surf_area = FW_bins.get_bin(i).wetted_subbin.surface_area
            D, T = load_and_process_bin_data(str(file_path), final_time)
            all_sub_bins_D += D
            all_sub_bins_T += T
    else:
        for mode in ["shadowed", "low_wetted", "high_wetted"]:
            file_path = results_dir / f"wall_bin_{i}_sub_bin_{mode}.json"
            # if mode == "shadowed":
            #     bin_surf_area = FW_bins.get_bin(i).shadowed_subbin.surface_area
            # elif mode == "low_wetted":
            #     bin_surf_area = FW_bins.get_bin(i).low_wetted_subbin.surface_area
            # else:
            #     bin_surf_area = FW_bins.get_bin(i).high_wetted_subbin.surface_area
            D, T = load_and_process_bin_data(str(file_path), final_time)
            all_sub_bins_D += D
            all_sub_bins_T += T

    if i in [9, 13, 14]:
        # dfw sub-bins
        file_path = results_dir / f"wall_bin_{i}_sub_bin_dfw.json"
        # if FW_bins.get_bin(i).shadowed_subbin.dfw:
        #     bin_surf_area = FW_bins.get_bin(i).shadowed_subbin.surface_area
        D, T = load_and_process_bin_data(str(file_path), final_time)
        all_sub_bins_D += D
        all_sub_bins_T += T

    # Calculate surface area and real inventory per length
    bin_surface_area = calculate_bin_surface_area(
        FW_bins.get_bin(i).start_point,
        FW_bins.get_bin(i).end_point,
        bin_length
    )
    
    # Real inventory per length: total_inventory * surface_area / length
    real_inventory_D = (all_sub_bins_D * bin_surface_area / bin_length) if bin_length > 0 else 0
    real_inventory_T = (all_sub_bins_T * bin_surface_area / bin_length) if bin_length > 0 else 0
    
    bin_dict_D[i] = [
        real_inventory_D,  # g/m
        FW_bins.get_bin(i).start_point,
        FW_bins.get_bin(i).end_point,
    ]
    bin_dict_T[i] = [
        real_inventory_T,  # g/m
        FW_bins.get_bin(i).start_point,
        FW_bins.get_bin(i).end_point,
    ]
    
    # Debug print
    print(f"  Bin {i}: D={all_sub_bins_D:.2e}, T={all_sub_bins_T:.2e}, length={bin_length:.3f}")
    print(f"  Surface area: {bin_surface_area:.3f} m²")
    print(f"  Real inventory: D={real_inventory_D:.2e} g/m, T={real_inventory_T:.2e} g/m")
    print(f"  Start: {FW_bins.get_bin(i).start_point}, End: {FW_bins.get_bin(i).end_point}")

# divertor bins
for i in range(18, 62):
    print(f'Loading Bin {i}.')
    current_bin = Div_bins.get_bin(i)
    file_path = results_dir / f"div_bin_{i}.json"
    bin_surface_area = calculate_bin_surface_area(
        current_bin.start_point,
        current_bin.end_point,
        current_bin.length,
    )
    bin_length = current_bin.length
    D, T = load_and_process_bin_data(str(file_path), final_time)

    # Real inventory per length: total_inventory * surface_area / length
    real_inventory_D = (D * bin_surface_area / bin_length) if bin_length > 0 else 0
    real_inventory_T = (T * bin_surface_area / bin_length) if bin_length > 0 else 0

    bin_dict_D[i] = [
        real_inventory_D,  # g/m
        current_bin.start_point,
        current_bin.end_point,
    ]
    bin_dict_T[i] = [
        real_inventory_T,  # g/m
        current_bin.start_point,
        current_bin.end_point,
    ]
    
    # Debug print
    print(f"  Bin {i}: D={D:.2e}, T={T:.2e}, length={bin_length:.3f}")
    print(f"  Surface area: {bin_surface_area:.3f} m²")
    print(f"  Real inventory: D={real_inventory_D:.2e} g/m, T={real_inventory_T:.2e} g/m")
    print(f"  Start: {current_bin.start_point}, End: {current_bin.end_point}")

# T inventory plot
print(f"\n=== PLOTTING SUMMARY ===")
print(f"Final time used: {final_time}")

# Check if we have any non-zero values
total_T_inventory = sum([values[0] for values in bin_dict_T.values()])
total_D_inventory = sum([values[0] for values in bin_dict_D.values()])
print(f"Total T inventory: {total_T_inventory:.2e}")
print(f"Total D inventory: {total_D_inventory:.2e}")

# Show min/max values for plotting
T_values = [values[0] for values in bin_dict_T.values() if values[0] > 0]
if T_values:
    min_T = min(T_values)
    max_T = max(T_values)
    print(f"T inventory range: {min_T:.2e} to {max_T:.2e}")
    # Use dynamic maximum, but ensure minimum is not too high
    vmax_dynamic = max_T * 1.1  # Add 10% buffer for better visualization
else:
    print("No positive T inventory values found!")
    vmax_dynamic = 15  # Fallback value if no positive values

norm = LogNorm(vmin=1e-6, vmax=vmax_dynamic)
cmap = plt.get_cmap("viridis")

for bin_idx, values in bin_dict_T.items():
    plt.plot(
        [values[1][0], values[2][0]],  # R coords (start, end)
        [values[1][1], values[2][1]],  # Z coords (start, end)
        c=cmap(norm(values[0])),
        linewidth=3,  # Make lines thicker for better visibility
    )

plt.colorbar(
    plt.cm.ScalarMappable(norm=norm, cmap=cmap),
    label="Tritium Inventory (g/m)",
    ax=plt.gca(),
)
plt.xlabel("R (m)")
plt.ylabel("Z (m)")
plt.gca().set_aspect("equal", adjustable="box")
plt.title(f"Tritium inventory at End of Do Nothing Scenario")

plt.savefig("iter_inv_last_point.svg", bbox_inches="tight", dpi=300)
plt.show()

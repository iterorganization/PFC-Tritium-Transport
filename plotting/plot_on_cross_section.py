from make_iter_bins import my_reactor, Div_bins, total_fw_bins, FW_bins
from matplotlib.colors import LogNorm
import matplotlib.pyplot as plt
import json
import numpy as np
import math

# Constants
AVOGADROS_CONST = 6.02214076e23
D_AMU = 2.01410177811  # Atomic mass unit for Deuterium
T_AMU = 3.0160492779  # Atomic mass unit for Tritium

# Import scenario
from iter_scenarios.do_nothing import scenario as scenario

final_time = (
    scenario.get_maximum_time() - 1
)  # last milestone is two seconds before end of waiting period


def calculate_bin_surface_area(bin_start_point, bin_end_point, bin_length):
    avg_r_coord = 0.5 * abs(bin_start_point[0] + bin_end_point[0])
    return 2 * math.pi * avg_r_coord * bin_length


def load_and_process_bin_data(file_path, final_time):
    with open(file_path, "r") as file:
        bin_data = json.load(file)

    sub_data_D = 0
    sub_data_T = 0

    for name, value in bin_data.items():
        if name in ["bin_index", "parent_bin_index", "mode"]:
            continue

        quantities_dict = value
        time = np.array(quantities_dict["t"])
        data = np.array(quantities_dict["data"])

        for idx, t in enumerate(time):
            if t == float(final_time):
                if "D" in name:
                    sub_data_D += data[idx] / AVOGADROS_CONST * D_AMU
                elif "T" in name:
                    sub_data_T += data[idx] / AVOGADROS_CONST * T_AMU

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
            file_path = f"results_do_nothing/wall_bin_{i}_sub_bin_{mode}.json"
            # if mode == "shadowed":
            #     bin_surf_area = FW_bins.get_bin(i).shadowed_subbin.surface_area
            # elif mode == "wetted":
            #     bin_surf_area = FW_bins.get_bin(i).wetted_subbin.surface_area
            D, T = load_and_process_bin_data(file_path, final_time)
            all_sub_bins_D += D
            all_sub_bins_T += T
    else:
        for mode in ["shadowed", "low_wetted", "high_wetted"]:
            file_path = f"results_do_nothing/wall_bin_{i}_sub_bin_{mode}.json"
            # if mode == "shadowed":
            #     bin_surf_area = FW_bins.get_bin(i).shadowed_subbin.surface_area
            # elif mode == "low_wetted":
            #     bin_surf_area = FW_bins.get_bin(i).low_wetted_subbin.surface_area
            # else:
            #     bin_surf_area = FW_bins.get_bin(i).high_wetted_subbin.surface_area
            D, T = load_and_process_bin_data(file_path, final_time)
            all_sub_bins_D += D
            all_sub_bins_T += T

    if i in [9, 13, 14]:
        # dfw sub-bins
        file_path = f"results_do_nothing/wall_bin_{i}_sub_bin_dfw.json"
        # if FW_bins.get_bin(i).shadowed_subbin.dfw:
        #     bin_surf_area = FW_bins.get_bin(i).shadowed_subbin.surface_area
        D, T = load_and_process_bin_data(file_path, final_time)
        all_sub_bins_D += D
        all_sub_bins_T += T

    # totals for this bin
    bin_dict_D[i] = [
        all_sub_bins_D * bin_length,
        FW_bins.get_bin(i).start_point,
        FW_bins.get_bin(i).end_point,
    ]
    bin_dict_T[i] = [
        all_sub_bins_T * bin_length,
        FW_bins.get_bin(i).start_point,
        FW_bins.get_bin(i).end_point,
    ]

# divertor bins
for i in range(18, 62):
    print(f'Loading Bin {i}.')
    current_bin = Div_bins.get_bin(i)
    file_path = f"results_do_nothing/div_bin_{i}.json"
    # bin_surf_area = calculate_bin_surface_area(
    #     current_bin.start_point,
    #     current_bin.end_point,
    #     current_bin.length,
    # )
    bin_length = current_bin.length
    D, T = load_and_process_bin_data(file_path, final_time)

    # totals for this bin
    bin_dict_D[i] = [
        D * bin_length,
        current_bin.start_point,
        current_bin.end_point,
    ]
    bin_dict_T[i] = [
        T * bin_length,
        current_bin.start_point,
        current_bin.end_point,
    ]

# T inventory plot
norm = LogNorm(vmin=1e-6, vmax=15)  # Adjust vmin as needed
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

import json
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from make_iter_bins import Div_bins, total_fw_bins, FW_bins
import math

# Constants
AVOGADROS_CONST = 6.02214076e23
D_AMU = 2.01410177811  # Atomic mass unit for Deuterium
T_AMU = 3.0160492779  # Atomic mass unit for Tritium


# Function to calculate bin surface area
def calculate_bin_surface_area(bin_start_point, bin_end_point, bin_length):
    avg_r_coord = 0.5 * abs(bin_start_point[0] + bin_end_point[0])
    return 2 * math.pi * avg_r_coord * bin_length


# Function to load and process bin data
def load_and_process_bin_data(file_path, bin_surf_area):
    with open(file_path, "r") as file:
        bin_data = json.load(file)

    time = None
    D_inventory = None
    T_inventory = None

    for name, value in bin_data.items():
        if name == "bin_index" or name == "parent_bin_index" or name == "mode":
            continue

        quantities_dict = value
        if time is None:
            time = np.array(quantities_dict["t"])
            D_inventory = np.zeros(len(time))
            T_inventory = np.zeros(len(time))

        data = np.array(quantities_dict["data"])
        if "D" in name and "flux" not in name:
            D_inventory += data
        elif "T" in name and "flux" not in name:
            T_inventory += data

    D_grams = D_inventory * bin_surf_area / AVOGADROS_CONST * D_AMU
    T_grams = T_inventory * bin_surf_area / AVOGADROS_CONST * T_AMU

    return time, D_grams, T_grams


# Initialize total inventories
total_time = None
total_D_grams = None
total_T_grams = None

# Process wall bins (0 to 17)
for i in range(18):
    if i == 16 or i == 17:
        for mode in ["shadowed", "wetted"]:
            file_path = f"results/wall_bin_{i}_sub_bin_{mode}.json"
            bin_surf_area = calculate_bin_surface_area(
                FW_bins.get_bin(i).start_point,
                FW_bins.get_bin(i).end_point,
                FW_bins.get_bin(i).length,
            )
            time, D_grams, T_grams = load_and_process_bin_data(file_path, bin_surf_area)

            if total_time is None:
                total_time = time
                total_D_grams = D_grams
                total_T_grams = T_grams
            else:
                total_D_grams += D_grams
                total_T_grams += T_grams
    else:
        for mode in ["shadowed", "low_wetted", "high_wetted"]:
            file_path = f"results/wall_bin_{i}_sub_bin_{mode}.json"
            bin_surf_area = calculate_bin_surface_area(
                FW_bins.get_bin(i).start_point,
                FW_bins.get_bin(i).end_point,
                FW_bins.get_bin(i).length,
            )
            time, D_grams, T_grams = load_and_process_bin_data(file_path, bin_surf_area)

            if total_time is None:
                total_time = time
                total_D_grams = D_grams
                total_T_grams = T_grams
            else:
                total_D_grams += D_grams
                total_T_grams += T_grams

# Process bottom bins (18 to 62)
list1 = list(range(18, 32))
list2 = list(range(34, 40))
list3 = list(range(44, 62))
for i in list1 + list2 + list3:
    current_bin = Div_bins.get_bin(i)
    if current_bin.material == "W":
        file_path = f"results/div_bin_{i}.json"
        bin_surf_area = calculate_bin_surface_area(
            Div_bins.get_bin(i).start_point,
            Div_bins.get_bin(i).end_point,
            Div_bins.get_bin(i).length,
        )
        time, D_grams, T_grams = load_and_process_bin_data(file_path, bin_surf_area)

        if total_time is None:
            total_time = time
            total_D_grams = D_grams
            total_T_grams = T_grams
        else:
            min_length = min(len(total_time), len(time))
            total_time = total_time[:min_length]
            total_D_grams = total_D_grams[:min_length] + D_grams[:min_length]
            total_T_grams = total_T_grams[:min_length] + T_grams[:min_length]

# Plotting with Plotly
fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=total_time / 3600,
        y=total_D_grams,
        name="Total D",
        line=dict(color="firebrick", width=2),
        stackgroup="one",
    )
)

fig.add_trace(
    go.Scatter(
        x=total_time / 3600,
        y=total_T_grams,
        name="Total T",
        line=dict(color="royalblue", width=2),
        stackgroup="one",
    )
)

fig.update_xaxes(title_text="Time (hrs)")
fig.update_yaxes(title_text="Total Quantity (g)")

fig.update_layout(title_text="Total Inventory for Div W Bins")

fig.write_html("total_inventory_plot.html", auto_open=True)

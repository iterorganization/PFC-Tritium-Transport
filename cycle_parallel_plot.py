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

# import scenarios
from iter_scenarios.do_nothing import scenario as scenario

# pull milestones for plotting
time_points = [0]

for pulse in scenario.pulses:
    for i in range(pulse.nb_pulses):
        time_points.append(time_points[-1] + pulse.total_duration)

D_inventory = np.zeros(len(time_points))
T_inventory = np.zeros(len(time_points))


# Function to calculate bin surface area
def calculate_bin_surface_area(bin_start_point, bin_end_point, bin_length):
    avg_r_coord = 0.5 * abs(bin_start_point[0] + bin_end_point[0])
    return 2 * math.pi * avg_r_coord * bin_length


# Function to load and process bin data
def load_and_process_bin_data(
    file_path, bin_surf_area, scenario_time, data_list_D, data_list_T
):
    with open(file_path, "r") as file:
        bin_data = json.load(file)

    for name, value in bin_data.items():
        if name == "bin_index" or name == "parent_bin_index" or name == "mode":
            continue

        quantities_dict = value
        time = np.array(quantities_dict["t"])
        data = np.array(quantities_dict["data"])

        for idx, t in enumerate(time):
            if t in np.array(scenario_time):
                time_idx = np.where(np.isclose(t, scenario_time))[0]
                if "D" in name:
                    data_list_D[time_idx] += (
                        data[idx] * bin_surf_area / AVOGADROS_CONST * D_AMU
                    )
                elif "T" in name:
                    data_list_T[time_idx] += (
                        data[idx] * bin_surf_area / AVOGADROS_CONST * T_AMU
                    )
            if t == float(1814400 - 1):  # write exception for the last point
                time_idx = -1
                if "D" in name:
                    data_list_D[time_idx] += (
                        data[idx] * bin_surf_area / AVOGADROS_CONST * D_AMU
                    )
                elif "T" in name:
                    data_list_T[time_idx] += (
                        data[idx] * bin_surf_area / AVOGADROS_CONST * T_AMU
                    )

    return data_list_D, data_list_T


# Process wall bins (0 to 17)
for i in range(18):
    if i in [13, 14, 16, 17]:
        for mode in ["shadowed", "wetted"]:
            file_path = f"results/wall_bin_{i}_sub_bin_{mode}.json"
            bin_surf_area = calculate_bin_surface_area(
                FW_bins.get_bin(i).start_point,
                FW_bins.get_bin(i).end_point,
                FW_bins.get_bin(i).length,
            )
            D_inventory, T_inventory = load_and_process_bin_data(
                file_path, bin_surf_area, time_points, D_inventory, T_inventory
            )
    elif i in [9, 13, 14]:
        file_path = f"results/wall_bin_{i}_sub_bin_dfw.json"
        bin_surf_area = calculate_bin_surface_area(
            FW_bins.get_bin(i).start_point,
            FW_bins.get_bin(i).end_point,
            FW_bins.get_bin(i).length,
        )
        D_inventory, T_inventory = load_and_process_bin_data(
            file_path, bin_surf_area, time_points, D_inventory, T_inventory
        )
    else:
        for mode in ["shadowed", "low_wetted", "high_wetted"]:
            file_path = f"results/wall_bin_{i}_sub_bin_{mode}.json"
            bin_surf_area = calculate_bin_surface_area(
                FW_bins.get_bin(i).start_point,
                FW_bins.get_bin(i).end_point,
                FW_bins.get_bin(i).length,
            )
            D_inventory, T_inventory = load_and_process_bin_data(
                file_path, bin_surf_area, time_points, D_inventory, T_inventory
            )

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
        D_inventory, T_inventory = load_and_process_bin_data(
            file_path, bin_surf_area, time_points, D_inventory, T_inventory
        )

# Plotting with Plotly
fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=time_points,
        y=D_inventory,
        name="Total D",
        line=dict(color="firebrick", width=2),
        stackgroup="one",
    )
)

fig.add_trace(
    go.Scatter(
        x=time_points,
        y=T_inventory,
        name="Total T",
        line=dict(color="royalblue", width=2),
        stackgroup="one",
    )
)

fig.update_xaxes(title_text="Time (hrs)")
fig.update_yaxes(title_text="Total Quantity (g)")

fig.update_layout(title_text="Total Inventory for Div W Bins")

fig.write_html("total_inventory_plot.html", auto_open=True)

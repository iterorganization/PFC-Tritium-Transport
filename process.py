# post-process inventory bar graphs
import json
import numpy as np
from make_iter_bins import Div_bins, total_fw_bins, FW_bins
import math
###### THIS FILE CREATES PLOT-READY DATA FILES FROM SIMULATION RESULTS DATA ######
## There are a few things that need to be adjusted depending on which scenario you want to look at:
# System path directory on line 17
# Scenario that you’d like to import and plot on line 18
# Output plot-ready-data file names based on the scenario you’re using on lines 200 and 202
## Then you’re good to go!
# import scenarios

# from iter_scenarios.capability_test import scenario as scenario
from iter_scenarios.just_glow import scenario as scenario
# from iter_scenarios.do_nothing import scenario as scenario

# folder = "results_do_nothing"
folder = "results_just_glow"
# folder = "results_capability_test"
# pull milestones at end of each pulse type for plotting
time_points = [0]
for pulse in scenario.pulses:
    time_points.append(
        time_points[-1] + pulse.total_duration * pulse.nb_pulses
    )  # end of each pulse type
time_points = time_points[1:]
print([p for p in scenario.pulses], time_points)


def calculate_bin_surface_area(bin_start_point, bin_end_point, bin_length):
    avg_r_coord = 0.5 * abs(bin_start_point[0] + bin_end_point[0])
    return 2 * math.pi * avg_r_coord * bin_length


# func to calculate bin surface area
D_inventory = {}
T_inventory = {}


# Function to load, process, and plot bin data for each bin
def load_and_process_bin_data(
    file_path, scenario_time, material, sub_dict_D, sub_dict_T, bin_surf_area=None
):
    print(f"Loading data from {file_path}")
    with open(file_path, "r") as file:
        bin_data = json.load(file)
    print("File loaded.")
    data_list_D = np.zeros(len(time_points))
    data_list_T = np.zeros(len(time_points))
    if i in range(18):
        unit_factor = 1
    else:
        unit_factor = bin_surf_area  # putting in atms/m for divertor

    for name, value in bin_data.items():
        if name == "bin_index" or name == "parent_bin_index" or name == "mode":
            if name == "bin_index" or name == "parent_bin_index":
                bin_idx = value
            elif name == "mode":
                mode = value
            continue
        quantities_dict = value
        time = np.array(quantities_dict["t"])
        data = np.array(quantities_dict["data"])

        for time_id, time_of_interest in enumerate(scenario_time):
            idx = np.where(np.isclose(time, time_of_interest, atol=10, rtol=0))[0][0]
            print(idx, data[idx])
            assert time[idx] <= time_of_interest, (
                "Time in data exceeds time of interest"
            )
            if "D" in name:
                data_list_D[time_id] += data[idx] * unit_factor
            elif "T" in name:
                data_list_T[time_id] += data[idx] * unit_factor

    if i in range(18):
        print(i)
        sub_dict_D[mode] = data_list_D.tolist()
        sub_dict_T[mode] = data_list_T.tolist()
    else:
        print(i)
        sub_dict_D["Div"] = data_list_D.tolist()
        sub_dict_T["Div"] = data_list_T.tolist()
    return sub_dict_D, sub_dict_T


# Process wall bins (0 to 17)
for i in range(18):
    sub_dict_D = {}
    sub_dict_T = {}
    if i in [13, 14, 16, 17]:
        for mode in ["shadowed", "wetted"]:
            print(f"Processing wall bin {i}, mode {mode}")
            file_path = f"{folder}/wall_bin_{i}_sub_bin_{mode}.json"
            if mode == "shadowed":
                material = FW_bins.get_bin(i).shadowed_subbin.material
            elif mode == "wetted":
                material = FW_bins.get_bin(i).wetted_subbin.material
            sub_dict_D, sub_dict_T = load_and_process_bin_data(
                file_path, time_points, material, sub_dict_D, sub_dict_T
            )
    else:
        for mode in ["shadowed", "low_wetted", "high_wetted"]:
            print(f"Processing wall bin {i}, mode {mode}")
            file_path = f"{folder}/wall_bin_{i}_sub_bin_{mode}.json"
            if mode == "shadowed":
                material = FW_bins.get_bin(i).shadowed_subbin.material
            elif mode == "low_wetted":
                material = FW_bins.get_bin(i).low_wetted_subbin.material
            else:
                material = FW_bins.get_bin(i).high_wetted_subbin.material
            sub_dict_D, sub_dict_T = load_and_process_bin_data(
                file_path, time_points, material, sub_dict_D, sub_dict_T
            )
    if i in [9, 13, 14]:
        print(f"Processing wall bin {i}, mode DFW")
        file_path = f"{folder}/wall_bin_{i}_sub_bin_dfw.json"
        material = "DFW"
        sub_dict_D, sub_dict_T = load_and_process_bin_data(
            file_path, time_points, material, sub_dict_D, sub_dict_T
        )
    D_inventory[i] = sub_dict_D
    T_inventory[i] = sub_dict_T
# process div bins
for i in range(18, 62):
    sub_dict_D = {}
    sub_dict_T = {}
    current_bin = Div_bins.get_bin(i)
    file_path = f"{folder}/div_bin_{i}.json"
    bin_surf_area = calculate_bin_surface_area(
        current_bin.start_point,
        current_bin.end_point,
        current_bin.length,
    )
    material = current_bin.material
    sub_dict_D, sub_dict_T = load_and_process_bin_data(
        file_path,
        time_points,
        material,
        sub_dict_D,
        sub_dict_T,
        bin_surf_area=bin_surf_area,
    )
    D_inventory[i] = sub_dict_D
    T_inventory[i] = sub_dict_T
# save data
with open(f"{folder}_D_data.json", "w") as file:
    json.dump(D_inventory, file)
with open(f"{folder}_T_data.json", "w") as file:
    json.dump(T_inventory, file)

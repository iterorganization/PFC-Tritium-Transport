import json
import numpy as np
from make_iter_bins import Div_bins, FW_bins
import math

# Constants
AVOGADROS_CONST = 6.02214076e23
D_AMU = 2.01410177811  # Atomic mass unit for Deuterium
T_AMU = 3.0160492779  # Atomic mass unit for Tritium

###### THIS FILE CREATES PLOT-READY DATA FILES FROM SIMULATION RESULTS DATA FOR ONLY TOTAL INVENTORY PLOTTING ######
## There are a few things that need to be adjusted depending on which scenario you want to look at:
# System path directory on line 20
# Scenario that you'd like to import and plot on line 21 
# Output plot-ready-data file names based on the scenario you're using on lines 215 and 216
## Then you're good to go!

# import scenarios
import sys
sys.path.insert(0, '/home/ITER/dunnelk/PFC-tritium-transport/scenarios')
from do_nothing import scenario as scenario


# pull milestones for plotting
time_points = [0]

for pulse in scenario.pulses:
    if pulse.pulse_type == "GDC" or pulse.pulse_type == "ICWC":
        for i in range(pulse.nb_pulses):
            time_points.append(time_points[-1] + pulse.duration_no_waiting)
            time_points.append(time_points[-1] + pulse.waiting)
    else:
        for i in range(pulse.nb_pulses):
            time_points.append(time_points[-1] + pulse.ramp_up) # end of ramp up
            time_points.append(time_points[-1] + pulse.steady_state) # start of ramp down 
            time_points.append(time_points[-1] + pulse.ramp_down) # end of ramp down 
            # time_points.append(time_points[-1] + pulse.duration_no_waiting)
            time_points.append(time_points[-1] + pulse.waiting)

D_inventory = np.zeros(len(time_points))
T_inventory = np.zeros(len(time_points))

# Function to calculate bin surface area
def calculate_bin_surface_area(bin_start_point, bin_end_point, bin_length):
    avg_r_coord = 0.5 * abs(bin_start_point[0] + bin_end_point[0])
    return 2 * math.pi * avg_r_coord * bin_length


# Function to load and process bin data
def load_and_process_bin_data(
    file_path, bin_surf_area, scenario_time, data_list_D, data_list_T, material
):
    with open(file_path, "r") as file:
        bin_data = json.load(file)

    for name, value in bin_data.items():
        if name == "bin_index" or name == "parent_bin_index" or name == "mode":
            continue

        quantities_dict = value
        time = np.array(quantities_dict["t"])
        data = np.array(quantities_dict["data"])
        processed_times = []
        for idx, t in enumerate(time):
            if t in scenario_time:
                processed_times.append(t)
                # print(t)
                time_idx = np.where(t == scenario_time)[0]
                if "D" in name:
                    data_list_D[time_idx] += (
                        data[idx] * bin_surf_area / AVOGADROS_CONST * D_AMU
                    )
                elif "T" in name:
                    data_list_T[time_idx] += (
                        data[idx] * bin_surf_area / AVOGADROS_CONST * T_AMU
                    )
            else:
                if material == "W" or material == "DFW":
                    if np.any(np.isclose(t, np.array(processed_times), atol=0.01, rtol=0)):
                        continue
                    else:
                        if np.any(np.isclose(t, np.array(scenario_time), atol=0.01, rtol=0)):
                            processed_times.append(t)
                            time_idx = np.where(np.isclose(t, scenario_time, rtol=0, atol=1e-2))[0]
                            if "D" in name:
                                data_list_D[time_idx] += (
                                    data[idx] * bin_surf_area / AVOGADROS_CONST * D_AMU
                                )
                            elif "T" in name:
                                data_list_T[time_idx] += (
                                    data[idx] * bin_surf_area / AVOGADROS_CONST * T_AMU
                                )
                elif material == "B":
                    if np.any(np.isclose(t, np.array(processed_times), atol=1e-5, rtol=0)):
                        continue
                    else:
                        if np.any(np.isclose(t, np.array(scenario_time), rtol=0, atol=1e-4)):
                            processed_times.append(t)
                            # print(t)
                            time_idx = np.where(np.isclose(t, scenario_time, rtol=0, atol=1e-5))[0]
                            if "D" in name:
                                data_list_D[time_idx] += (
                                    data[idx] * bin_surf_area / AVOGADROS_CONST * D_AMU
                                )
                            elif "T" in name:
                                data_list_T[time_idx] += (
                                    data[idx] * bin_surf_area / AVOGADROS_CONST * T_AMU
                                )
            if t == float(scenario.get_maximum_time() - 1):  # write exception for the last point
                time_idx = -1
                if "D" in name:
                    data_list_D[time_idx] += (
                        data[idx] * bin_surf_area / AVOGADROS_CONST * D_AMU
                    )
                elif "T" in name:
                    data_list_T[time_idx] += (
                        data[idx] * bin_surf_area / AVOGADROS_CONST * T_AMU
                    )

        unmatched_scenario_indices = [i for i, st in enumerate(scenario_time) if not np.any(np.isclose(st, processed_times, atol=0.01, rtol=0))]

        for idx, t in enumerate(time):
            if material == "B":
                if np.any(np.isclose(t, np.array(processed_times), atol=1e-5, rtol=0)):
                    continue

                for st_idx in unmatched_scenario_indices:
                    if np.isclose(t, scenario_time[st_idx], atol=5e-3, rtol=0):
                        processed_times.append(t)
                        # print(t)
                        if "D" in name:
                            data_list_D[st_idx] += (
                                data[idx] * bin_surf_area / AVOGADROS_CONST * D_AMU
                            )
                        elif "T" in name:
                            data_list_T[st_idx] += (
                                data[idx] * bin_surf_area / AVOGADROS_CONST * T_AMU
                            )
                        break  # Move to next 't' after first match
            else:
                if np.any(np.isclose(t, np.array(processed_times), atol=0.01, rtol=0)):
                    continue
            
                # check if this 't' matches any unmatched scenario_time with looser tolerance
                for st_idx in unmatched_scenario_indices:
                    if np.isclose(t, scenario_time[st_idx], atol=0.05, rtol=0):
                        processed_times.append(t)
                        if "D" in name:
                            data_list_D[st_idx] += (
                                data[idx] * bin_surf_area / AVOGADROS_CONST * D_AMU
                            )
                        elif "T" in name:
                            data_list_T[st_idx] += (
                                data[idx] * bin_surf_area / AVOGADROS_CONST * T_AMU
                            )
                        break  # Move to next 't' after first match
    # print(processed_times)
    return data_list_D, data_list_T


# Process wall bins (0 to 17)
for i in range(18):
    if i in [13, 14, 16, 17]:
        for mode in ["shadowed", "wetted"]:
            file_path = f"results_do_nothing/wall_bin_{i}_sub_bin_{mode}.json"
            if mode == "shadowed":
                bin_surf_area = FW_bins.get_bin(i).shadowed_subbin.surface_area
                material = FW_bins.get_bin(i).shadowed_subbin.material
            elif mode == "wetted":
                bin_surf_area = FW_bins.get_bin(i).wetted_subbin.surface_area
                material = FW_bins.get_bin(i).wetted_subbin.material
            D_inventory, T_inventory = load_and_process_bin_data(
                file_path, bin_surf_area, time_points, D_inventory, T_inventory, material
            )
    elif i in [9, 13, 14]:
        file_path = f"results_do_nothing/wall_bin_{i}_sub_bin_dfw.json"
        if FW_bins.get_bin(i).shadowed_subbin.dfw:
            bin_surf_area = FW_bins.get_bin(i).shadowed_subbin.surface_area
        material = "DFW"
        D_inventory, T_inventory = load_and_process_bin_data(
            file_path, bin_surf_area, time_points, D_inventory, T_inventory, material
        )
    else:
        for mode in ["shadowed", "low_wetted", "high_wetted"]:
            file_path = f"results_do_nothing/wall_bin_{i}_sub_bin_{mode}.json"
            if mode == "shadowed":
                bin_surf_area = FW_bins.get_bin(i).shadowed_subbin.surface_area
                material = FW_bins.get_bin(i).shadowed_subbin.material
            elif mode == "low_wetted":
                bin_surf_area = FW_bins.get_bin(i).low_wetted_subbin.surface_area
                material = FW_bins.get_bin(i).low_wetted_subbin.material
            else:
                bin_surf_area = FW_bins.get_bin(i).high_wetted_subbin.surface_area
                material = FW_bins.get_bin(i).high_wetted_subbin.material
            D_inventory, T_inventory = load_and_process_bin_data(
                file_path, bin_surf_area, time_points, D_inventory, T_inventory, material
            )


# process div bins
for i in range(18,62):
    current_bin = Div_bins.get_bin(i)
    file_path = f"results_do_nothing/div_bin_{i}.json"
    bin_surf_area = calculate_bin_surface_area(
        Div_bins.get_bin(i).start_point,
        Div_bins.get_bin(i).end_point,
        Div_bins.get_bin(i).length,
    )
    material = Div_bins.get_bin(i).material
    D_inventory, T_inventory = load_and_process_bin_data(
        file_path, bin_surf_area, time_points, D_inventory, T_inventory, material
    )

# save data in case plotting go awry
np.savetxt("plot_total_d_donothing", D_inventory)
np.savetxt("plot_total_t_donothing", T_inventory)
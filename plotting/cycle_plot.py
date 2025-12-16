# post-process cycle comparison script
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import os
import math
import pandas as pd
from make_iter_bins import Div_bins, total_nb_bins, total_fw_bins, FW_bins
import math

from scenarios.do_nothing import scenario as scenario_do_nothing
from scenarios.benchmark import scenario as scenario_benchmark
from scenarios.clean_every_2_days import scenario as scenario_clean_every_2
from scenarios.clean_every_5_days import scenario as scenario_clean_every_5
from scenarios.no_glow import scenario as scenario_no_glow

T_AMU = 3.016049 # g/mol
D_AMU = 2.014102 # g/mol
AVOGADROS_CONST = 6.0221408e+23 # atms/mol

# FIXME: improve and shorten code 
time_do_nothing = [0]
time_benchmark = [0]
time_no_glow = [0]
time_every_2 = [0]
time_every_5 = [0]

for pulse in scenario_do_nothing.pulses:
    for i in range(pulse.nb_pulses):
        time_do_nothing.append(time_do_nothing[-1] + pulse.total_duration)

for pulse in scenario_benchmark.pulses:
    for i in range(pulse.nb_pulses):
        time_benchmark.append(time_benchmark[-1] + pulse.total_duration)

for pulse in scenario_clean_every_2.pulses:
    for i in range(pulse.nb_pulses):
        time_every_2.append(time_every_2[-1] + pulse.total_duration)

for pulse in scenario_no_glow.pulses:
    for i in range(pulse.nb_pulses):
        time_no_glow.append(time_no_glow[-1] + pulse.total_duration)

for pulse in scenario_clean_every_5.pulses:
    for i in range(pulse.nb_pulses):
        time_every_5.append(time_every_5[-1] + pulse.total_duration)

bench_total_D = np.zeros(len(time_benchmark))
bench_ng_total_D = np.zeros(len(time_no_glow))
every_2_total_D = np.zeros(len(time_every_2))
every_5_total_D = np.zeros(len(time_every_5))
do_nothing_total_D = np.zeros(len(time_do_nothing))

bench_total_T = np.zeros(len(time_benchmark))
bench_ng_total_T = np.zeros(len(time_no_glow))
every_2_total_T = np.zeros(len(time_every_2))
every_5_total_T = np.zeros(len(time_every_5))
do_nothing_total_T = np.zeros(len(time_do_nothing))

def get_bin_data(data: list, bin_index: int) -> dict:
    """Returns the right dictionary for a given bin index

    Args:
        data (list): the list of dictionaries
        bin_index (int): the bin index
    """

    for i in data:
        if i["bin_index"] == bin_index:
            return i


def make_plot_lists(scenario_data, scenario_time, data_list_D, data_list_T):
    """Generates lists of inventories at scenario milestones for 
    scenario comparison plotting.

    Args:
        scenario_data (str): Name of scenario for .json file
        scenario_time (list): List of milestone times in seconds
        data_list_D (list): Empty D list sized to corresponding scenario time list
        data_list_T (list): Empty T list sized to corresponding scenario time list

    Returns:
        data_list_D: Filled list of inventory in atms at each milestone for Deuterium
        data_list_T: Filled list of inventory in atms at each milestone for Tritium
    """
    
    # open results file
    with open('results_'+scenario_data+'.json', 'r') as file:
        dict_data = json.load(file)

    # fw bins
    for bin_index in range(total_fw_bins):
        fw_bin = FW_bins.get_bin(bin_index)
        avg_r_coord = 0.5*abs(fw_bin.start_point[0]+fw_bin.end_point[0])
        bin_surf_area = 2*math.pi*avg_r_coord*fw_bin.length

        bin_data = get_bin_data(dict_data, bin_index=bin_index)
        for sub_bin in bin_data["sub_bins"]: # means that we are now in sub_bin list 
            for name, quantities_dict in sub_bin.items(): # one dictionary per species (e.g. D, T, trap1_D, etc.)
                    if name in ["mode", "parent_bin_index"]:
                        continue  # skip these keys
        
                    data = np.array(quantities_dict['data'])
                    time_points = np.array(quantities_dict['t'])

                    for idx, time in enumerate(time_points):
                        if time in np.array(scenario_time): # ADJUST
                            time_idx = np.where(np.isclose(time, scenario_time))[0]
                            if "D" in name:
                                data_list_D[time_idx] += data[idx] #* bin_surf_area * / AVOGADROS_CONST * D_AMU
                            if "T" in name: 
                                data_list_T[time_idx] += data[idx] #* bin_surf_area / AVOGADROS_CONST * T_AMU
                        if time == float(1188000-1): # write exception for the last point
                            time_idx = -1
                            if "D" in name:
                                data_list_D[time_idx] += data[idx] #* bin_surf_area / AVOGADROS_CONST * D_AMU
                            if "T" in name: 
                                data_list_T[time_idx] += data[idx] #* bin_surf_area / AVOGADROS_CONST * T_AMU

    for bin_index in range(total_fw_bins,total_nb_bins):
        div_bin = Div_bins.get_bin(bin_index)
        avg_r_coord = 0.5*abs(div_bin.start_point[0]+div_bin.end_point[0])
        bin_surf_area = 2*math.pi*avg_r_coord*div_bin.length

        bin_data = get_bin_data(dict_data, bin_index=bin_index)

        for name, quantities_dict in bin_data.items():
            if name in ["bin_index"]:
                continue  # skip this key

            data = np.array(quantities_dict['data'])
            time_points = np.array(quantities_dict['t'])

            for idx, time in enumerate(time_points):
                if time in np.array(scenario_time): # BENCHMARK SCEN
                    time_idx = np.where(np.isclose(time, scenario_time))[0]
                    if "D" in name:
                        data_list_D[time_idx] += data[idx] #* bin_surf_area / AVOGADROS_CONST * D_AMU
                    if "T" in name: 
                        data_list_T[time_idx] += data[idx] #* bin_surf_area / AVOGADROS_CONST * T_AMU
                if time == float(1188000-1): # write exception for the last point
                            time_idx = -1
                            if "D" in name:
                                data_list_D[time_idx] += data[idx] #* bin_surf_area / AVOGADROS_CONST * D_AMU
                            if "T" in name: 
                                data_list_T[time_idx] += data[idx] #* bin_surf_area / AVOGADROS_CONST * T_AMU

    return data_list_D, data_list_T

bench_total_D, bench_total_T = make_plot_lists('benchmark', time_benchmark, bench_total_D, bench_total_T)
bench_ng_total_D, bench_ng_total_T = make_plot_lists('no_glow',time_no_glow, bench_ng_total_D, bench_ng_total_T)
do_nothing_total_D, do_nothing_total_T = make_plot_lists('do_nothing', time_do_nothing, do_nothing_total_D,do_nothing_total_T)
every_5_total_D, every_5_total_T = make_plot_lists('clean_every_5_days', time_every_5, every_5_total_D, every_5_total_T)
every_2_total_D, every_2_total_T = make_plot_lists('clean_every_2_days', time_every_2, every_2_total_D, every_2_total_T)

# -------- PLOTTING -------- 

plt.figure() # D figure
plt.plot(time_do_nothing, do_nothing_total_D, label="Do Nothing")
plt.plot(time_benchmark, bench_total_D, label="Benchmark")
plt.plot(time_no_glow, bench_ng_total_D, label="Benchmark No Glow")
plt.plot(time_every_5, every_5_total_D, label="Clean Every 5")
plt.plot(time_every_2, every_2_total_D, label="Clean Every 2")
plt.legend()
plt.title("Two Week Cycle Scenarios: Deuterium")
plt.ylabel("Total Quantity (atms/m^2)")
plt.xlabel("Time (seconds)")
plt.show()


plt.figure() # T figure
plt.plot(time_do_nothing, do_nothing_total_T, label="Do Nothing")
plt.plot(time_benchmark, bench_total_T, label="Benchmark")
plt.plot(time_no_glow, bench_ng_total_T, label="Benchmark No Glow")
plt.plot(time_every_5, every_5_total_T, label="Clean Every 5")
plt.plot(time_every_2, every_2_total_T, label="Clean Every 2")
plt.legend()
plt.title("Two Week Cycle Scenarios: Tritium")
plt.ylabel("Total Quantity (atms/m^2)")
plt.xlabel("Time (seconds)")
plt.show()

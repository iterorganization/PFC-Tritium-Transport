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


time_do_nothing = [0,86400, 172800, 259200,345600,432000,518400,604800,691200,777600,1209599]
time_bench = [0,86400, 172800, 259200,345600,432000,518400,604800,691200,777600,864000,871300,873100,874900,876700,878500,880300,950500,957800,959600,961400,963200,965000,966800,1037000,1188199]
time_every_2 = [0,86400, 172800,174600,176400,178200,208800,259200,266400,268200,270000,271800,345600,432000,518400,520200,522000,523800,554400,604800,612000,613800,615600,617400,691200,777600,864000,865800,867600,869400,871200,873000,874800,950400,1101600]
time_every_5 = [0,86400, 172800, 259200,345600,432000,433800,435600,437400,439200,441000,442800,518400,604800,691200,777600,864000,950400,952200,954000,955800,957600,959400,961200,1036800,1188000]
time_bench_ng = [0,86400, 172800, 259200,345600,432000,518400,604800,691200,777600,864000,871300,873100,874900,876700,878500,880300,950500,957800,959600,961400,963200,965000,966800,1209799]


bench_total_D = np.zeros(len(time_bench))
bench_ng_total_D = np.zeros(len(time_bench_ng))
every_2_total_D = np.zeros(len(time_every_2))
every_5_total_D = np.zeros(len(time_every_5))
do_nothing_total_D = np.zeros(len(time_do_nothing))

bench_total_T = np.zeros(len(time_bench))
bench_ng_total_T = np.zeros(len(time_bench_ng))
every_2_total_T = np.zeros(len(time_every_2))
every_5_total_T = np.zeros(len(time_every_5))
do_nothing_total_T = np.zeros(len(time_do_nothing))

def make_plot_lists(scenario_data, data_list_D, data_list_T):
    # open results file
    with open(scenario_data+'.json', 'r') as file:
        dict_data = json.load(file)

    # fw bins
    for bin_index in range(total_fw_bins):
        fw_bin = FW_bins.get_bin(bin_index)
        avg_r_coord = 0.5*abs(fw_bin.start_point[0]+fw_bin.end_point[0])
        bin_surf_area = 2*math.pi*avg_r_coord*fw_bin.length

        # fw_bin_data = {"bin_index": fw_bin.index, "sub_bins": []}
        bin_data = dict_data[bin_index]
        for name, quantities_dict in bin_data.items(): # iterates through bin_index and sub_bins, which is a list of dictionaries
            for sub_bin in bin_data["sub_bins"]: # means that we are now in sub_bin list 
                for name, quantities_dict in sub_bin.items():
                        if name in ["mode", "parent_bin_index"]:
                            continue  # skip these keys
            
                        data = np.array(quantities_dict['data'])
                        time_points = np.array(quantities_dict['t'])

                        for idx, time in enumerate(time_points):
                            if time in np.array(time_bench): # BENCHMARK SCEN
                                time_idx = time_bench.index(time)
                                if "D" in name:
                                    data_list_D[time_idx] += data[idx] * bin_surf_area
                                if "T" in name: 
                                    data_list_T[time_idx] += data[idx] * bin_surf_area
                    


    for bin_index in range(total_fw_bins,total_nb_bins):
        div_bin = Div_bins.get_bin(bin_index)
        avg_r_coord = 0.5*abs(div_bin.start_point[0]+div_bin.end_point[0])
        bin_surf_area = 2*math.pi*avg_r_coord*div_bin.length

        bin_data = dict_data[bin_index]

        for name, quantities_dict in bin_data.items():
            if name in ["bin_index"]:
                continue  # skip this key

            data = np.array(quantities_dict['data'])
            time_points = np.array(quantities_dict['t'])

            for idx, time in enumerate(time_points):
                if time in np.array(time_bench): # BENCHMARK SCEN
                    time_idx = time_bench.index(time)
                    if "D" in name:
                        data_list_D[time_idx] += data[idx] * bin_surf_area
                    if "T" in name: 
                        data_list_T[time_idx] += data[idx] * bin_surf_area

            return data_list_D, data_list_T

bench_total_D, bench_total_T = make_plot_lists('benchmark_scenario', bench_total_D, bench_total_T)
bench_ng_total_D, bench_ng_total_T = make_plot_lists('benchmark_no_glow_scenario',bench_ng_total_D, bench_ng_total_T)
do_nothing_total_D, do_nothing_total_T = make_plot_lists('do_nothing_scenario', do_nothing_total_D,do_nothing_total_T)
every_5_total_D, every_5_total_T = make_plot_lists('clean_every_5_scenario', every_5_total_D, every_5_total_T)
every_2_total_D, every_2_total_T = make_plot_lists('clean_every_2_scenario', every_2_total_D, every_2_total_T)

print(bench_total_D)
print(bench_ng_total_D)
print(do_nothing_total_D)
print(every_2_total_D)
print(every_5_total_D)

print(bench_total_T)
print(bench_ng_total_T)
print(do_nothing_total_T)
print(every_2_total_T)
print(every_5_total_T)

# def cycle_plot(cycle_data_d, cycle_data_t, with_clean=False):
#     """
#     plots total tokamak inventory over time for different
#     cycles and cleaning scenarios

#     parameters: 
#         .txt files produced by load_cycle_data for d and t
#     """
#     # ALL INV PLOTTING

#     # open and read .txt files
#     with open(cycle_data_d) as file: 
#         lines = [line for line in file if not line.startswith('#')]

#     datad = np.loadtxt(lines, skiprows=1)

#     with open(cycle_data_t) as file: 
#         lines = [line for line in file if not line.startswith('#')]

#     datat = np.loadtxt(lines, skiprows=1)

#     bench_plot_D = datad[:16,0]
#     scenA_plot_D = datad[:14,1]
#     scenC_plot_D = datad[:16,2]
#     scenD_plot_D = datad[:16,3]
#     scenE_plot_D = datad[:,4]

#     bench_plot_T = datat[:16,0]
#     scenA_plot_T = datat[:14,1]
#     scenC_plot_T = datat[:16,2]
#     scenD_plot_T = datat[:16,3]
#     scenE_plot_T = datat[:,4]

#     time_plot = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]
#     time_bench = [0,1,2,3,4,5,6,7,8,9,10,11,11.083,12,12.083,13,14]
#     time_every_2 = [0,1,2,3,3.0625,3.416,4,4.145,5,6,7,7.0625,7.416,8,8.145,9,10,11,11.083,12,13,14]
#     time_every_5 = [0,1,2,3,4,5,6,6.125,7,8,9,10,11,12,12.125,13,14]
#     time_bench_ng = [0,1,2,3,4,5,6,7,8,9,10,11,11.083,12,12.083,13,14]

#     bench_plot_D = [0] + bench_plot_D.tolist()
#     bench_plot_T = [0] + bench_plot_T.tolist()
#     scenA_plot_D = [0] + scenA_plot_D.tolist()
#     scenC_plot_D = [0] + scenC_plot_D.tolist()
#     scenD_plot_D = [0] + scenD_plot_D.tolist()
#     scenE_plot_D = [0] + scenE_plot_D.tolist()
#     scenA_plot_T = [0] + scenA_plot_T.tolist()
#     scenC_plot_T = [0] + scenC_plot_T.tolist()
#     scenD_plot_T = [0] + scenD_plot_T.tolist()
#     scenE_plot_T = [0] + scenE_plot_T.tolist()

#     # convert inventories to grams 
#     # D conversion 
#     bench_plot_D_g = np.array(bench_plot_D)/(6.022e23)*2.0141
#     scenA_plot_D_g = np.array(scenA_plot_D)/(6.022e23)*2.0141
#     scenC_plot_D_g = np.array(scenC_plot_D)/(6.022e23)*2.0141
#     scenD_plot_D_g = np.array(scenD_plot_D)/(6.022e23)*2.0141
#     scenE_plot_D_g = np.array(scenE_plot_D)/(6.022e23)*2.0141

#     # T conversion 
#     bench_plot_T_g = np.array(bench_plot_T)/(6.022e23)*3.016
#     scenA_plot_T_g = np.array(scenA_plot_T)/(6.022e23)*3.016
#     scenC_plot_T_g = np.array(scenC_plot_T)/(6.022e23)*3.016
#     scenD_plot_T_g = np.array(scenD_plot_T)/(6.022e23)*3.016
#     scenE_plot_T_g = np.array(scenE_plot_T)/(6.022e23)*3.016

#     # D plotting
#     fig, ax = plt.subplots(1, 1, figsize=(12, 6))

#     if with_clean:
#         ax.plot(time_bench, bench_plot_D_g, label="Benchmark", marker='o')
#         ax.plot(time_plot, scenA_plot_D_g, label="Do Nothing", marker='o')
#         ax.plot(time_bench_ng, scenC_plot_D_g, label="Benchmark w/o Glow", marker='o')
#         ax.plot(time_every_5, scenD_plot_D_g, label="Every 5", marker='o')
#         ax.plot(time_every_2, scenE_plot_D_g, label="Every 2", marker='o')
#     else:
#         ax.plot(time_plot, bench_plot_D_g, label="Benchmark")
#         ax.plot(time_plot, scenA_plot_D_g, label="Do Nothing")
#         ax.plot(time_plot, scenC_plot_D_g, label="Benchmark w/o Glow")
#         ax.plot(time_plot, scenD_plot_D_g, label="Every 5")
#         ax.plot(time_plot, scenE_plot_D_g, label="Every 2")
#     plt.ylim(ymin=0.0)

#     plt.legend()
#     plt.grid(True)
#     ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
#     ax.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
#     plt.xticks(time_plot[1:])
#     plt.xlabel('Day', fontsize=14)
#     plt.ylabel('Concentration (g)', fontsize=14)
#     plt.title(f'Two Week Cycle Scenarios: Deuterium', fontsize=16)
    
#     plt.savefig('D_total_inv.png')

#     # T plotting
#     fig.clear()
#     fig, ax = plt.subplots(1, 1, figsize=(12, 6))

#     if with_clean:
#         ax.plot(time_bench, bench_plot_T_g, label="Benchmark", marker='o')
#         ax.plot(time_plot, scenA_plot_T_g, label="Do Nothing", marker='o')
#         ax.plot(time_bench_ng, scenC_plot_T_g, label="Benchmark w/o Glow", marker='o')
#         ax.plot(time_every_5, scenD_plot_T_g, label="Every 5", marker='o')
#         ax.plot(time_every_2, scenE_plot_T_g, label="Every 2", marker='o')
#     else:
#         ax.plot(time_plot, bench_plot_T_g, label="Benchmark")
#         ax.plot(time_plot, scenA_plot_T_g, label="Do Nothing")
#         ax.plot(time_plot, scenC_plot_T_g, label="Benchmark w/o Glow")
#         ax.plot(time_plot, scenD_plot_T_g, label="Every 5")
#         ax.plot(time_plot, scenE_plot_T_g, label="Every 2")
#     plt.ylim(ymin=0.0)

#     plt.legend()
#     plt.grid(True)
#     ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
#     ax.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
#     plt.xticks(time_plot[1:])
#     plt.xlabel('Day', fontsize=14)
#     plt.ylabel('Concentration (g)', fontsize=14)
#     plt.title(f'Two Week Cycle Scenarios: Tritium', fontsize=16)
    
#     plt.savefig('T_total_inv.png')


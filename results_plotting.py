import json
import matplotlib.pyplot as plt
from make_iter_bins import Div_bins, total_nb_bins, total_fw_bins
import math
import numpy as np
from collections import Counter

TRITIUM_AMU = 3.016049 # g/mol
D_AMU = 2.014102 # g/mol
AVOGADROS_CONST = 6.0221408e+23 # atms/mol

# open results file
with open('benchmark_results.json', 'r') as file:
    benchmark_data = json.load(file)

global_dict = {}

for bin_index in range(total_fw_bins,total_nb_bins):
    div_bin = Div_bins.get_bin(bin_index)
    avg_r_coord = 0.5*abs(div_bin.start_point[0]+div_bin.end_point[0])
    bin_surf_area = 2*math.pi*avg_r_coord*div_bin.length

    bin_data = benchmark_data[bin_index]

    for name, quantities_dict in bin_data.items():
        if name != "bin_index":
            print(name)
            data = np.array(quantities_dict['data'])
            global_dict.setdefault('t', quantities_dict['t'])
            if "D" in name:
                if "trap" in name:
                    global_dict["Trapped_Deuterium"] = global_dict.get("Trapped_Deuterium", np.zeros_like(data)) + data * bin_surf_area
                else:
                    global_dict["Mobile_Deuterium"] = global_dict.get("Mobile_Deuterium", np.zeros_like(data)) + data * bin_surf_area
            else:
                if "trap" in name:
                    global_dict["Trapped_Tritium"] = global_dict.get("Trapped_Tritium", np.zeros_like(data)) + data * bin_surf_area
                else:
                    global_dict["Mobile_Tritium"] = global_dict.get("Mobile_Tritium", np.zeros_like(data)) + data * bin_surf_area

plt.plot(global_dict['t'], global_dict["Mobile_Deuterium"], label="Mobile_Deuterium", marker="o")
plt.plot(global_dict['t'], global_dict["Mobile_Tritium"], label="Mobile_Tritium", marker="o")
plt.plot(global_dict['t'], global_dict["Trapped_Deuterium"], label="Trapped_Deuterium", marker="o")
plt.plot(global_dict['t'], global_dict["Trapped_Tritium"], label="Trapped_Tritium", marker="o")

plt.xlabel("Time (s)")
plt.ylabel("Total inventory (atm)")
plt.title("Inventory in Bin 50, Benchmark Scenario")
plt.legend()
plt.yscale("log")

plt.show()

# to plot one bin
# for i in bin_data.items():
#     name = i[0]
#     if name!="bin_index":
#         print(name)
#         quantities_dict = i[1]
#         data = np.array(quantities_dict['data'])
#         if "D" in name:
#             plt.plot(quantities_dict['t'], data*bin_surf_area, label=name, marker="o")
#         else:
#             plt.plot(quantities_dict['t'], data*bin_surf_area, label=name, marker="o")



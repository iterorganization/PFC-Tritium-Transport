import json
import matplotlib.pyplot as plt
from make_iter_bins import Div_bins, total_nb_bins, total_fw_bins, FW_bins
import math
import numpy as np
from collections import Counter

TRITIUM_AMU = 3.016049 # g/mol
D_AMU = 2.014102 # g/mol
AVOGADROS_CONST = 6.0221408e+23 # atms/mol

BIN_INDEX = 49

if BIN_INDEX in range(total_fw_bins):
    my_bin = FW_bins.get_bin(BIN_INDEX)
else: 
    my_bin = Div_bins.get_bin(BIN_INDEX)

avg_r_coord = 0.5*abs(my_bin.start_point[0]+my_bin.end_point[0])
bin_surf_area = 2*math.pi*avg_r_coord*my_bin.length

# open results file
with open('results_benchmark.json', 'r') as file:
    dict_data = json.load(file)

bin_data = dict_data[BIN_INDEX]

for i in bin_data.items():
    name = i[0]
    if name!="bin_index":
        print(name)
        quantities_dict = i[1]
        data = np.array(quantities_dict['data'])
        if "D" in name:
            plt.plot(quantities_dict['t'], data, label=name, marker="o", linewidth=0.5, markersize=0.5)
        else:
            plt.plot(quantities_dict['t'], data, label=name, marker="o", linewidth=0.5, markersize=0.75)

plt.xlabel("Time (s)")
plt.ylabel("Total Quantity (atms/m^2)")
plt.title("Bin "+str(BIN_INDEX)+" Results Benchmark Scenario")
plt.yscale("log")
plt.legend()
plt.show()

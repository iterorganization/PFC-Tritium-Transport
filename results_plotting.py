import json
import matplotlib.pyplot as plt
from make_iter_bins import Div_bins
import math
import numpy as np

TRITIUM_AMU = 3.016049 # g/mol
D_AMU = 2.014102 # g/mol
AVOGADROS_CONST = 6.0221408e+23 # atms/mol

# open results file
with open('benchmark_results.json', 'r') as file:
    benchmark_data = json.load(file)

bin_index = 49

div_bin = Div_bins.get_bin(bin_index)
div_bin.start_point = (-3.923999999999999932e+00,4.157000000000000028e+00)
div_bin.end_point = (-3.869000000000000217e+00,4.184000000000000163e+00)
bin_surf_area = 2*math.pi*0.5*div_bin.length

bin_data = benchmark_data[bin_index]
# print(bin_data.items())
for i in bin_data.items():
    name = i[0]
    if name!="bin_index":
        print(name)
        quantities_dict = i[1]
        data = np.array(quantities_dict['data'])
        if "D" in name:
            plt.plot(quantities_dict['t'], data*bin_surf_area, label=name, marker="o")
        else:
            plt.plot(quantities_dict['t'], data*bin_surf_area, label=name, marker="o")

plt.xlabel("Time (s)")
plt.ylabel("Total inventory (atm)")
plt.title("Inventory in Bin 50, Benchmark Scenario")
plt.legend()
plt.yscale("log")

plt.show()



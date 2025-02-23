import json
import matplotlib.pyplot as plt
from make_iter_bins import Div_bins, total_nb_bins, total_fw_bins, FW_bins
import math
import numpy as np
from collections import Counter

TRITIUM_AMU = 3.016049  # g/mol
D_AMU = 2.014102  # g/mol
AVOGADROS_CONST = 6.0221408e23  # atms/mol

BIN_INDEX = 22

def get_bin_data(data: list, bin_index: int) -> dict:
    """Returns the right dictionary for a given bin index

    Args:
        data (list): the list of dictionaries
        bin_index (int): the bin index
    """

    for i in data:
        if i["bin_index"] == bin_index:
            return i

if BIN_INDEX in range(total_fw_bins):
    my_bin = FW_bins.get_bin(BIN_INDEX)
else:
    my_bin = Div_bins.get_bin(BIN_INDEX)

avg_r_coord = 0.5 * abs(my_bin.start_point[0] + my_bin.end_point[0])
bin_surf_area = 2 * math.pi * avg_r_coord * my_bin.length

# open results file
with open("processed_data.json", "r") as file:
    dict_data = json.load(file)

bin_data = get_bin_data(dict_data, BIN_INDEX)

if BIN_INDEX in list(range(18,65)):
    plt.figure()
    Time_Full = False
    D_Full = False
    for name, value in bin_data.items():
        # skip the bin_index
        if name == "bin_index":
            continue
        quantities_dict = value
        if not Time_Full:
            time = quantities_dict["t"]
            Time_Full = True
        D_inventory = np.zeros(len(time))
        T_inventory = np.zeros(len(time))
    for name, value in bin_data.items():
        # skip the bin_index
        if name == "bin_index":
            continue
        print(name)
        quantities_dict = value
        data = np.array(quantities_dict["data"])
        if "D" in name:
            D_inventory += data
        else:
            T_inventory += data
    D_grams = D_inventory * bin_surf_area / AVOGADROS_CONST * D_AMU
    T_grams = T_inventory * bin_surf_area / AVOGADROS_CONST * D_AMU
    plt.plot(time, D_grams, label="D", marker="o", linewidth=0.5, markersize=0.75)
    plt.plot(time, T_grams, label="T", marker="o", linewidth=0.5, markersize=0.75)
    plt.vlines([429,1079,1534,86400,86829,87479,87934,172800,173229,173879,174334],0,50,linestyles="-", linewidth=0.1)
    plt.xlabel("Time (s)")
    plt.ylabel("Total Quantity (g)")
    plt.title("Bin " + str(BIN_INDEX+1) + " Results Benchmark Scenario")
    plt.yscale("log")
    plt.legend()
    plt.show()

else:
    sub_bin_data = bin_data["sub_bins"]
    Time_Full = False
    D_Full = False
    plt.figure()
    for sub_bin in sub_bin_data[0:3]:
        mode = sub_bin["mode"]
        for name, quantities_dict in sub_bin.items():
            # skip the parent bin_index
            if name == "parent_bin_index":
                continue
            if name == "mode": 
                continue
            if not Time_Full:
                time = quantities_dict["t"]
                Time_Full = True
        D_sub = np.zeros(len(time))
        T_sub = np.zeros(len(time))
        for name, quantities_dict in sub_bin.items():
            # skip the parent bin_index
            if name == "parent_bin_index":
                continue
            if name == "mode": 
                continue
            print(name)
            data = np.array(quantities_dict["data"])
            if "D" in name:
                D_sub += data
            else:
                T_sub += data
        if not D_Full:
            D_inventory = D_sub
            T_inventory = T_sub
            D_Full = True
        else:
            D_inventory += D_sub
            T_inventory += T_sub

    D_grams = D_inventory * bin_surf_area / AVOGADROS_CONST * D_AMU
    T_grams = T_inventory * bin_surf_area / AVOGADROS_CONST * D_AMU
    plt.plot(time, D_grams, label="D", marker="o", linewidth=0.5, markersize=0.75)
    plt.plot(time, T_grams, label="T", marker="o", linewidth=0.5, markersize=0.75)
    plt.vlines([429,1079,1534,86400,86829,87479,87934,172800,173229,173879,174334],0,50,linestyles="-", linewidth=0.1)
    plt.xlabel("Time (s)")
    plt.ylabel("Total Quantity (g)")
    plt.title("Bin " + str(BIN_INDEX+1) + " "+mode+" Results Benchmark Scenario")
    plt.yscale("log")
    plt.legend()
    plt.show()
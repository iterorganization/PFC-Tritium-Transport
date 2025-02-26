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

if BIN_INDEX in range(total_fw_bins):
    my_bin = FW_bins.get_bin(BIN_INDEX)
else:
    my_bin = Div_bins.get_bin(BIN_INDEX)

avg_r_coord = 0.5 * abs(my_bin.start_point[0] + my_bin.end_point[0])
bin_surf_area = 2 * math.pi * avg_r_coord * my_bin.length

# open results file
with open("processed_22.json", "r") as file:
    dict_data = json.load(file)


def get_bin_data(data: list, bin_index: int) -> dict:
    """Returns the right dictionary for a given bin index

    Args:
        data (list): the list of dictionaries
        bin_index (int): the bin index
    """

    for i in data:
        if i["bin_index"] == bin_index:
            return i


bin_data = get_bin_data(dict_data, BIN_INDEX)

if BIN_INDEX in list(range(18,65)):
    plt.figure()
    for name, value in bin_data.items():
        # skip the bin_index
        if name == "bin_index":
            continue
        elif name == "surface_temperature" or "flux" in name:
            continue
        print(name)
        quantities_dict = value
        data = np.array(quantities_dict["data"])
        if "D" in name:
            plt.plot(
                quantities_dict["t"],
                data,
                label=name,
                marker="o",
                linewidth=0.5,
                markersize=0.5,
            )
        else:
            plt.plot(
                quantities_dict["t"],
                data,
                label=name,
                marker="o",
                linewidth=0.5,
                markersize=0.75,
            )
    plt.xlabel("Time (s)")
    plt.ylabel("Total Quantity (atms/m^2)")
    plt.title("Bin " + str(BIN_INDEX) + " Results Test Scenario")
    plt.yscale("log")
    plt.legend()
    plt.savefig('out.png')
    plt.show()

else:
    sub_bin_data = bin_data["sub_bins"]
    for sub_bin in sub_bin_data:
        mode = sub_bin["mode"]
        plt.figure()
        for name, quantities_dict in sub_bin.items():
            # skip the parent bin_index
            if name == "parent_bin_index":
                continue
            if name == "mode": 
                continue
            print(name)
            data = np.array(quantities_dict["data"])
            if "D" in name:
                plt.plot(
                    quantities_dict["t"],
                    data,
                    label=name,
                    marker="o",
                    linewidth=0.5,
                    markersize=0.5,
                )
            else:
                plt.plot(
                    quantities_dict["t"],
                    data,
                    label=name,
                    marker="x",
                    linewidth=0.5,
                    markersize=0.75,
                )
        plt.xlabel("Time (s)")
        plt.ylabel("Total Quantity (atms/m^2)")
        plt.title("Bin " + str(BIN_INDEX) + " "+mode+" Results Benchmark Scenario")
        plt.yscale("log")
        plt.legend()
        plt.savefig(f'bin_{BIN_INDEX}_{mode}.png')
        plt.show()



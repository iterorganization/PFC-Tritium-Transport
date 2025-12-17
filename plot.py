from make_iter_bins import Div_bins, total_fw_bins, FW_bins
import json
import matplotlib.pyplot as plt
import numpy as np

from iter_scenarios.do_nothing import scenario as do_nothing_scenario
from iter_scenarios.just_glow import scenario as just_glow_scenario
from iter_scenarios.capability_test import scenario as capability_test_scenario

scenario_to_colour = {
    just_glow_scenario: "tab:blue",
    do_nothing_scenario: "tab:orange",
    capability_test_scenario: "tab:green",
}

scenario_to_letter = {
    do_nothing_scenario: "A",
    just_glow_scenario: "B",
    capability_test_scenario: "C",
}

def calculate_bin_surface_area(bin_start_point, bin_end_point, bin_length):
    avg_r_coord = 0.5 * abs(bin_start_point[0] + bin_end_point[0])
    return 2 * np.pi * avg_r_coord * bin_length

def plot_scenario(t_plot_data: dict, scenario, fp10_value = None):
    # create material inv lists with number of points determined by length of data list
    data_t_len = len(t_plot_data["0"]["high_wetted"])
    boron_inv_wall = np.zeros(data_t_len)
    boron_inv_div = np.zeros(data_t_len)
    tungsten_inv_wall = np.zeros(data_t_len)
    tungsten_inv_div = np.zeros(data_t_len)
    ss_inv_wall = np.zeros(data_t_len)
    ss_inv_div = np.zeros(data_t_len)

    if scenario == just_glow_scenario:
        x_values = [2, 4, 5]

    elif scenario == do_nothing_scenario:
        x_values = [1.9, 2, 5]
    elif scenario == capability_test_scenario:
        x_values = [0, 1, 2, 3, 4, 5]


    # extract inv in materials
    for name, value in t_plot_data.items():
        for mode, data_lst in value.items():
            bin_idx = int(name)

            if bin_idx in range(18):
                bin_length = FW_bins.get_bin(bin_idx).length
                
                if mode == "shadowed":
                    material = FW_bins.get_bin(bin_idx).shadowed_subbin.material
                elif mode == "low_wetted":
                    material = FW_bins.get_bin(bin_idx).low_wetted_subbin.material
                elif mode == "high_wetted":
                    material = FW_bins.get_bin(bin_idx).high_wetted_subbin.material
                else:
                    material = FW_bins.get_bin(bin_idx).wetted_subbin.material
                if material == "B":
                    boron_inv_wall += data_lst
                elif material == "W":
                    tungsten_inv_wall += data_lst
                else:
                    ss_inv_wall += data_lst

            else:
                material = Div_bins.get_bin(bin_idx).material
                bin_surf_area = calculate_bin_surface_area(
                    Div_bins.get_bin(bin_idx).start_point,
                    Div_bins.get_bin(bin_idx).end_point,
                    Div_bins.get_bin(bin_idx).length,
                )
                if material == "B":
                    boron_inv_div += np.array(data_lst)*bin_surf_area
                elif material == "W":
                    tungsten_inv_div += np.array(data_lst)*bin_surf_area
                else:
                    ss_inv_div += np.array(data_lst)*bin_surf_area

    if scenario == do_nothing_scenario:
        correct_fp10_value = boron_inv_wall[0]
        correction_factor=1
    elif scenario == just_glow_scenario:
        correction_factor = fp10_value/boron_inv_wall[0]
    else:
        correction_factor=1

    ax_top.plot(
        x_values,
        boron_inv_wall*correction_factor,
        color=scenario_to_colour[scenario],
        linestyle="dashed",
        marker="o",
        label=scenario_to_letter[scenario],
        linewidth=2,
    )
    ax_top.plot(
        x_values,
        tungsten_inv_wall,
        color=scenario_to_colour[scenario],
        linestyle="dashed",
        marker="o",
        linewidth=2,
    )
    # ax_top.annotate(
    #     text="B", xy=(1 + 0.1, boron_inv_wall[-1] + 0.1), color="firebrick"
    # )
    # ax_top.annotate(
    #     text="W", xy=(1 + 0.1, tungsten_inv_wall[-1] + 0.1), color="royalblue"
    # )
    # ax_top.annotate(
    #     f"-{float(np.diff(boron_inv_wall)) / boron_inv_wall[0]:.2%}",
    #     xy=(0.5, np.mean(boron_inv_wall) * 1.1),
    #     color="firebrick",
    # )
    # ax_top.annotate(
    #     f"-{float(np.diff(tungsten_inv_wall)) / tungsten_inv_wall[0]:.2%}",
    #     xy=(0.5, np.mean(tungsten_inv_wall) * 1.01),
    #     color="royalblue",
    # )

    ax_bot.plot(
        x_values,
        boron_inv_div,
        marker="o",
        color=scenario_to_colour[scenario],
        linestyle="dashed",
        linewidth=2,
    )
    ax_bot.plot(
        x_values,
        tungsten_inv_div,
        marker="o",
        color=scenario_to_colour[scenario],
        linestyle="dashed",
        linewidth=2,
    )

    # ax_bot.annotate(f"x{boron_inv_div[-1]/boron_inv_div[0]:.2f}", xy=(0.5, np.mean(boron_inv_div)*1.1) , color="firebrick")
    # ax_bot.annotate(f"x{tungsten_inv_div[-1]/tungsten_inv_div[0]:.2f}", xy=(0.5, np.mean(tungsten_inv_div)*1.1) , color="royalblue")

    # ax_bot.annotate(
    #     f"-{float(np.diff(boron_inv_div)) / boron_inv_div[0]:.2%}",
    #     xy=(0.5, np.mean(boron_inv_div) * 1.1),
    #     color="firebrick",
    # )
    # ax_bot.annotate(
    #     f"-{float(np.diff(tungsten_inv_div)) / tungsten_inv_div[0]:.2%}",
    #     xy=(0.5, np.mean(tungsten_inv_div) * 1.05),
    #     color="royalblue",
    # )

    if scenario == do_nothing_scenario:
        return correct_fp10_value


# create scatter plot in matplotlib
fig, (ax_top, ax_bot) = plt.subplots(2, 1, sharex=True, figsize=(10, 8))


with open("results_just_glow_D_data.json", "r") as file:
    d_plot_data = json.load(file)

with open("results_just_glow_T_data.json", "r") as file:
    t_plot_data_just_glow = json.load(file)

with open("results_do_nothing_T_data.json", "r") as file:
    t_plot_data_do_nothing = json.load(file)

with open("results_capability_test_T_data.json", "r") as file:
    t_plot_data_capability_test = json.load(file)

correct_fp10_value = plot_scenario(t_plot_data_do_nothing, do_nothing_scenario)
plot_scenario(t_plot_data_just_glow, just_glow_scenario, fp10_value=correct_fp10_value)
plot_scenario(t_plot_data_capability_test, capability_test_scenario)

ax_top.annotate(
    text="in Boron",
    xy=(-0.1, 3e22),
    color="tab:grey",
    fontsize=14,
    ha="right",
    va="center",
)
ax_top.annotate(
    text="in Tungsten",
    xy=(-0.1, 3.6e20),
    color="tab:grey",
    fontsize=14,
    ha="right",
    va="center",
)

ax_bot.annotate(
    text="in Boron",
    xy=(-0.1, 4.7e24),
    color="tab:grey",
    fontsize=14,
    ha="right",
    va="center",
)
ax_bot.annotate(
    text="in Tungsten",
    xy=(-0.1, 4.7e21),
    color="tab:grey",
    fontsize=14,
    ha="right",
    va="center",
)


ax_top.set_yscale("log")
ax_bot.set_yscale("log")
ax_top.set_ylabel("Inventory (T/m^3)", fontsize=14)
ax_bot.set_ylabel("Inventory (T/m)",fontsize=14)
# ax_top.legend(loc='upper left')
ax_top.grid(which="both", alpha=0.3)
ax_bot.grid(which="both", alpha=0.3)

ax_top.set_title("Wall", fontsize=20)
ax_bot.set_title("Divertor", fontsize=20)


x_labels = [
    "After 5 FP",
    "After LP D",
    "After 10 FP",
    "After LP D",
    "After GDC",
    "After BAKE",
]

ax_top.set_xticks(np.arange(len(x_labels)), x_labels)
ax_bot.set_xticks(np.arange(len(x_labels)), x_labels, fontsize=14)

# create a legend for each scenario

ax_top.legend(
    title="Scenario", bbox_to_anchor=(1.05, 0), loc="upper left", frameon=False, fontsize=14, title_fontsize=14
)


for ax in [ax_top, ax_bot]:
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_xlim(left=-1.2)
    # ax.set_ylim(1e18, 1e20)

plt.tight_layout()
# plt.legend(handles=[tungsten,boron],loc='upper right')
plt.savefig("paper_plots/material-comp.pdf", bbox_inches="tight")
# plt.savefig("paper_plots/material-comp.png", bbox_inches="tight")
# plt.show()

# plot final inventory
fig, axs = plt.subplots(nrows=2, ncols=1, figsize=(6, 8), sharex=True)

for data, scenario in zip(
    [t_plot_data_do_nothing, t_plot_data_just_glow, t_plot_data_capability_test],
    [do_nothing_scenario, just_glow_scenario, capability_test_scenario],
):
    total_inv_fw = 0
    total_inv_div = 0
    for name, value in data.items():
        for mode, data_lst in value.items():
            bin_idx = int(name)
            if bin_idx in range(18):
                total_inv_fw += data_lst[-1]
            else:
                total_inv_div += data_lst[-1]
    axs[0].bar(
        scenario_to_letter[scenario],
        total_inv_fw,
        color=scenario_to_colour[scenario],
        label=scenario_to_letter[scenario],
    )
    axs[1].bar(
        scenario_to_letter[scenario],
        total_inv_div,
        color=scenario_to_colour[scenario],
        label=scenario_to_letter[scenario],
    )

# annotate bars
fmt = "{:.2e}"

plt.sca(axs[0])
for c in axs[0].containers:
    plt.bar_label(c, fmt=fmt)

plt.sca(axs[1])
for c in axs[1].containers:
    plt.bar_label(c, fmt=fmt)

axs[0].set_ylabel("Total Inventory (T)")
axs[0].set_title("Wall")

axs[1].set_ylabel("Total Inventory (T/m)")
axs[1].set_title("Divertor")

for ax in axs:
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(which="both", alpha=0.3, axis="y")

plt.tight_layout()
plt.savefig("paper_plots/final_inventory.pdf", bbox_inches="tight")
plt.show()

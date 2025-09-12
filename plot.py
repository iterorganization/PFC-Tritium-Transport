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


def plot_scenario(t_plot_data: dict, scenario):
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
    # x_ticks = np.arange(len(t_plot_data["0"]["high_wetted"]) + 1)

    # extract inv in materials
    for name, value in t_plot_data.items():
        for mode, data_lst in value.items():
            bin_idx = int(name)

            if bin_idx in range(18):
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

                if material == "B":
                    boron_inv_div += data_lst
                elif material == "W":
                    tungsten_inv_div += data_lst
                else:
                    ss_inv_div += data_lst

    ax_top.plot(
        x_values,
        boron_inv_wall,
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


# create scatter plot in matplotlib
fig, (ax_top, ax_bot) = plt.subplots(2, 1, sharex=True, figsize=(10, 8))


with open("results_just_glow_D_data.json", "r") as file:
    d_plot_data = json.load(file)

with open("results_just_glow_T_data.json", "r") as file:
    t_plot_data_just_glow = json.load(file)

with open("results_do_nothing_T_data.json", "r") as file:
    t_plot_data_do_nothing = json.load(file)

plot_scenario(t_plot_data_do_nothing, do_nothing_scenario)
plot_scenario(t_plot_data_just_glow, just_glow_scenario)

ax_top.annotate(text="B", xy=(5.12, 3e22), color="black", fontsize=14)
ax_top.annotate(text="W", xy=(4.12, 5e20), color="black", fontsize=14)

ax_bot.annotate(text="B", xy=(5.12, 5e24), color="black", fontsize=14)
ax_bot.annotate(text="W", xy=(4.12, 6e21), color="black", fontsize=14)


ax_top.set_yscale("log")
ax_bot.set_yscale("log")
ax_top.set_ylabel("Inventory (T)")
ax_bot.set_ylabel("Inventory (T/m)")
# ax_top.legend(loc='upper left')
ax_top.grid(which="both", alpha=0.3)
ax_bot.grid(which="both", alpha=0.3)

ax_top.set_title("Wall")
ax_bot.set_title("Divertor")


x_labels = [
    "After 5 FP",
    "After LP D",
    "After 10 FP",
    "After LP D",
    "After GDC",
    "After BAKE",
]

ax_top.set_xticks(np.arange(len(x_labels)), x_labels)
ax_bot.set_xticks(np.arange(len(x_labels)), x_labels)

# create a legend for each scenario

ax_top.legend(title="Scenario")


for ax in [ax_top, ax_bot]:
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_xlim(left=-0.2)
    # ax.set_ylim(1e18, 1e20)

plt.tight_layout()
# plt.legend(handles=[tungsten,boron],loc='upper right')
plt.savefig("paper_plots/material-comp.pdf", bbox_inches="tight")
# plt.savefig("paper_plots/material-comp.png", bbox_inches="tight")
plt.show()
print("done")

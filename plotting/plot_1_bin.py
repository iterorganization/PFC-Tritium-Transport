import json
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use("TkAgg")  # Forces external interactive plots

# Load the JSON file
file_path = "results_just_glow/div_bin_18.json"  # Update the path if needed
with open(file_path, "r") as file:
    data = json.load(file)

# Loop through all keys in the dictionary and plot them
for key, values in data.items():
    if isinstance(values, dict) and "t" in values and "data" in values:
        time_values = values["t"]
        time_values = [time / 60 / 60 for time in time_values] # Divide all time values by 3600
        data_values = values["data"]
        plt.plot(time_values, data_values, label=f"{key}", marker="x", markersize=4)


# Customize plot with logarithmic scale
# plt.xscale("lin")
plt.yscale("log")
plt.xlabel("Time (hours)")
plt.ylabel("Data Value (log scale)")
plt.title("Log Plot for one Bin")
plt.legend()
plt.grid(which="both", linestyle="--", linewidth=0.5)

# Show plot
plt.show()
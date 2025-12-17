import matplotlib
import matplotlib.pyplot as plt
import numpy as np
matplotlib.use("TkAgg")  # Forces external interactive plots
import pandas as pd

# Load the data
file_path = "iter_bins/iter_bins.dat"
df = pd.read_csv(file_path)

# Plot each segment and label them with a counter
SFW = 0
Sdiv = 0
plt.figure(figsize=(2, 5))
for i, row in df.iterrows():
    z_start, r_start, z_end, r_end = row
    plt.plot([r_start, r_end], [z_start, z_end], 'b')  # Flipping axes: R is x, Z is y
    # Label the middle of the segment
    r_mid = (r_start + r_end) / 2
    z_mid = (z_start + z_end) / 2
    plt.text(r_mid, z_mid, str(i+1), fontsize=8, color='red', ha='center', va='center', bbox=dict(facecolor='white', alpha=0.7, edgecolor='gray'))
    if (i+1 > 18):
        Sdiv += 2*3.14*r_mid*np.sqrt((r_start - r_end)**2.0 + (z_start - z_end)**2.0)
    else:
        SFW += 2*3.14*r_mid*np.sqrt((r_start - r_end)**2.0 + (z_start - z_end)**2.0)


print(Sdiv)
print(SFW)
print(Sdiv+SFW)

# plt.xlabel("R")
# plt.ylabel("Z")
# plt.xlim(3.8, 6.6)
# plt.ylim(-4.8,-2)
plt.grid(True)
plt.axis('equal')
# plt.xlim(3.8, 6.6)
plt.tight_layout()
plt.show()
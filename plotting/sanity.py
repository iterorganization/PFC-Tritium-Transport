#!/usr/bin/env python3
"""
Scan for folders named like `mb<bin>_<mode>_results` (e.g. mb0_wetted_results)
and for each folder plot the T profiles (mobile and trap *_T.h5) at the last
available time-step. The plot uses log-log scale for depth (x) and
concentration (y) and is saved in the folder as `profiles_last_T_loglog.png`.

Usage: run from the parent directory that contains the mb folders, or pass a
root directory as the first CLI argument.
"""

import sys
import os
import glob
import h5py
import numpy as np
import matplotlib.pyplot as plt

# Target specific folder
target_folder = "/home/ITER/llealsa/AdriaLlealS/PFC-Tritium-Transport-dolfinx10/mb47_wetted_results"

if not os.path.isdir(target_folder):
    print(f"Target folder not found: {target_folder}")
    sys.exit(0)

folders = [target_folder]

for folder in folders:
    print(f"Processing folder: {folder}")
    # find all T-related h5 files with the correct naming pattern
    t_files = []
    t_files.extend(glob.glob(os.path.join(folder, "mobile_concentration_t.h5")))
    t_files.extend(glob.glob(os.path.join(folder, "trapped_concentration_t*.h5")))
    t_files = sorted(t_files)
    
    if not t_files:
        print(f"  No T concentration files found in {folder}; skipping")
        continue
    
    print(f"  Found files: {[os.path.basename(f) for f in t_files]}")

    # Collect profile data every 100s and create plots
    profiles_by_time = {}  # {time: {species: concentration_array}}
    x_ref = None

    for fpath in t_files:
        # Create a cleaner label from filename
        basename = os.path.splitext(os.path.basename(fpath))[0]
        if "mobile" in basename:
            label = "mobile_T"
        elif "trapped" in basename:
            if "t1" in basename:
                label = "trap1_T"
            elif "t2" in basename:
                label = "trap2_T"
            else:
                label = "trapped_T"
        else:
            label = basename
        
        try:
            with h5py.File(fpath, "r") as f:
                # coordinates
                if "/Mesh/mesh/geometry" not in f:
                    print(f"  {fpath}: mesh geometry not found; skipping file")
                    continue
                coords = np.asarray(f["/Mesh/mesh/geometry"])[:, 0]

                # find time group
                if "/Function" not in f:
                    print(f"  {fpath}: '/Function' group not found; skipping file")
                    continue
                subgroups = list(f["/Function"].keys())
                if not subgroups:
                    print(f"  {fpath}: no subgroups under /Function; skipping file")
                    continue
                time_group = f"/Function/{subgroups[0]}"
                time_keys = list(f[time_group].keys())
                if not time_keys:
                    print(f"  {fpath}: no time datasets under {time_group}; skipping file")
                    continue

                # parse all times and process every 100s
                t_floats = [float(k.replace("_", ".")) for k in time_keys]
                
                # Set reference coordinates from first file
                if x_ref is None:
                    x_ref = np.asarray(coords)
                
                # Process all timesteps
                for i, (time_key, time_val) in enumerate(zip(time_keys, t_floats)):
                    # Only process times that are close to multiples of 100s
                    # Round to nearest 100 and check if we're within 5s of a multiple
                    nearest_hundred = round(time_val / 100) * 100
                    if abs(time_val - nearest_hundred) <= 5.0:
                        try:
                            dataset = np.asarray(f[f"{time_group}/{time_key}"])
                            if dataset.ndim == 1:
                                conc = dataset
                            else:
                                conc = dataset[:, 0]
                            
                            # Align coordinates if needed
                            x_cur = np.asarray(coords)
                            if (len(x_cur) != len(x_ref)) or np.max(np.abs(x_cur - x_ref)) > 1e-14:
                                order = np.argsort(x_cur)
                                conc = np.interp(x_ref, x_cur[order], conc[order])
                            
                            # Store profile data - use the rounded time as key
                            if nearest_hundred not in profiles_by_time:
                                profiles_by_time[nearest_hundred] = {}
                            profiles_by_time[nearest_hundred][label] = conc
                            
                        except Exception as e:
                            print(f"  Error processing time {time_val} in {fpath}: {e}")
                            continue

        except Exception as e:
            print(f"  Error reading {fpath}: {e}; skipping")
            continue

    # Create plots for each time point (every 100s)
    if profiles_by_time and x_ref is not None:
        print(f"  Creating plots every 100s...")
        
        # Prepare x for log scale
        x = np.array(x_ref)
        positive_mask = x > 0
        if not np.any(positive_mask):
            x_plot = np.logspace(-12, -3, num=len(x))
        else:
            minpos = np.min(x[positive_mask])
            x_plot = x.copy()
            x_plot[x_plot <= 0] = minpos * 1e-3
        
        for time_val in sorted(profiles_by_time.keys()):
            profiles = profiles_by_time[time_val]
            
            plt.figure(figsize=(8.5, 6.0))
            for label, y in profiles.items():
                y_arr = np.asarray(y, dtype=float)
                # ensure positive values for log scale
                pos_mask = y_arr > 0
                if np.any(pos_mask):
                    minposy = np.min(y_arr[pos_mask])
                    y_plot = y_arr.copy()
                    y_plot[~pos_mask] = minposy * 1e-6
                else:
                    y_plot = np.full_like(y_arr, 1e-20)

                plt.plot(x_plot, y_plot, label=label, linewidth=2)

            plt.yscale("log")
            plt.xlabel("Depth x (m)")
            plt.ylabel("Concentration")
            
            x_max = np.max(x_plot)
            plt.xlim(1e-3, x_max)
            
            plt.title(f"Profiles (T) at t = {time_val:g} s\n{os.path.basename(folder)}")
            plt.grid(True, alpha=0.3)
            plt.legend(loc="best")
            plt.tight_layout()

            out_path = os.path.join(folder, f"profiles_T_t{int(time_val):06d}s.png")
            try:
                plt.savefig(out_path, dpi=200)
                print(f"    Saved: {os.path.basename(out_path)}")
            except Exception as e:
                print(f"    Error saving {out_path}: {e}")
            plt.close()
    else:
        print(f"  No valid profile data found")

print("Done.")

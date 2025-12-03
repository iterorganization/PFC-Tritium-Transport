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
import xml.etree.ElementTree as ET

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
PATTERN = os.path.join(ROOT, "mb*_*_results")

def read_xdmf_file(xdmf_path):
    """
    Read an XDMF file and return coordinates and time series data.
    XDMF files are XML that reference HDF5 data files.
    """
    try:
        # Parse the XDMF XML file
        tree = ET.parse(xdmf_path)
        root = tree.getroot()
        
        # Look for the associated HDF5 file
        h5_file = None
        for elem in root.iter():
            if elem.tag.endswith('DataItem') and elem.get('Format') == 'HDF':
                h5_ref = elem.text.strip()
                if ':' in h5_ref:
                    h5_filename = h5_ref.split(':')[0]
                    h5_file = os.path.join(os.path.dirname(xdmf_path), h5_filename)
                    break
        
        if h5_file and os.path.exists(h5_file):
            # Try to read the HDF5 file directly
            return read_h5_file(h5_file)
        else:
            print(f"  Could not find HDF5 data file for {xdmf_path}")
            return None, None, None
            
    except Exception as e:
        print(f"  Error parsing XDMF file {xdmf_path}: {e}")
        return None, None, None

def read_h5_file(h5_path):
    """Read an HDF5 file and return coordinates and time series data."""
    try:
        with h5py.File(h5_path, "r") as f:
            # coordinates
            if "/Mesh/mesh/geometry" not in f:
                print(f"  {h5_path}: mesh geometry not found")
                return None, None, None
            coords = np.asarray(f["/Mesh/mesh/geometry"])[:, 0]

            # find time group and keys
            if "/Function" not in f:
                print(f"  {h5_path}: '/Function' group not found")
                return None, None, None
            subgroups = list(f["/Function"].keys())
            if not subgroups:
                print(f"  {h5_path}: no subgroups under /Function")
                return None, None, None
            time_group = f"/Function/{subgroups[0]}"
            time_keys = list(f[time_group].keys())
            if not time_keys:
                print(f"  {h5_path}: no time datasets under {time_group}")
                return None, None, None

            # parse times
            t_floats = [float(k.replace("_", ".")) for k in time_keys]

            # target index: closest to 72000 s
            t_target = 72000.0
            idx_target = int(np.argmin([abs(t - t_target) for t in t_floats]))
            key_target = time_keys[idx_target]

            # last index: max time
            idx_last = int(np.argmax(t_floats))
            key_last = time_keys[idx_last]

            # load target dataset
            dataset_t = np.asarray(f[f"{time_group}/{key_target}"])
            if dataset_t.ndim == 1:
                conc_t = dataset_t
            else:
                conc_t = dataset_t[:, 0]

            # load last dataset
            dataset_l = np.asarray(f[f"{time_group}/{key_last}"])
            if dataset_l.ndim == 1:
                conc_l = dataset_l
            else:
                conc_l = dataset_l[:, 0]

            return coords, (conc_t, float(t_floats[idx_target])), (conc_l, float(t_floats[idx_last]))
            
    except Exception as e:
        print(f"  Error reading HDF5 file {h5_path}: {e}")
        return None, None, None

# Helper to create and save a log-log plot from a profiles dict
def _plot_profiles_loglog(x_ref, profiles_dict, times_dict, out_filename, title_extra, folder):
    # Prepare x for log scale: remove or replace zero/negative coordinates
    x = np.array(x_ref)
    
    # Use the actual thickness from the mesh data
    thickness = np.max(x)
    
    positive_mask = x > 0
    if not np.any(positive_mask):
        x_plot = np.logspace(-12, -3, num=len(x))
    else:
        minpos = np.min(x[positive_mask])
        x_plot = x.copy()
        x_plot[x_plot <= 0] = minpos * 1e-3

    x_plot[x_plot < 1e-10] = 1e-10

    # Build plot
    plt.figure(figsize=(8.5, 6.0))
    for label, y in profiles_dict.items():
        y_arr = np.asarray(y, dtype=float)
        # Remove restriction: just mask non-positive values
        pos_mask = y_arr > 0
        if np.any(pos_mask):
            y_plot = y_arr.copy()
            y_plot[~pos_mask] = np.nan  # Let matplotlib skip invalid points
        else:
            y_plot = np.full_like(y_arr, np.nan, dtype=float)

        plt.plot(x_plot, y_plot, label=label, linewidth=2)

    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("Depth x (m)")
    plt.ylabel("Concentration")
    
    # Set x-axis limits from minimum positive value to thickness
    min_x = np.min(x_plot[x_plot > 0]) if np.any(x_plot > 0) else 1e-10
    plt.xlim(min_x, thickness)
    
    avg_t = float(np.mean(list(times_dict.values()))) if times_dict else 0.0
    plt.title(f"Profiles (T) {title_extra} at t ≈ {avg_t:g} s\n{os.path.basename(folder)}\nThickness: {thickness:.2e} m")
    plt.grid(True, alpha=0.3)
    plt.legend(loc="best")
    plt.tight_layout()

    out_path = os.path.join(folder, out_filename)
    try:
        plt.savefig(out_path, dpi=200)
        print(f"  Saved: {out_path}")
    except Exception as e:
        print(f"  Error saving {out_path}: {e}")
    plt.close()

folders = sorted([p for p in glob.glob(PATTERN) if os.path.isdir(p)])
if not folders:
    print(f"No folders matching pattern: {PATTERN}")
    sys.exit(0)

for folder in folders:
    print(f"Processing folder: {folder}")
    # find mobile and trapped T files using the actual export names
    # Try both .h5 (HDF5) and .xdmf (XDMF) formats
    patterns = [
        os.path.join(folder, "mobile_concentration_t*.h5"),
        os.path.join(folder, "trapped_concentration_t*.h5"),
        os.path.join(folder, "mobile_concentration_t*.xdmf"),
        os.path.join(folder, "trapped_concentration_t*.xdmf"),
    ]
    matches = []
    for p in patterns:
        matches.extend([m for m in glob.glob(p) if os.path.isfile(m)])
    
    # Debug: show what files were actually found
    all_t_files = []
    for pattern in [os.path.join(folder, "mobile_concentration_t*"), os.path.join(folder, "trapped_concentration_t*")]:
        all_t_files.extend(glob.glob(pattern))
    if all_t_files and not matches:
        print(f"  Found T files but no .h5 files: {[os.path.basename(f) for f in all_t_files]}")
        print(f"  Looking for .h5 files specifically but found other formats. Skipping...")
    
    # sort for deterministic order (mobile first usually)
    t_files = sorted(matches)
    if not t_files:
        print(f"  No T concentration files (.h5 or .xdmf) found in {folder}; skipping")
        continue

    profiles = {}
    times = {}
    x_ref = None

    # New: store separate sets for t=72000 target and for last timestep
    profiles_target = {}
    times_target = {}
    profiles_last = {}
    times_last = {}

    for fpath in t_files:
        # Create a readable label from the filename, e.g. 'mobile_concentration_t' or 'trapped_concentration_t1'
        basename = os.path.splitext(os.path.basename(fpath))[0]
        # In case basename contains extensions like '.h5' removed above; keep full prefix
        label = basename
        
        # Determine file format and read accordingly
        if fpath.endswith('.xdmf'):
            coords, target_data, last_data = read_xdmf_file(fpath)
        elif fpath.endswith('.h5'):
            coords, target_data, last_data = read_h5_file(fpath)
        else:
            print(f"  Unsupported file format: {fpath}")
            continue
            
        if coords is None or target_data is None or last_data is None:
            continue
            
        conc_t, time_t = target_data
        conc_l, time_l = last_data

        # align to x_ref if needed and store both target and last profiles
        if x_ref is None:
            x_ref = np.asarray(coords)
            profiles_target[label] = np.asarray(conc_t)
            profiles_last[label] = np.asarray(conc_l)
        else:
            x_cur = np.asarray(coords)
            c_t_cur = np.asarray(conc_t)
            c_l_cur = np.asarray(conc_l)
            if (len(x_cur) != len(x_ref)) or np.max(np.abs(x_cur - x_ref)) > 1e-14:
                order = np.argsort(x_cur)
                profiles_target[label] = np.interp(x_ref, x_cur[order], c_t_cur[order])
                profiles_last[label] = np.interp(x_ref, x_cur[order], c_l_cur[order])
            else:
                profiles_target[label] = c_t_cur
                profiles_last[label] = c_l_cur

        times_target[label] = time_t
        times_last[label] = time_l

    if not profiles_target:
        print(f"  No valid profiles in {folder}; skipping")
        continue

    # Create plot for t ~ 72000 s
    _plot_profiles_loglog(x_ref, profiles_target, times_target, "profiles_t72000_T_loglog.png", "(closest to 72000 s)", folder)
    # Create plot for actual last timestep
    _plot_profiles_loglog(x_ref, profiles_last, times_last, "profiles_last_T_loglog.png", "(last timestep)", folder)

print("Done.")

"""
Check the structure of profile data to understand how it's stored.
"""

import json
import sys
import numpy as np

if len(sys.argv) < 2:
    print("Usage: python check_profile_structure.py <profiles_file.json>")
    sys.exit(1)

profiles_file = sys.argv[1]

# Load profile data
with open(profiles_file, 'r') as f:
    profiles = json.load(f)

# Get T profile
T_profile = profiles.get('T_profile')

if not T_profile:
    print("No T_profile found")
    sys.exit(1)

x = T_profile['x']
t = T_profile['t']
data = T_profile['data']

print("=" * 60)
print("Profile data structure:")
print("=" * 60)
print(f"Number of spatial points (x): {len(x)}")
print(f"Number of timesteps (t): {len(t)}")
print(f"Expected total entries: {len(x) * len(t)}")
print()
print(f"Type of 'data': {type(data)}")
print(f"Length of 'data' list: {len(data)}")
print()

# Check structure of data
if isinstance(data, list):
    if len(data) > 0:
        first_entry = data[0]
        print(f"Type of first entry: {type(first_entry)}")
        print(f"Length of first entry: {len(first_entry) if hasattr(first_entry, '__len__') else 'N/A'}")
        
        # Count total entries
        if isinstance(first_entry, list):
            total_entries = sum(len(entry) for entry in data)
            print(f"Total entries (summing all sub-lists): {total_entries}")
            print()
            print("Structure: List of lists (each sub-list is a profile at one time)")
            print(f"  data[0] = profile at t={t[0]:.2f}s (length: {len(data[0])})")
            print(f"  data[1] = profile at t={t[1]:.2f}s (length: {len(data[1])})")
            print(f"  ...")
            print(f"  data[{len(data)-1}] = profile at t={t[-1]:.2f}s (length: {len(data[-1])})")
        else:
            print(f"Total entries in flat data: {len(data)}")
            print()
            print("Structure: Flat list")
            
        print()
        print("Match check:")
        if isinstance(first_entry, list):
            if len(data) == len(t) and len(first_entry) == len(x):
                print(f"  ✓ data has {len(data)} entries (matches {len(t)} timesteps)")
                print(f"  ✓ Each entry has {len(first_entry)} values (matches {len(x)} spatial points)")
                print("  → Data structure: [timesteps][spatial_points]")
            else:
                print(f"  ✗ Dimension mismatch!")
                print(f"    data length: {len(data)} (expected: {len(t)})")
                print(f"    first entry length: {len(first_entry)} (expected: {len(x)})")
        else:
            if len(data) == len(x) * len(t):
                print(f"  ✓ Flat data has {len(data)} entries = {len(x)} × {len(t)}")
                print("  → Data is flattened and needs reshaping")
            else:
                print(f"  ✗ Flat data has {len(data)} entries ≠ {len(x)} × {len(t)} = {len(x) * len(t)}")

print("=" * 60)

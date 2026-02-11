"""
Mesh configuration for PFC-Tritium-Transport bins.

This file defines the user mesh parameters for each bin group.
The BINS_MESHES dictionary is generated from these parameters.
"""

import os
import numpy as np
from typing import Dict
from meshing import MeshBin


def graded_vertices(L, h0, r):
    """
    Generate graded mesh vertices from 0 to L.
    
    Args:
        L: Domain length (thickness)
        h0: Initial mesh spacing
        r: Mesh refinement ratio (> 1 for refinement towards x=0)
        
    Returns:
        numpy array of vertex positions
    """
    xs = [0.0]
    h = h0
    while xs[-1] + h < L:
        xs.append(xs[-1] + h)
        h *= r
    if xs[-1] < L:
        xs.append(L)
    return np.array(xs, dtype=float)


# Load reactor to get bin thicknesses
# Use INPUT_DIR_CONTEXT environment variable set by runner, or default to input_files/
input_dir = os.environ.get("INPUT_DIR_CONTEXT", "input_files")
csv_path = os.path.join(input_dir, "input_table.csv")
materials_path = os.path.join(input_dir, "materials.csv")

# Import here to ensure we pass materials_csv_path
from bins_from_csv.csv_bin_loader import CSVBinLoader
loader = CSVBinLoader(csv_path, materials_csv_path=materials_path)
reactor = loader.load_reactor()

# Generate BINS_MESHES - user defines mesh for each bin/group
BINS_MESHES: Dict[int, MeshBin] = {}

# Bins 1-50: h0=1e-10, r=1.05 (finer mesh for higher resolution)
#for bin in reactor.bins:
#    if 1 <= bin.bin_id <= 50:
#        mesh_array = graded_vertices(L=bin.thickness, h0=1e-10, r=1.05)
#        BINS_MESHES[bin.bin_id] = MeshBin(bin_id=bin.bin_id, mesh=mesh_array)

# Working for CV36ST_v1_2 with Analytical BC : h0=1e-8, r=1.02 (coarser mesh)
#for bin in reactor.bins:
#    if 1 <= bin.bin_id <= 94:
#        mesh_array = graded_vertices(L=bin.thickness, h0=1e-8, r=1.02)
#        BINS_MESHES[bin.bin_id] = MeshBin(bin_id=bin.bin_id, mesh=mesh_array)
#
#print(f"✓ Generated meshes for {len(BINS_MESHES)} bins")

for bin in reactor.bins:
    if 1 <= bin.bin_id <= 2 and bin.material.name == "W":
        mesh_array = graded_vertices(L=bin.thickness, h0=5e-10, r=1.03)
        BINS_MESHES[bin.bin_id] = MeshBin(bin_id=bin.bin_id, mesh=mesh_array)
print(f"✓ Generated meshes for {len(BINS_MESHES)} bins")
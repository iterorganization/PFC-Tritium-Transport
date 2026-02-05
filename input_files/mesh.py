"""
Mesh configuration for PFC-Tritium-Transport bins.

This file defines the user mesh parameters for each bin group.
The BINS_MESHES dictionary is generated from these parameters.
"""

import numpy as np
from typing import Dict
from meshing import MeshBin
from bins_from_csv.csv_bin_loader import load_csv_reactor


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
reactor = load_csv_reactor("input_files/input_table.csv")

# Generate BINS_MESHES - user defines mesh for each bin/group
BINS_MESHES: Dict[int, MeshBin] = {}

# Bins 1-50: h0=1e-10, r=1.05 (finer mesh for higher resolution)
for bin in reactor.bins:
    if 1 <= bin.bin_id <= 50:
        mesh_array = graded_vertices(L=bin.thickness, h0=1e-10, r=1.05)
        BINS_MESHES[bin.bin_id] = MeshBin(bin_id=bin.bin_id, mesh=mesh_array)

# Bins 51-94: h0=1e-8, r=1.02 (coarser mesh)
for bin in reactor.bins:
    if 51 <= bin.bin_id <= 94:
        mesh_array = graded_vertices(L=bin.thickness, h0=1e-8, r=1.02)
        BINS_MESHES[bin.bin_id] = MeshBin(bin_id=bin.bin_id, mesh=mesh_array)

print(f"✓ Generated meshes for {len(BINS_MESHES)} bins")

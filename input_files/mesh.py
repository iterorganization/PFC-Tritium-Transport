"""
Mesh configuration for PFC-Tritium-Transport bins.

This file defines the mesh parameters for each bin group and generates
the BINS_MESHES dictionary used by hisp simulations.
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


def _generate_bins_meshes() -> Dict[int, MeshBin]:
    """
    Generate mesh for all bins from reactor.
    
    Mesh parameters:
    - Bins 1-50: h0=1e-10, r=1.05 (finer mesh)
    - Bins 51-94: h0=1e-8, r=1.02 (coarser mesh)
    
    Returns:
        Dictionary of MeshBin objects keyed by bin_id
    """
    try:
        reactor = load_csv_reactor("input_files/input_table.csv")
    except FileNotFoundError:
        print("Warning: Could not load reactor CSV. BINS_MESHES will be empty.")
        print("Make sure to run from the PFC-Tritium-Transport directory.")
        return {}
    
    bins_meshes = {}
    
    # Bins 1-50: h0=1e-10, r=1.05 (finer mesh for higher resolution)
    for bin in reactor.bins:
        if 1 <= bin.bin_id <= 50:
            mesh_array = graded_vertices(L=bin.thickness, h0=1e-10, r=1.05)
            bins_meshes[bin.bin_id] = MeshBin(bin_id=bin.bin_id, mesh=mesh_array)
    
    # Bins 51-94: h0=1e-8, r=1.02 (coarser mesh)
    for bin in reactor.bins:
        if 51 <= bin.bin_id <= 94:
            mesh_array = graded_vertices(L=bin.thickness, h0=1e-8, r=1.02)
            bins_meshes[bin.bin_id] = MeshBin(bin_id=bin.bin_id, mesh=mesh_array)
    
    if bins_meshes:
        print(f"✓ Generated meshes for {len(bins_meshes)} bins")
    
    return bins_meshes


# Generate BINS_MESHES on module import
BINS_MESHES: Dict[int, MeshBin] = _generate_bins_meshes()

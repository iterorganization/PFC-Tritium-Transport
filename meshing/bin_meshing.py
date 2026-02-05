import numpy as np
from typing import Union, Dict
from bins_from_csv.csv_bin import Bin, Reactor, BinCollection


def graded_vertices(L, h0, r):
    """Generate graded mesh vertices from 0 to L."""
    xs = [0.0]
    h = h0
    while xs[-1] + h < L:
        xs.append(xs[-1] + h)
        h *= r
    if xs[-1] < L:
        xs.append(L)
    return np.array(xs, dtype=float)


class MeshBin:
    """Container linking a bin_id to its mesh array."""
    def __init__(self, bin_id: int, mesh: np.ndarray):
        """
        Initialize with bin_id and mesh array.
        
        Args:
            bin_id: ID of the bin
            mesh: Array of mesh vertices
        """
        self.bin_id = bin_id
        self.mesh = mesh
    
    def __repr__(self):
        return f"MeshBin(bin_id={self.bin_id}, nodes={len(self.mesh)})"


# --- Generate BINS_MESHES for all bins ---
# Load reactor from CSV when module is imported
def _generate_bins_meshes() -> Dict[int, MeshBin]:
    """Generate mesh for all bins from reactor."""
    from bins_from_csv.csv_bin_loader import load_csv_reactor
    
    try:
        reactor = load_csv_reactor("input_files/input_table.csv")
    except FileNotFoundError:
        print("Warning: Could not load reactor CSV. BINS_MESHES will be empty.")
        print("Make sure to run this script from the PFC-Tritium-Transport directory.")
        return {}
    
    bins_meshes = {}
    
    # Bins 1-50: h0=1e-10, r=1.05
    for bin in reactor.bins:
        if 1 <= bin.bin_id <= 50:
            mesh_array = graded_vertices(L=bin.thickness, h0=1e-10, r=1.05)
            bins_meshes[bin.bin_id] = MeshBin(bin_id=bin.bin_id, mesh=mesh_array)
    
    # Bins 51-94: h0=1e-8, r=1.02
    for bin in reactor.bins:
        if 51 <= bin.bin_id <= 94:
            mesh_array = graded_vertices(L=bin.thickness, h0=1e-8, r=1.02)
            bins_meshes[bin.bin_id] = MeshBin(bin_id=bin.bin_id, mesh=mesh_array)
    
    if bins_meshes:
        print(f"✓ Generated meshes for {len(bins_meshes)} bins")
    
    return bins_meshes


# Execute mesh generation on module import
BINS_MESHES: Dict[int, MeshBin] = _generate_bins_meshes()

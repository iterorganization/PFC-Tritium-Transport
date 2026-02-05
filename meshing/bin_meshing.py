import numpy as np
from typing import Dict


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


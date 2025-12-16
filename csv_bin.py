"""
CSV-driven bin classes for HISP reactor modeling.
Each bin represents one row from the CSV configuration table.
"""

from typing import Optional
from dataclasses import dataclass


@dataclass
class BinConfiguration:
    """Configuration parameters for HISP simulation."""
    rtol: float
    atol: float
    fp_max_stepsize: float  # FP max. stepsize (s)
    max_stepsize_no_fp: float  # Max. stepsize no FP (s)
    bc_plasma_facing_surface: str  # BC Plasma Facing Surface
    bc_rear_surface: str  # BC rear surface
    
    def __post_init__(self):
        """Validate configuration parameters."""
        if self.rtol <= 0:
            raise ValueError(f"rtol must be positive, got {self.rtol}")
        if self.atol <= 0:
            raise ValueError(f"atol must be positive, got {self.atol}")
        if self.fp_max_stepsize <= 0:
            raise ValueError(f"fp_max_stepsize must be positive, got {self.fp_max_stepsize}")
        if self.max_stepsize_no_fp <= 0:
            raise ValueError(f"max_stepsize_no_fp must be positive, got {self.max_stepsize_no_fp}")


class Bin:
    """
    A bin class representing one row from the CSV configuration table.
    Each bin contains all geometric, material, and simulation properties.
    """
    
    def __init__(
        self,
        bin_number: int,
        z_start: float,
        r_start: float, 
        z_end: float,
        r_end: float,
        material: str,
        thickness: float,
        cu_thickness: float,
        mode: str,
        parent_bin_surf_area: float,
        surface_area: float,
        f_ion_flux_fraction: float,
        location: str,
        coolant_temp: float = 343.0,
        bin_configuration: Optional[BinConfiguration] = None,
        bin_id: Optional[int] = None
    ):
        """
        Initialize a CSV-based bin.
        
        Args:
            bin_number: Bin number from CSV
            z_start: Z coordinate start position (m)
            r_start: R coordinate start position (m)
            z_end: Z coordinate end position (m)
            r_end: R coordinate end position (m)
            material: Material type (W, B, SS, etc.)
            thickness: Bin thickness (m)
            cu_thickness: Copper thickness (m)
            mode: Operating mode (hw, lw, shadowed, wetted, etc.)
            parent_bin_surf_area: Surface area of parent bin (m^2)
            surface_area: Surface area of this specific bin/mode (m^2)
            f_ion_flux_fraction: Ion flux fraction
            location: Location identifier (FW, DIV, etc.)
            coolant_temp: Coolant temperature (K)
            bin_configuration: BinConfiguration object with simulation parameters
            bin_id: Row number from CSV table (optional)
            
        Calculated Properties:
            ion_scaling_factor: Calculated as f_ion_flux_fraction * parent_bin_surf_area / surface_area
        """
        # Geometric properties
        self.bin_number = bin_number
        self.z_start = z_start
        self.r_start = r_start
        self.z_end = z_end
        self.r_end = r_end
        
        # Material properties
        self.material = material
        self.thickness = thickness
        self.cu_thickness = cu_thickness
        
        # Operating properties
        self.mode = mode
        self.parent_bin_surf_area = parent_bin_surf_area
        self.surface_area = surface_area
        self.f_ion_flux_fraction = f_ion_flux_fraction
        self.location = location
        self.coolant_temp = coolant_temp
        
        # CSV row identifier
        self.bin_id = bin_id if bin_id is not None else bin_number
        
        # Calculate ion scaling factor
        self.ion_scaling_factor = self.f_ion_flux_fraction * self.parent_bin_surf_area / self.surface_area
        
        # Simulation configuration (use provided or create default)
        self.bin_configuration = bin_configuration if bin_configuration is not None else BinConfiguration(
            rtol=1e-10,
            atol=1e10,
            fp_max_stepsize=5.0,
            max_stepsize_no_fp=100.0,
            bc_plasma_facing_surface="Robin - Surf. Rec. + Implantation",
            bc_rear_surface="Neumann - no flux"
        )
    
    @property
    def copper_thickness(self) -> float:
        """Compatibility property for HISP temperature functions."""
        return self.cu_thickness
    
    @property
    def start_point(self) -> tuple[float, float]:
        """Get start point as (Z, R) tuple."""
        return (self.z_start, self.r_start)
    
    @property
    def end_point(self) -> tuple[float, float]:
        """Get end point as (Z, R) tuple."""
        return (self.z_end, self.r_end)
    
    @property
    def length(self) -> float:
        """Calculate the poloidal length of the bin (m)."""
        return (
            (self.z_end - self.z_start) ** 2 + 
            (self.r_end - self.r_start) ** 2
        ) ** 0.5
    
    @property
    def is_first_wall(self) -> bool:
        """Check if this is a first wall bin."""
        return self.location.upper() == "FW"
    
    @property
    def is_divertor(self) -> bool:
        """Check if this is a divertor bin."""
        return self.location.upper() in ["DIV", "DIVERTOR"]
    
    @property
    def is_shadowed(self) -> bool:
        """Check if this bin is in shadowed mode."""
        return self.mode.lower() in ["shadowed", "shadow"]
    
    @property
    def is_wetted(self) -> bool:
        """Check if this bin is in any wetted mode."""
        return self.mode.lower() in ["wetted", "wet", "hw", "lw", "high_wetted", "low_wetted"]
    
    def __str__(self) -> str:
        """String representation of the bin."""
        return (
            f"Bin(id={self.bin_id}, bin_num={self.bin_number}, "
            f"material={self.material}, mode={self.mode}, "
            f"location={self.location}, thickness={self.thickness*1000:.1f}mm)"
        )
    
    def __repr__(self) -> str:
        """Detailed representation of the bin."""
        return self.__str__()


class BinCollection:
    """Collection of CSV-based bins."""
    
    def __init__(self, bins: list[Bin] = None):
        """Initialize collection with list of Bin objects."""
        self.bins = bins if bins is not None else []
    
    def add_bin(self, bin: Bin):
        """Add a bin to the collection."""
        self.bins.append(bin)
    
    def get_bin_by_id(self, bin_id: int) -> Bin:
        """Get bin by its CSV row ID."""
        for bin in self.bins:
            if bin.bin_id == bin_id:
                return bin
        raise ValueError(f"No bin found with ID {bin_id}")
    
    def get_bin_by_number(self, bin_number: int) -> Bin:
        """Get bin by its bin number."""
        for bin in self.bins:
            if bin.bin_number == bin_number:
                return bin
        raise ValueError(f"No bin found with number {bin_number}")
    
    def get_bins_by_material(self, material: str) -> list[Bin]:
        """Get all bins with specified material."""
        return [bin for bin in self.bins if bin.material.upper() == material.upper()]
    
    def get_bins_by_location(self, location: str) -> list[Bin]:
        """Get all bins at specified location (FW, DIV, etc.)."""
        return [bin for bin in self.bins if bin.location.upper() == location.upper()]
    
    def get_bins_by_mode(self, mode: str) -> list[Bin]:
        """Get all bins with specified mode."""
        return [bin for bin in self.bins if bin.mode.lower() == mode.lower()]
    
    @property
    def first_wall_bins(self) -> list[Bin]:
        """Get all first wall bins."""
        return [bin for bin in self.bins if bin.is_first_wall]
    
    @property
    def divertor_bins(self) -> list[Bin]:
        """Get all divertor bins."""
        return [bin for bin in self.bins if bin.is_divertor]
    
    def __len__(self) -> int:
        """Return number of bins in collection."""
        return len(self.bins)
    
    def __iter__(self):
        """Make collection iterable."""
        return iter(self.bins)
    
    def __str__(self) -> str:
        """String representation of the collection."""
        fw_count = len(self.first_wall_bins)
        div_count = len(self.divertor_bins)
        return f"BinCollection({len(self.bins)} bins: {fw_count} FW, {div_count} DIV)"


class Reactor(BinCollection):
    """
    A reactor representing the complete collection of all bins from a CSV table.
    This is the main class for representing the entire ITER reactor configuration.
    """
    
    def __init__(self, bins: list[Bin] = None, csv_path: str = None):
        """
        Initialize reactor with list of CSVBin objects.
        
        Args:
            bins: List of Bin objects representing all reactor bins
            csv_path: Optional path to the source CSV file for reference
        """
        super().__init__(bins)
        self.csv_path = csv_path
    
    @classmethod
    def from_csv(cls, csv_path: str) -> 'Reactor':
        """
        Create a complete reactor by loading all bins from a CSV table.
        
        Args:
            csv_path: Path to the CSV configuration file
            
        Returns:
            Reactor: Complete reactor with all bins from the CSV table
        """
        # Import here to avoid circular imports
        from csv_bin_loader import CSVBinLoader
        
        loader = CSVBinLoader(csv_path)
        bins = loader.load_all_bins()
        return cls(bins=bins, csv_path=csv_path)
    
    @property
    def total_bins(self) -> int:
        """Get total number of bins in the reactor."""
        return len(self.bins)
    
    @property
    def materials_summary(self) -> dict[str, int]:
        """Get summary of materials used in the reactor."""
        materials = {}
        for bin in self.bins:
            material = bin.material.upper()
            materials[material] = materials.get(material, 0) + 1
        return materials
    
    @property
    def locations_summary(self) -> dict[str, int]:
        """Get summary of bin locations in the reactor."""
        locations = {}
        for bin in self.bins:
            location = bin.location.upper()
            locations[location] = locations.get(location, 0) + 1
        return locations
    
    def get_reactor_summary(self) -> str:
        """Get comprehensive summary of the reactor configuration."""
        summary = [
            f"Reactor Summary:",
            f"  Total bins: {self.total_bins}",
            f"  CSV source: {self.csv_path or 'Not specified'}",
            f"  First Wall bins: {len(self.first_wall_bins)}",
            f"  Divertor bins: {len(self.divertor_bins)}",
            f"  Materials: {self.materials_summary}",
            f"  Locations: {self.locations_summary}"
        ]
        return "\n".join(summary)
    
    def __str__(self) -> str:
        """String representation of the reactor."""
        return f"Reactor({self.total_bins} total bins: {len(self.first_wall_bins)} FW, {len(self.divertor_bins)} DIV)"

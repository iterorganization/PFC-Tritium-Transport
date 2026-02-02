"""
CSV loader for creating Bin objects from CSV configuration files.
"""

import pandas as pd
from typing import List, Dict, Any, Optional
from pathlib import Path
from bins_from_csv.csv_bin import Bin, BinCollection, Reactor, BinConfiguration
from materials.materials_loader import load_materials


class CSVBinLoader:
    """Loads Bin objects from CSV configuration files."""
    
    def __init__(self, csv_path: str, materials_csv_path: Optional[str] = None):
        """
        Initialize loader with CSV file path.
        
        Args:
            csv_path: Path to the CSV configuration file
        """
        self.csv_path = csv_path
        # Allow caller to pass either the direct path or the filename located in input_files/
        try:
            self.df = pd.read_csv(csv_path)
        except FileNotFoundError:
            # try under input_files/ for convenience
            alt = Path("input_files") / csv_path
            try:
                self.df = pd.read_csv(alt)
                self.csv_path = str(alt)
            except FileNotFoundError:
                # re-raise original error with more context
                raise FileNotFoundError(f"CSV file not found at '{csv_path}' or '{alt}'")
        self._validate_csv()
        # Load materials CSV if available (default: input_files/materials.csv)
        if materials_csv_path is None:
            materials_csv_path = Path("input_files/materials.csv")
        try:
            self.materials = load_materials(materials_csv_path)
            print(f"✓ Loaded {len(self.materials)} materials from {materials_csv_path}")
        except Exception as e:
            raise RuntimeError(f"Failed to load materials from {materials_csv_path}: {e}")
    
    def _validate_csv(self):
        """Validate that CSV has required columns."""
        required_columns = [
            'Bin number', 'Z_start (m)', 'R_start (m)', 'Z_end (m)', 'R_end (m)',
            'Material', 'Thickness (m)', 'Cu thickness (m)', 'mode',
            'S. Area parent bin (m^2)', 'Surface area (m^2)', 'f (ion flux scaling factor)', 'location'
        ]
        
        missing_columns = [col for col in required_columns if col not in self.df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns in CSV: {missing_columns}")
        
        print(f"✓ CSV validation passed. Found {len(self.df)} rows with {len(self.df.columns)} columns.")
    
    def _get_column_value(self, row: pd.Series, column: str, default: Any = None) -> Any:
        """Safely get column value with fallback to default."""
        if column in self.df.columns:
            value = row[column]
            # Handle NaN values
            if pd.isna(value):
                return default
            return value
        return default
    
    def load_bin_from_row(self, row: pd.Series, row_index: int) -> Bin:
        """
        Create a Bin from a pandas DataFrame row.
        
        Args:
            row: Pandas Series representing one row from the CSV
            row_index: Index of the row (0-based)
            
        Returns:
            Bin object
        """
        # Required geometric properties
        bin_number = int(row['Bin number'])
        z_start = float(row['Z_start (m)'])
        r_start = float(row['R_start (m)'])
        z_end = float(row['Z_end (m)'])
        r_end = float(row['R_end (m)'])
        
        # Required material properties
        material = str(row['Material'])
        thickness = float(row['Thickness (m)'])
        cu_thickness = float(row['Cu thickness (m)'])

        # find matching Material object (case-insensitive). If no match,
        # raise an error — CSV values must match `materials.csv`.
        mat_obj = None
        mat_name = material.strip()
        if hasattr(self, 'materials') and self.materials:
            mat_obj = self.materials.get(mat_name)
            if mat_obj is None:
                for k, v in self.materials.items():
                    if k.lower() == mat_name.lower():
                        mat_obj = v
                        break
        if mat_obj is None:
            available = ', '.join(sorted(self.materials.keys()))
            raise ValueError(
                f"Unknown material '{material}' in CSV row {row_index + 1}. "
                f"Available materials: {available}"
            )
        
        # Required operating properties
        mode = str(row['mode'])
        parent_bin_surf_area = float(row['S. Area parent bin (m^2)'])
        surface_area = float(row['Surface area (m^2)'])
        f_ion_flux_fraction = float(row['f (ion flux scaling factor)'])
        location = str(row['location'])
        
        # Optional properties with defaults
        coolant_temp = self._get_column_value(row, 'Coolant Temp. (K)', 343.0)
        if coolant_temp is not None:
            coolant_temp = float(coolant_temp)
        else:
            coolant_temp = 343.0
        
        # Simulation configuration with defaults
        rtol = float(self._get_column_value(row, 'rtol', 1e-10))
        atol = float(self._get_column_value(row, 'atol', 1e10))
        fp_max_stepsize = float(self._get_column_value(row, 'FP max. stepsize (s)', 5.0))
        max_stepsize_no_fp = float(self._get_column_value(row, 'Max. stepsize no FP (s)', 100.0))
        
        # Boundary conditions with defaults
        bc_plasma_facing = self._get_column_value(row, 'BC Plasma Facing Surface', 'Robin - Surf. Rec. + Implantation')
        bc_rear = self._get_column_value(row, 'BC rear surface', 'Neumann - no flux')
        
        # Implantation parameters calculation flag (default: True to calculate from flux data)
        calc_implant_str = self._get_column_value(row, 'Calculate Implantation Parameters', 'Yes')
        calculate_implantation_params = str(calc_implant_str).lower().strip() != 'no'
        
        # Create bin configuration
        bin_config = BinConfiguration(
            rtol=rtol,
            atol=atol,
            fp_max_stepsize=fp_max_stepsize,
            max_stepsize_no_fp=max_stepsize_no_fp,
            bc_plasma_facing_surface=bc_plasma_facing,
            bc_rear_surface=bc_rear
        )
        
        # Create Bin instance; `mat_obj` is guaranteed non-None here.
        bin_obj = Bin(
            bin_number=bin_number,
            z_start=z_start,
            r_start=r_start,
            z_end=z_end,
            r_end=r_end,
            material=mat_obj,
            thickness=thickness,
            cu_thickness=cu_thickness,
            mode=mode,
            parent_bin_surf_area=parent_bin_surf_area,
            surface_area=surface_area,
            f_ion_flux_fraction=f_ion_flux_fraction,
            location=location,
            coolant_temp=coolant_temp,
            bin_configuration=bin_config,
            bin_id=row_index + 1,  # 1-based row numbering
            calculate_implantation_params=calculate_implantation_params,
        )
        # material already stored on the bin by its constructor; nothing more to do

        return bin_obj
    
    def load_all_bins(self) -> BinCollection:
        """
        Load all bins from the CSV file.
        
        Returns:
            BinCollection containing all bins
        """
        bins = []
        
        for row_index, row in self.df.iterrows():
            bin_obj = self.load_bin_from_row(row, row_index)
            bins.append(bin_obj)
        print(f"✓ Successfully loaded {len(bins)} bins from CSV")
        return BinCollection(bins)
    
    def load_reactor(self) -> Reactor:
        """
        Load a complete reactor from the CSV file.
        
        Returns:
            Reactor containing all bins
        """
        bin_collection = self.load_all_bins()
        return Reactor(bin_collection.bins)
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics of the CSV data.
        
        Returns:
            Dictionary with summary information
        """
        summary = {
            'total_rows': len(self.df),
            'unique_bin_numbers': len(self.df['Bin number'].unique()),
            'materials': self.df['Material'].value_counts().to_dict(),
            'locations': self.df['location'].value_counts().to_dict(),
            'modes': self.df['mode'].value_counts().to_dict(),
        }
        
        return summary
    
    def print_summary(self):
        """Print summary statistics of the CSV data."""
        summary = self.get_summary()
        
        print("\n=== CSV Data Summary ===")
        print(f"Total rows: {summary['total_rows']}")
        print(f"Unique bin numbers: {summary['unique_bin_numbers']}")
        
        print("\nMaterials:")
        for material, count in summary['materials'].items():
            print(f"  {material}: {count}")
        
        print("\nLocations:")
        for location, count in summary['locations'].items():
            print(f"  {location}: {count}")
        
        print("\nModes:")
        for mode, count in summary['modes'].items():
            print(f"  {mode}: {count}")


def load_csv_reactor(csv_path: str) -> Reactor:
    """
    Convenience function to load a reactor from CSV file.
    
    Args:
        csv_path: Path to the CSV configuration file
        
    Returns:
        Reactor object
    """
    loader = CSVBinLoader(csv_path)
    return loader.load_reactor()


# Example usage function
def example_usage():
    """Example of how to use the CSV bin loader."""
    
    # Load reactor from CSV
    csv_path = "input_files/input_table.csv"
    
    try:
        # Create loader and load reactor
        loader = CSVBinLoader(csv_path)
        loader.print_summary()
        
        reactor = loader.load_reactor()
        
        print(f"\n✓ Created {reactor}")
        print(f"  First wall bins: {len(reactor.first_wall_bins)}")
        print(f"  Divertor bins: {len(reactor.divertor_bins)}")
        
        # Example bin access
        if len(reactor.bins) > 0:
            example_bin = reactor.bins.bins[0]
            print(f"\nExample bin: {example_bin}")
            print(f"  Configuration: rtol={example_bin.configuration.rtol}")
            print(f"  Geometry: {example_bin.start_point} -> {example_bin.end_point}")
            print(f"  Length: {example_bin.length:.3f} m")
        
    except Exception as e:
        print(f"Error loading CSV reactor: {e}")


if __name__ == "__main__":
    example_usage()

"""
CSV loader for creating CSVBin objects from CSV configuration files.
"""

import pandas as pd
from typing import List, Dict, Any
from csv_bin import CSVBin, CSVBinCollection, CSVReactor, BinConfiguration


class CSVBinLoader:
    """Loads CSVBin objects from CSV configuration files."""
    
    def __init__(self, csv_path: str):
        """
        Initialize loader with CSV file path.
        
        Args:
            csv_path: Path to the CSV configuration file
        """
        self.csv_path = csv_path
        self.df = pd.read_csv(csv_path)
        self._validate_csv()
    
    def _validate_csv(self):
        """Validate that CSV has required columns."""
        required_columns = [
            'Bin number', 'Z_start (m)', 'R_start (m)', 'Z_end (m)', 'R_end (m)',
            'Material', 'Thickness (m)', 'Cu thickness (m)', 'mode',
            'S. Area parent bin (m^2)', 'Surface area (m^2)', 'f (ion flux fraction)', 'location'
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
    
    def load_bin_from_row(self, row: pd.Series, row_index: int) -> CSVBin:
        """
        Create a CSVBin from a pandas DataFrame row.
        
        Args:
            row: Pandas Series representing one row from the CSV
            row_index: Index of the row (0-based)
            
        Returns:
            CSVBin object
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
        
        # Required operating properties
        mode = str(row['mode'])
        parent_bin_surf_area = float(row['S. Area parent bin (m^2)'])
        surface_area = float(row['Surface area (m^2)'])
        f_ion_flux_fraction = float(row['f (ion flux fraction)'])
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
        
        # Create bin configuration
        bin_config = BinConfiguration(
            rtol=rtol,
            atol=atol,
            fp_max_stepsize=fp_max_stepsize,
            max_stepsize_no_fp=max_stepsize_no_fp,
            bc_plasma_facing_surface=bc_plasma_facing,
            bc_rear_surface=bc_rear
        )
        
        # Create and return CSVBin
        return CSVBin(
            bin_number=bin_number,
            z_start=z_start,
            r_start=r_start,
            z_end=z_end,
            r_end=r_end,
            material=material,
            thickness=thickness,
            cu_thickness=cu_thickness,
            mode=mode,
            parent_bin_surf_area=parent_bin_surf_area,
            surface_area=surface_area,
            f_ion_flux_fraction=f_ion_flux_fraction,
            location=location,
            coolant_temp=coolant_temp,
            bin_configuration=bin_config,
            bin_id=row_index + 1  # 1-based row numbering
        )
    
    def load_all_bins(self) -> CSVBinCollection:
        """
        Load all bins from the CSV file.
        
        Returns:
            CSVBinCollection containing all bins
        """
        bins = []
        
        for row_index, row in self.df.iterrows():
            try:
                bin_obj = self.load_bin_from_row(row, row_index)
                bins.append(bin_obj)
            except Exception as e:
                print(f"Warning: Failed to load row {row_index + 1}: {e}")
                continue
        
        print(f"✓ Successfully loaded {len(bins)} bins from CSV")
        return CSVBinCollection(bins)
    
    def load_reactor(self) -> CSVReactor:
        """
        Load a complete reactor from the CSV file.
        
        Returns:
            CSVReactor containing all bins
        """
        bin_collection = self.load_all_bins()
        return CSVReactor(bin_collection.bins)
    
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


def load_csv_reactor(csv_path: str) -> CSVReactor:
    """
    Convenience function to load a reactor from CSV file.
    
    Args:
        csv_path: Path to the CSV configuration file
        
    Returns:
        CSVReactor object
    """
    loader = CSVBinLoader(csv_path)
    return loader.load_reactor()


# Example usage function
def example_usage():
    """Example of how to use the CSV bin loader."""
    
    # Load reactor from CSV
    csv_path = "input_table.csv"
    
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

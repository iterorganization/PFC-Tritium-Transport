#!/usr/bin/env python3
"""
Extract bin configuration (number, mode, material, thickness) from make_iter_bins.py
and save as CSV file.
"""
import pandas as pd
import sys
import os

# Add current directory to path to import make_iter_bins
sys.path.insert(0, '.')

# Import the bin configuration from the same location as the wall bins job
from iter_bins.make_iter_bins import FW_bins, Div_bins

def extract_bin_config():
    """Extract bin configuration data into a list of dictionaries."""
    config_data = []
    
    # Extract First Wall bins
    for fw_bin in FW_bins.bins:
        for subbin in fw_bin.sub_bins:
            config_data.append({
                'bin_number': fw_bin.index,
                'bin_type': 'FW',
                'mode': subbin.mode,
                'material': subbin.material,
                'thickness_m': subbin.thickness,
                'thickness_mm': subbin.thickness * 1000 if subbin.thickness >= 1e-6 else subbin.thickness * 1e9,  # mm for thick, nm for thin
                'thickness_unit': 'mm' if subbin.thickness >= 1e-6 else 'nm',
                'copper_thickness_m': getattr(subbin, 'copper_thickness', None),
                'copper_thickness_mm': getattr(subbin, 'copper_thickness', 0) * 1000 if hasattr(subbin, 'copper_thickness') and subbin.copper_thickness else None,
            })
    
    # Extract Divertor bins
    for div_bin in Div_bins.bins:
        config_data.append({
            'bin_number': div_bin.index,
            'bin_type': 'DIV',
            'mode': div_bin.mode,
            'material': div_bin.material,
            'thickness_m': div_bin.thickness,
            'thickness_mm': div_bin.thickness * 1000 if div_bin.thickness >= 1e-6 else div_bin.thickness * 1e9,  # mm for thick, nm for thin
            'thickness_unit': 'mm' if div_bin.thickness >= 1e-6 else 'nm',
            'copper_thickness_m': getattr(div_bin, 'copper_thickness', None),
            'copper_thickness_mm': getattr(div_bin, 'copper_thickness', 0) * 1000 if hasattr(div_bin, 'copper_thickness') and div_bin.copper_thickness else None,
        })
    
    return config_data

def main():
    print("Extracting bin configuration...")
    
    # Extract the data
    config_data = extract_bin_config()
    
    # Create DataFrame
    df = pd.DataFrame(config_data)
    
    # Sort by bin number
    df = df.sort_values('bin_number')
    
    # Round thickness values for readability
    df['thickness_m'] = df['thickness_m'].round(9)  # Round to nm precision
    df['thickness_mm'] = df['thickness_mm'].round(3)  # Round to 3 decimal places
    df['copper_thickness_m'] = df['copper_thickness_m'].round(6)  # Round to μm precision
    df['copper_thickness_mm'] = df['copper_thickness_mm'].round(3)  # Round to 3 decimal places
    
    # Save to CSV
    output_file = 'bin_configuration.csv'
    df.to_csv(output_file, index=False)
    
    print(f"Saved bin configuration to: {output_file}")
    print(f"Total bins: {len(df)}")
    print(f"First Wall bins: {len(df[df['bin_type'] == 'FW'])}")
    print(f"Divertor bins: {len(df[df['bin_type'] == 'DIV'])}")
    
    # Print summary statistics
    print("\nMaterial distribution:")
    print(df['material'].value_counts())
    
    print("\nThickness ranges by material:")
    for material in df['material'].unique():
        material_data = df[df['material'] == material]
        print(f"  {material}: {material_data['thickness_m'].min():.2e} - {material_data['thickness_m'].max():.2e} m")
    
    print(f"\nFirst few rows of the configuration:")
    print(df.head(10).to_string(index=False))
    
    print(f"\nSample of different materials:")
    for material in df['material'].unique():
        sample = df[df['material'] == material].head(2)
        print(f"\n{material} samples:")
        print(sample[['bin_number', 'mode', 'thickness_m', 'thickness_unit']].to_string(index=False))

if __name__ == "__main__":
    main()

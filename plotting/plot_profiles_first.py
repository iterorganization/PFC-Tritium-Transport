#!/usr/bin/env python3
"""
Plot 1D T concentration profiles (mobile and trapped) from simulation results.
This version plots the FIRST timestep.
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import sys
import os


def plot_T_profiles(profiles_file, output_file=None):
    """
    Plot mobile and trapped T concentration profiles from JSON file.
    Plots the first timestep.
    """
    
    # Load profiles from JSON
    with open(profiles_file, 'r') as f:
        data = json.load(f)
    
    # Extract T mobile profile
    if 'T_profile' not in data:
        print(f"Error: 'T_profile' not found in {profiles_file}")
        print(f"Available profiles: {list(data.keys())}")
        return
    
    T_mobile = data['T_profile']
    x = np.array(T_mobile['x'])
    t = np.array(T_mobile['t'])
    
    print(f"Available profiles in file: {list(data.keys())}")
    
    # Extract trapped T profiles
    trap_profiles = {}
    for key in data.keys():
        if 'trap' in key and 'T_profile' in key:
            trap_profiles[key] = data[key]
    
    print(f"Found {len(trap_profiles)} trap profiles: {list(trap_profiles.keys())}")
    
    # Get indices for first and last timesteps
    idx_first = 0
    idx_last = len(t) - 1
    
    # Handle potential data structure issues
    mobile_first_raw = T_mobile['data'][idx_first]
    
    # Check if data needs reshaping
    if isinstance(mobile_first_raw, list):
        mobile_first_raw = np.array(mobile_first_raw)
    
    if len(mobile_first_raw.shape) > 1:
        # Data might be 2D, flatten it
        mobile_first = mobile_first_raw.flatten()
    else:
        mobile_first = mobile_first_raw
    
    # Check data consistency
    if len(mobile_first) != len(x):
        print(f"Warning: Data length {len(mobile_first)} != x length {len(x)}")
        print(f"  Attempting to handle data structure issue...")
        
        # Check if data is stored in a different format
        all_mobile_data = np.array(T_mobile['data'])
        print(f"  Full data shape: {all_mobile_data.shape}")
        
        if len(mobile_first) == len(x) * len(t):
            print("  Detected flattened data - attempting to reshape...")
            # Data is flattened, reshape it
            all_data = np.array(T_mobile['data']).flatten()
            n_times = len(t)
            n_x = len(x)
            
            # Reshape and extract first/last
            reshaped = all_data.reshape(n_times, n_x)
            mobile_first = reshaped[0, :]
            mobile_last = reshaped[-1, :]
        else:
            print("  Cannot determine data structure - aborting")
            return
    
    print(f"Plotting profiles at:")
    print(f"  First timestep: t = {t[idx_first]:.2f} s")
    print(f"  Last timestep:  t = {t[idx_last]:.2f} s")
    print(f"  Total timesteps: {len(t)}")
    print(f"  Spatial points: {len(x)}")
    
    # Use first timestep
    idx_plot = idx_first
    
    # Create figure with two y-axes
    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax2 = ax1.twinx()
    
    # Colors
    color_mobile = 'tab:blue'
    color_traps = 'tab:red'
    
    # Plot mobile T on left axis
    mobile_plot = np.array(T_mobile['data'][idx_plot])
    
    # Check for negative/zero values
    print(f"\nMobile T concentration statistics:")
    print(f"  Plotting timestep: min={np.min(mobile_plot):.2e}, max={np.max(mobile_plot):.2e}")
    print(f"  Negative values: {np.sum(mobile_plot < 0)}/{len(mobile_plot)}")
    print(f"  Zero values: {np.sum(mobile_plot == 0)}/{len(mobile_plot)}")
    
    ax1.plot(x * 1e3, mobile_plot, color=color_mobile, linestyle='-', 
             label=f'Mobile T (t={t[idx_plot]:.1f}s)', linewidth=2)
    
    ax1.set_xlabel('Depth (mm)', fontsize=12)
    ax1.set_ylabel('Mobile T concentration (m⁻³)', color=color_mobile, fontsize=12)
    ax1.tick_params(axis='y', labelcolor=color_mobile)
    ax1.set_xlim(0, 0.01)
    ax1.grid(True, which='both', alpha=0.3)
    
    # Add minor ticks on left axis (will be adjusted if right axis exists)
    ax1.minorticks_on()
    ax1.tick_params(which='minor', length=3, color='gray')
    
    # Plot trapped T on right axis
    if trap_profiles:
        # Sum all trap contributions (for the selected timestep)
        total_trapped_plot = np.zeros_like(mobile_plot)
        
        for trap_name, trap_data in trap_profiles.items():
            # Get trap times (should match mobile T times)
            trap_t = np.array(trap_data['t'])
            trap_data_plot = np.array(trap_data['data'][idx_plot])
            
            # Handle dimension mismatch for traps too
            if len(trap_data_plot) != len(x):
                print(f"  {trap_name}: data length {len(trap_data_plot)} != x length {len(x)}")
                
                # Check if entire data array needs reshaping
                all_trap_data = np.array(trap_data['data'])
                print(f"  {trap_name}: data array shape = {all_trap_data.shape}")
                
                total_entries = all_trap_data.size
                expected = len(x) * len(trap_t)
                
                print(f"  {trap_name}: total entries = {total_entries}, expected = {expected}")
                print(f"  {trap_name}: ratio = {total_entries / expected:.4f}")
                
                # The data array is (n_times, 2*n_x) - each timestep has duplicate spatial points
                # Check if spatial dimension is approximately 2x what we expect
                spatial_ratio = len(trap_data_plot) / len(x)
                print(f"  {trap_name}: spatial ratio = {spatial_ratio:.4f}")
                
                if 1.95 < spatial_ratio < 2.05:  # Each timestep has ~2x spatial points
                    print(f"  {trap_name}: Each timestep has 2x spatial points, deduplicating within arrays")
                    # Each array in data has duplicate x values - take every other spatial point
                    # 612 points but we need 307, not 306 (612/2)
                    # This suggests duplicates are interleaved, but with an odd number of unique points
                    
                    if len(trap_data_plot) == 612 and len(x) == 307:
                        # 612 = 2*306, but we need 307 points
                        # Take every other point: indices [0, 2, 4, ..., 610] gives 306 points
                        # To get 307, we need to go to 612 but max index is 611
                        # So take [0, 2, 4, ..., 610] = 306 points, then add last point
                        trap_plot_dedup = trap_data_plot[::2]  # 306 points
                        
                        # Pad with the last unique value to get 307 points
                        trap_plot = np.append(trap_plot_dedup, trap_data_plot[-1])
                    else:
                        # Generic deduplication
                        trap_plot = trap_data_plot[::2]
                    
                    print(f"  {trap_name}: Successfully deduplicated spatial dimension: {len(trap_plot)} points")
                    
                    # Final check
                    if len(trap_plot) != len(x):
                        print(f"  Warning: Still have dimension mismatch: {len(trap_plot)} != {len(x)}, adjusting")
                        if len(trap_plot) > len(x):
                            trap_plot = trap_plot[:len(x)]
                        else:
                            # Pad with last value if needed
                            trap_plot = np.pad(trap_plot, (0, len(x) - len(trap_plot)), mode='edge')
                        print(f"  {trap_name}: Adjusted to {len(trap_plot)} points")
                else:
                    print(f"  Warning: Skipping {trap_name} - unexpected data structure")
                    continue
            else:
                trap_plot = trap_data_plot
            
            # Plot individual traps with thin lines (for the selected timestep)
            ax2.plot(x * 1e3, trap_plot, linestyle='-', alpha=0.4, linewidth=1,
                    label=f'{trap_name.replace("_profile", "")} (t={t[idx_plot]:.1f}s)')
            
            total_trapped_plot += trap_plot
        
        # Print trapped T statistics
        print(f"\nTrapped T concentration statistics:")
        print(f"  Plotting timestep: min={np.min(total_trapped_plot):.2e}, max={np.max(total_trapped_plot):.2e}")
        print(f"  Negative values: {np.sum(total_trapped_plot < 0)}/{len(total_trapped_plot)}")
        
        # Plot total trapped with thick line (for the selected timestep)
        ax2.plot(x * 1e3, total_trapped_plot, color=color_traps, linestyle='-', 
                linewidth=2.5, label=f'Total trapped (t={t[idx_plot]:.1f}s)')
        
        ax2.set_ylabel('Trapped T concentration (m⁻³)', color=color_traps, fontsize=12)
        ax2.tick_params(axis='y', labelcolor=color_traps)
        
        # Use matplotlib's autoscale with tight layout for adaptive axis scaling
        ax1.autoscale(enable=True, axis='y')
        ax2.autoscale(enable=True, axis='y')
        
        # Add minor ticks for better readability
        ax1.minorticks_on()
        ax2.minorticks_on()
        ax1.tick_params(which='minor', length=3, color='gray')
        ax2.tick_params(which='minor', length=3, color='gray')
        
        # Combine legends
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='best', fontsize=9)
    else:
        ax1.legend(loc='best', fontsize=10)
        print("No trapped T profiles found")
    
    plt.title(f'T concentration profiles at t={t[idx_plot]:.1f}s\n{os.path.basename(profiles_file)}', fontsize=13)
    plt.tight_layout()
    
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Plot saved to: {output_file}")
    else:
        plt.show()
    
    plt.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python plot_profiles_first.py <profiles_file.json> [output_file.png]")
        print("\nExample:")
        print("  python plot_profiles_first.py results_10FPdays_baking/id_95_bin_num_95_w_apical_profiles.json")
        sys.exit(1)
    
    profiles_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # If no output file specified, create one based on input with suffix
    if not output_file:
        base_name = os.path.splitext(profiles_file)[0]
        output_file = f"{base_name}_T_profiles_first.png"
    
    if not os.path.exists(profiles_file):
        print(f"Error: File not found: {profiles_file}")
        sys.exit(1)
    
    plot_T_profiles(profiles_file, output_file)

import os
import sys
import json
import pandas as pd
import numpy as np
import argparse
import importlib.util

# Ensure HISP can locate PFC-Tritium-Transport's csv_bin.py without user setup
if "PFC_TT_PATH" not in os.environ and "HISP_PFC_TT_PATH" not in os.environ:
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    os.environ["PFC_TT_PATH"] = repo_root


# Get the parent directory of the current script
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Add the parent directory to sys.path
sys.path.insert(0, parent_dir)

from plasma_data_handling import PlasmaDataHandling

# Add hisp src to path
hisp_src = os.path.abspath(os.path.join(parent_dir, "hisp", "src"))
if hisp_src not in sys.path:
    sys.path.insert(0, hisp_src)

# Import CSV bin system
from bins_from_csv.csv_bin_loader import CSVBinLoader
from bins_from_csv.csv_bin import Reactor
from run_bin_functions import load_scenario_variable

# Import implantation calculator
from implantation_calculator import ImplantationCalculator

# Import NewModel class from hisp
from hisp.new_model import NewModel

# Parse command-line arguments
parser = argparse.ArgumentParser(
    description="Run a single CSV bin simulation",
    usage="%(prog)s bin_id scenario_folder scenario_name csv_file [--input-dir INPUT_DIR]"
)
parser.add_argument("bin_id", type=int, help="CSV bin ID (1-based row number in input table)")
parser.add_argument("scenario_folder", help="Scenario folder path")
parser.add_argument("scenario_name", help="Scenario name")
parser.add_argument("csv_file", help="Path to CSV input file")
parser.add_argument("--input-dir", dest="input_dir", default="input_files",
                    help="Directory containing input files (materials.csv, mesh.py, etc.). Default: input_files")

# Parse positional arguments first (for backwards compatibility)
args = parser.parse_args()

bin_id = args.bin_id
scenario_folder = args.scenario_folder
scenario_name = args.scenario_name
csv_file_path = args.csv_file
input_dir = args.input_dir

# If input_dir is provided, try to find materials and mesh files in that directory
if input_dir and input_dir != "input_files":
    print(f"Using input directory: {input_dir}")
    
    # Check if materials.csv exists in the input_dir
    materials_in_dir = os.path.join(input_dir, "materials.csv")
    if os.path.exists(materials_in_dir):
        print(f"  Found materials.csv in input directory")
        # CSVBinLoader will use this when the input_dir is properly set
    
    # Check if mesh.py exists in the input_dir
    mesh_in_dir = os.path.join(input_dir, "mesh.py")
    if os.path.exists(mesh_in_dir):
        print(f"  Found mesh.py in input directory")
        # Will be loaded from BINS_MESHES when available

print(f"Loading scenario: {scenario_name} from {scenario_folder}")
scenario = load_scenario_variable(scenario_folder, scenario_name)

print(f"Loading CSV bins from: {csv_file_path}")
# Load CSV reactor with optional materials path from input_dir
materials_path = None
if input_dir and input_dir != "input_files":
    materials_in_dir = os.path.join(input_dir, "materials.csv")
    if os.path.exists(materials_in_dir):
        materials_path = materials_in_dir

# Create loader with materials path
loader = CSVBinLoader(csv_file_path, materials_csv_path=materials_path)
csv_reactor = loader.load_reactor()

print(f"Loaded {len(csv_reactor)} bins from CSV")
print(csv_reactor.get_reactor_summary())

# Make a plasma data handling object. Prefer scenario-provided instance if present.
data_folder = "data"
if hasattr(scenario, "plasma_data_handling"):
    plasma_data_handling = scenario.plasma_data_handling
else:
    plasma_data_handling = PlasmaDataHandling(
        pulse_type_to_data={
            "FP": pd.read_csv(data_folder + "/Binned_Flux_Data.dat", delimiter=","),
            "FP_D": pd.read_csv(data_folder + "/Binned_Flux_Data_just_D_pulse.dat", delimiter=",", comment='#'),
            "ICWC": pd.read_csv(data_folder + "/ICWC_data.dat", delimiter=","),
            "GDC": pd.read_csv(data_folder + "/GDC_data.dat", delimiter=","),
        },
        path_to_ROSP_data=data_folder + "/ROSP_data",
        path_to_RISP_data=data_folder + "/RISP_data",
        path_to_RISP_wall_data=data_folder + "/RISP_Wall_data.dat",
    )


def compute_and_attach_implantation_params(bin, scenario, plasma_data_handling, use_physics_model=False):
    """
    Compute implantation parameters for a bin and attach them to bin.implantation_params.
    
    Args:
        bin: Bin object
        scenario: Scenario object
        plasma_data_handling: PlasmaDataHandling object with flux data
        use_physics_model: Whether to use physics-based calculations
    """
    calculator = ImplantationCalculator(use_physics_model=use_physics_model)
    material_name = bin.material.name if hasattr(bin.material, 'name') else str(bin.material)
    
    # Check if we should calculate parameters from flux data
    should_calculate = getattr(bin, 'calculate_implantation_params', True)
    
    # Try to extract energy and angle from the first FP pulse
    energy_ion = None
    angle_ion = None
    energy_atom = None
    angle_atom = None
    
    if should_calculate:
        # Look for FP pulse to get energy/angle data
        for pulse in scenario.pulses:
            if pulse.pulse_type == "FP":
                # Get ion data using bin's method
                implant_data_ion = bin.get_implantation_data(pulse, plasma_data_handling, ion=True)
                energy_ion = implant_data_ion.get('energy')
                angle_ion = implant_data_ion.get('angle')
                
                # Get atom data using bin's method
                implant_data_atom = bin.get_implantation_data(pulse, plasma_data_handling, ion=False)
                energy_atom = implant_data_atom.get('energy')
                angle_atom = implant_data_atom.get('angle')
                break
    
    # Compute parameters for ions and atoms
    params_ion = calculator.compute_implantation_params(
        energy=energy_ion,
        angle=angle_ion,
        material=material_name,
        particle_type='ion'
    )
    
    params_atom = calculator.compute_implantation_params(
        energy=energy_atom,
        angle=angle_atom,
        material=material_name,
        particle_type='atom'
    )
    
    # Attach to bin
    bin.implantation_params = {
        'ion': params_ion,
        'atom': params_atom
    }
    
    # Print debug info
    if should_calculate:
        if energy_ion is not None and angle_ion is not None:
            print(f"  Calculated implantation params for ions: E={energy_ion:.2f} eV, α={angle_ion:.2f}°")
            print(f"    Range: {params_ion['implantation_range']*1e9:.3f} nm, Width: {params_ion['width']*1e9:.3f} nm, Reflection: {params_ion['reflection_coefficient']:.3f}")
        else:
            print(f"  No energy/angle data found for ions, using defaults")
            print(f"    Range: {params_ion['implantation_range']*1e9:.3f} nm, Width: {params_ion['width']*1e9:.3f} nm, Reflection: {params_ion['reflection_coefficient']:.3f}")
        
        if energy_atom is not None and angle_atom is not None:
            print(f"  Calculated implantation params for atoms: E={energy_atom:.2f} eV, α={angle_atom:.2f}°")
            print(f"    Range: {params_atom['implantation_range']*1e9:.3f} nm, Width: {params_atom['width']*1e9:.3f} nm, Reflection: {params_atom['reflection_coefficient']:.3f}")
        else:
            print(f"  No energy/angle data found for atoms, using defaults")
            print(f"    Range: {params_atom['implantation_range']*1e9:.3f} nm, Width: {params_atom['width']*1e9:.3f} nm, Reflection: {params_atom['reflection_coefficient']:.3f}")
    else:
        print(f"  Using default implantation parameters (Calculate Implantation Parameters = No)")
        print(f"    Ions   - Range: {params_ion['implantation_range']*1e9:.3f} nm, Width: {params_ion['width']*1e9:.3f} nm, Reflection: {params_ion['reflection_coefficient']:.3f}")
        print(f"    Atoms  - Range: {params_atom['implantation_range']*1e9:.3f} nm, Width: {params_atom['width']*1e9:.3f} nm, Reflection: {params_atom['reflection_coefficient']:.3f}")


def run_new_csv_bin_scenario(scenario, bin_id: int):
    """Run scenario for a specific CSV bin ID using NewModel class."""
    
    coolant_temp = 343.0
    
    # Import BINS_MESHES from appropriate mesh configuration
    BINS_MESHES = {}
    
    # Try to load mesh from input_dir if available
    if input_dir and input_dir != "input_files":
        mesh_file = os.path.join(input_dir, "mesh.py")
        if os.path.exists(mesh_file):
            try:
                # Set environment variable so mesh.py can find the correct input folder
                os.environ["INPUT_DIR_CONTEXT"] = input_dir
                # Dynamically import mesh.py from input_dir
                spec = importlib.util.spec_from_file_location("mesh_config", mesh_file)
                mesh_config = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mesh_config)
                if hasattr(mesh_config, 'BINS_MESHES'):
                    BINS_MESHES = mesh_config.BINS_MESHES
                    print(f"Loaded mesh configuration from: {mesh_file}")
            except Exception as e:
                print(f"Warning: Could not load mesh from {mesh_file}: {e}")
    
    # Fall back to default input_files/mesh.py if no mesh in input_dir
    if not BINS_MESHES:
        try:
            from input_files.mesh import BINS_MESHES
        except ImportError:
            print("No mesh configuration found, using default mesh generation")
            BINS_MESHES = {}

    # Create NewModel instance (similar to how old script creates Model)
    my_new_model = NewModel(
        reactor=csv_reactor,
        scenario=scenario,
        plasma_data_handling=plasma_data_handling,
        coolant_temp=coolant_temp,
        bins_meshes=BINS_MESHES,
    )

    # Find the specific bin by bin_id (1-based row index in CSV)
    try:
        # Search through bins to find one with matching bin_id
        target_bin = None
        for bin in csv_reactor.bins:
            if bin.bin_id == bin_id:
                target_bin = bin
                break
        
        if target_bin is None:
            available_ids = [b.bin_id for b in csv_reactor.bins]
            raise ValueError(f"No bin found with bin_id {bin_id}. Available bin IDs: {sorted(set(available_ids))}")
        
        # Compute and attach implantation parameters
        print(f"\n=== Computing implantation parameters for Bin ID {bin_id} (Bin #{target_bin.bin_number}) ===")
        compute_and_attach_implantation_params(target_bin, scenario, plasma_data_handling, use_physics_model=True)
        print()
    except ValueError as e:
        print(f"Error: {e}")
        return

    try:
        # Get bin configuration early
        bin_config = target_bin.bin_configuration
        
        print(f"\n{'='*60}")
        print(f"Running CSV row {bin_id} (Bin #{target_bin.bin_number})")
        print(f"  Bin ID (row): {target_bin.bin_id}")
        print(f"  Bin number: {target_bin.bin_number}")
        print(f"  Material: {target_bin.material.name}")
        print(f"  Mode: {target_bin.mode}")
        print(f"  Location: {target_bin.location}")
        print(f"  Thickness: {target_bin.thickness*1e3:.2f} mm")
        print(f"  Surface area: {target_bin.surface_area:.4f} m²")
        print(f"  Cu thickness: {target_bin.cu_thickness*1e3:.2f} mm")
        print(f"  Ion scaling factor: {target_bin.ion_scaling_factor:.3f}")
        print(f"  BC plasma facing: {bin_config.bc_plasma_facing_surface}")
        print(f"  BC rear surface: {bin_config.bc_rear_surface}")
        print(f"  Tolerances: rtol={bin_config.rtol:.0e}, atol={bin_config.atol:.0e}")
        print(f"  Max stepsize FP: {bin_config.fp_max_stepsize:.1f} s")
        print(f"  Max stepsize no FP: {bin_config.max_stepsize_no_fp:.1f} s")
        print(f"{'='*60}\n")
        
        # Debug: Print flux values during flat-top
        print("=== Flux Debug (before running simulation) ===")
        from hisp.festim_models.new_mb_model import make_particle_flux_function
        
        # Get a time during flat-top of first FP pulse
        first_fp_pulse = None
        cumulative_time = 0
        for pulse in scenario.pulses:
            if pulse.pulse_type == "FP":
                first_fp_pulse = pulse
                break
            cumulative_time += pulse.total_duration
        
        if first_fp_pulse:
            flat_top_time = float(cumulative_time + first_fp_pulse.ramp_up + 10)  # 10s into flat-top
            
            # Create flux functions
            d_ion_flux = make_particle_flux_function(scenario, plasma_data_handling, target_bin, ion=True, tritium=False)
            t_ion_flux = make_particle_flux_function(scenario, plasma_data_handling, target_bin, ion=True, tritium=True)
            d_atom_flux = make_particle_flux_function(scenario, plasma_data_handling, target_bin, ion=False, tritium=False)
            t_atom_flux = make_particle_flux_function(scenario, plasma_data_handling, target_bin, ion=False, tritium=True)
            
            print(f"  Debug time: {flat_top_time:.1f}s (flat-top of first FP pulse)")
            print(f"  Bin {target_bin.bin_number} (mode={target_bin.mode})")
            print(f"  D ion flux: {d_ion_flux(flat_top_time):.6e} part/m^2/s")
            print(f"  T ion flux: {t_ion_flux(flat_top_time):.6e} part/m^2/s")
            print(f"  D atom flux: {d_atom_flux(flat_top_time):.6e} part/m^2/s")
            print(f"  T atom flux: {t_atom_flux(flat_top_time):.6e} part/m^2/s")
            print(f"  ion_scaling_factor: {target_bin.ion_scaling_factor:.6f}")
        print("===========================================\n")
        
        # Run the bin using NewModel.run_bin() method
        print("Running bin using NewModel.run_bin()...")
        model, quantities = my_new_model.run_bin(target_bin, exports=False)
        
        # Get temperature function for recording
        from hisp.festim_models.new_mb_model import make_temperature_function
        temperature_function = make_temperature_function(
            scenario=scenario,
            plasma_data_handling=plasma_data_handling,
            bin=target_bin,
            coolant_temp=coolant_temp,
        )
        
        # Separate profile data from scalar quantities
        profile_data = {}
        scalar_data = {}
        
        # Get time array first from any non-profile quantity
        t_sampled = None
        for key, value in quantities.items():
            if not key.endswith('_profile'):
                t_sampled = value.t[::1]
                break
        
        for key, value in quantities.items():
            if key.endswith('_profile'):
                # This is a Profile1DExport - save to separate file
                # Profile1DExport has attributes: x, t, data (list of arrays)
                profile_data[key] = {
                    'x': value.x.tolist() if hasattr(value.x, 'tolist') else list(value.x),
                    't': value.t.tolist() if hasattr(value.t, 'tolist') else list(value.t),
                    'data': [arr.tolist() if hasattr(arr, 'tolist') else list(arr) for arr in value.data]
                }
            else:
                # Scalar quantity (TotalVolume, SurfaceFlux, etc.)
                scalar_data[key] = {
                    "data": value.data[::1].tolist() if hasattr(value.data, 'tolist') else value.data[::1]
                }
        
        # Build final output dict
        csv_bin_data = scalar_data
        csv_bin_data["t"] = t_sampled.tolist() if hasattr(t_sampled, 'tolist') else list(t_sampled)
        
        # Add CSV bin specific information
        csv_bin_data["bin_id"] = target_bin.bin_id
        csv_bin_data["bin_number"] = target_bin.bin_number
        csv_bin_data["mode"] = target_bin.mode
        csv_bin_data["material"] = target_bin.material.name
        csv_bin_data["location"] = target_bin.location
        csv_bin_data["thickness"] = target_bin.thickness
        csv_bin_data["cu_thickness"] = target_bin.cu_thickness
        csv_bin_data["ion_scaling_factor"] = target_bin.ion_scaling_factor
        csv_bin_data["surface_area"] = target_bin.surface_area
        csv_bin_data["parent_bin_surf_area"] = target_bin.parent_bin_surf_area
        
        # Add bin configuration parameters
        csv_bin_data["bin_configuration"] = {
            "rtol": bin_config.rtol,
            "atol": bin_config.atol,
            "fp_max_stepsize": bin_config.fp_max_stepsize,
            "max_stepsize_no_fp": bin_config.max_stepsize_no_fp,
            "bc_plasma_facing_surface": bin_config.bc_plasma_facing_surface,
            "bc_rear_surface": bin_config.bc_rear_surface,
        }

        # Calculate temperature at x=0 (surface)
        x_eval = np.array([[0.0]])  # x = 0
        temperature_values = [float(temperature_function(x_eval, float(t))[0]) for t in t_sampled]
        csv_bin_data["temperature_at_x0"] = temperature_values

        # Save results to JSON files
        material_name = target_bin.material.name.lower()
        mode_name = target_bin.mode.lower().replace("_", "")
        
        # Use input folder name for results directory, save inside the input folder
        input_folder_name = os.path.basename(os.path.normpath(input_dir)) if input_dir else "results"
        results_dir = os.path.join(input_dir, f"results_{input_folder_name}")
        profiles_dir = os.path.join(input_dir, f"profiles_{input_folder_name}")
        
        base_filename = f"{results_dir}/id_{target_bin.bin_id}_bin_num_{target_bin.bin_number}_{material_name}_{mode_name}"
        output_file = f"{base_filename}.json"
        
        profiles_base = f"{profiles_dir}/id_{target_bin.bin_id}_bin_num_{target_bin.bin_number}_{material_name}_{mode_name}"
        profiles_file = f"{profiles_base}_profiles.json"
        
        os.makedirs(results_dir, exist_ok=True)
        
        # Save scalar quantities
        with open(output_file, "w") as f:
            json.dump(csv_bin_data, f, indent=4)
        
        # Save profile data to separate folder
        if profile_data:
            os.makedirs(profiles_dir, exist_ok=True)
            with open(profiles_file, "w") as f:
                json.dump(profile_data, f, indent=4)

        print(f"\n{'='*60}")
        print(f"✓ Simulation complete!")
        print(f"  Quantities saved to: {output_file}")
        if profile_data:
            print(f"  Profiles saved to: {profiles_file}")
            print(f"  Profile export times: {len(profile_data[list(profile_data.keys())[0]]['t'])} timesteps")
        print(f"{'='*60}\n")

    except Exception as e:
        print(f"Failed to process CSV bin ID {bin_id}: {e}")
        import traceback
        traceback.print_exc()


def make_milestones(scenario, bin_config):
    """
    Create milestone times for adaptive timestepping based on scenario pulses.
    
    Note: This function is not currently used. HISP provides its own milestone generation.
    """
    return []


if __name__ == "__main__":
    run_new_csv_bin_scenario(scenario, bin_id)
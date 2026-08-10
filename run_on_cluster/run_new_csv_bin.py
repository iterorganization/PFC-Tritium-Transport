import sys
sys.dont_write_bytecode = True  # prevent __pycache__ creation
import os
import json
import pandas as pd
import numpy as np
import argparse
import importlib.util
from types import ModuleType
import time

start_time = time.perf_counter()

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

# Import resolve helper
from resolve_input_dir import resolve_input_dir

# Import NewModel class from hisp
from hisp.new_model import NewModel

# Parse command-line arguments
parser = argparse.ArgumentParser(
    description="Run a single CSV bin simulation",
    usage="%(prog)s sim_id scenario_folder scenario_name csv_file [--input-dir INPUT_DIR]"
)
parser.add_argument("sim_id", type=int, help="Simulation ID (from Sim. ID column, or 1-based row number)")
parser.add_argument("scenario_folder", help="Scenario folder path")
parser.add_argument("scenario_name", help="Scenario name")
parser.add_argument("csv_file", help="Path to CSV input file")
parser.add_argument("--input-dir", dest="input_dir", default="input_files",
                    help="Directory containing input files (materials.csv, mesh.py, etc.). Default: input_files")

# Parse positional arguments first (for backwards compatibility)
args = parser.parse_args()

sim_id = args.sim_id
scenario_folder = args.scenario_folder
scenario_name = args.scenario_name
csv_file_path = args.csv_file
input_dir = args.input_dir

# Resolve input directory (searches inside PFC-TT and one level above)
if input_dir and input_dir != "input_files":
    input_dir = resolve_input_dir(input_dir, repo_root=parent_dir)

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
scenario_plasma_data_handling = load_scenario_variable(scenario_folder, scenario_name, variable_name="plasma_data_handling")

# Debug: log baking temperature so it appears in SLURM .out files
_baking_temp_val = getattr(scenario, 'baking_temp', 'MISSING')
print(f"[DEBUG] scenario.baking_temp = {_baking_temp_val} K")
for i, p in enumerate(scenario.pulses):
    print(f"[DEBUG]   pulse[{i}] type={p.pulse_type}  duration={p.total_duration}s")


def _normalize_material_name(name):
    if not isinstance(name, str):
        return None
    return name.strip().upper()


def _extract_temperature_models_from_module(module: ModuleType):
    """
    Extract temperature model mapping from an imported module.

    Supported contracts in temperature_models.py:
      1) TEMPERATURE_MODELS: dict[str, callable]
      2) get_temperature_models() -> dict[str, callable]
    """
    mapping = None

    if hasattr(module, "TEMPERATURE_MODELS"):
        mapping = getattr(module, "TEMPERATURE_MODELS")
    elif hasattr(module, "get_temperature_models"):
        getter = getattr(module, "get_temperature_models")
        if callable(getter):
            mapping = getter()

    if mapping is None:
        return {}

    if not isinstance(mapping, dict):
        raise TypeError("temperature_models mapping must be a dict[str, callable]")

    parsed = {}
    for material, model_fn in mapping.items():
        material_key = _normalize_material_name(material)
        if material_key is None:
            print(f"Warning: ignoring non-string material key in temperature models: {material!r}")
            continue
        if not callable(model_fn):
            print(f"Warning: ignoring non-callable temperature model for material {material_key!r}")
            continue
        parsed[material_key] = model_fn

    return parsed


def load_temperature_model_overrides(input_folder: str):
    """
    Load optional per-material temperature models from <input_folder>/temperature_models.py.

    Returns:
        dict[str, callable]: mapping material -> temperature model callable
    """
    model_file = os.path.join(input_folder, "temperature_models.py")
    if not os.path.exists(model_file):
        print("No custom temperature models file found; using default HISP temperature models")
        return {}

    try:
        spec = importlib.util.spec_from_file_location("temperature_models", model_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        mapping = _extract_temperature_models_from_module(module)
        if mapping:
            print(f"Loaded custom temperature models for materials: {sorted(mapping.keys())}")
        else:
            print("temperature_models.py found, but no valid models were declared; using defaults")
        return mapping
    except Exception as e:
        print(f"Warning: Failed to load custom temperature models from {model_file}: {e}")
        print("Falling back to default HISP temperature models")
        return {}


temperature_model_overrides = load_temperature_model_overrides(input_dir)

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

# Make a plasma data handling object — MUST come from the scenario file.
# No silent fallback: if the scenario doesn't provide one (e.g. wrong data file
# path), we abort immediately so the user knows.
if scenario_plasma_data_handling is not None:
    plasma_data_handling = scenario_plasma_data_handling
    print("Using plasma_data_handling from scenario file")

    # Show which .dat files the scenario references (informational)
    import re as _re
    scenario_file_path = os.path.join(scenario_folder, f"{scenario_name}.py")
    try:
        with open(scenario_file_path) as _fh:
            _source = _fh.read()
        _dat_refs = _re.findall(r'["\']([^"\']*\.dat)["\']', _source)
        if _dat_refs:
            print("Plasma flux data files referenced in scenario:")
            for _p in _dat_refs:
                print(f"  ← {_p}")
    except Exception:
        pass
else:
    print("\n" + "=" * 60)
    print("ERROR: plasma_data_handling not found in scenario file!")
    print("=" * 60)
    print(f"  Scenario: {scenario_folder}/{scenario_name}.py")
    print()
    print("This usually means one of:")
    print("  1) The scenario file has a wrong path to a .dat flux data file")
    print("     (e.g. data_folder points to a non-existent directory)")
    print("  2) The scenario file does not define a 'plasma_data_handling' variable")
    print()
    print("Check the scenario file and ensure all pd.read_csv() paths are correct.")
    print("=" * 60)
    sys.exit(1)

# Print the actual data paths loaded into the PlasmaDataHandling object
print("Plasma data sources (actually loaded):")
for _pt, _df in plasma_data_handling.pulse_type_to_data.items():
    _src = getattr(_df, "attrs", {}).get("source", None)
    if _src is None and hasattr(_df, "_metadata"):
        _src = None  # pandas DataFrames don't remember their source path
    print(f"  pulse_type={_pt!r}: DataFrame with {len(_df)} rows, {len(_df.columns)} columns")
for _attr in ("path_to_RISP_data", "path_to_ROSP_data", "path_to_RISP_wall_data"):
    _val = getattr(plasma_data_handling, _attr, None)
    if _val is not None:
        _exists = os.path.exists(_val)
        print(f"  {_attr}: {os.path.abspath(_val)} (exists={_exists})")
    else:
        print(f"  {_attr}: not set")


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
        
        # If no FP pulse found, try GDC or Bake+GDC pulses
        if energy_ion is None and energy_atom is None:
            for pulse in scenario.pulses:
                if pulse.pulse_type in ("GDC", "Bake+GDC"):
                    implant_data_ion = bin.get_implantation_data(pulse, plasma_data_handling, ion=True)
                    energy_ion = implant_data_ion.get('energy')
                    angle_ion = implant_data_ion.get('angle')
                    
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
        print(f"  Material: {material_name} → {'SS' if material_name.strip().upper() == 'SS' else 'W'} implantation model")
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


def run_new_csv_bin_scenario(scenario, sim_id: int):
    """Run scenario for a specific simulation ID using NewModel class."""
    
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
        temperature_model_overrides=temperature_model_overrides,
    )

    # Find the specific bin by sim_id
    try:
        # Search through bins to find one with matching sim_id
        target_bin = None
        for bin in csv_reactor.bins:
            if bin.sim_id == sim_id:
                target_bin = bin
                break
        
        if target_bin is None:
            available_ids = [b.sim_id for b in csv_reactor.bins]
            raise ValueError(f"No bin found with sim_id {sim_id}. Available sim IDs: {sorted(set(available_ids))}")
        
        # Compute and attach implantation parameters
        print(f"\n=== Computing implantation parameters for Sim ID {sim_id} (Flux ID #{target_bin.flux_id}) ===")
        compute_and_attach_implantation_params(target_bin, scenario, plasma_data_handling, use_physics_model=True)
        print()
    except ValueError as e:
        print(f"Error: {e}")
        return

    try:
        # Get bin configuration early
        bin_config = target_bin.bin_configuration
        
        print(f"\n{'='*60}")
        print(f"Running Sim ID {sim_id} (Flux ID #{target_bin.flux_id})")
        print(f"  Sim ID: {target_bin.sim_id}")
        print(f"  Flux ID: {target_bin.flux_id}")
        print(f"  Material: {target_bin.material.name}")
        print(f"  Mode: {target_bin.mode}")
        print(f"  Location: {target_bin.location}")
        print(f"  Thickness: {target_bin.thickness*1e3:.2f} mm")
        print(f"  Surface area: {target_bin.surface_area:.4f} m²")
        print(f"  Cu thickness: {target_bin.cu_thickness*1e3:.2f} mm")
        print(f"  Ion scaling factor: {target_bin.ion_scaling_factor:.3f}")
        print(f"  Atom view factor: {getattr(target_bin, 'atom_view_factor', 1.0):.4f}")
        print(f"  BC plasma facing: {bin_config.bc_plasma_facing_surface}")
        print(f"  BC rear surface: {bin_config.bc_rear_surface}")
        print(f"  Tolerances: rtol={bin_config.rtol:.0e}, atol={bin_config.atol:.0e}")
        print(f"  Max stepsize FP: {bin_config.fp_max_stepsize:.1f} s")
        print(f"  Max stepsize no FP: {bin_config.max_stepsize_no_fp:.1f} s")

        material_key = _normalize_material_name(target_bin.material.name)
        if material_key in temperature_model_overrides:
            print(f"  Temperature model: custom user model from temperature_models.py (material={material_key})")
        else:
            print(f"  Temperature model: default HISP/FESTIM path (no custom model for material={material_key})")

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
            print(f"  Bin {target_bin.flux_id} (mode={target_bin.mode})")
            print(f"  D ion flux: {d_ion_flux(flat_top_time):.6e} part/m^2/s")
            print(f"  T ion flux: {t_ion_flux(flat_top_time):.6e} part/m^2/s")
            print(f"  D atom flux: {d_atom_flux(flat_top_time):.6e} part/m^2/s")
            print(f"  T atom flux: {t_atom_flux(flat_top_time):.6e} part/m^2/s")
            print(f"  ion_scaling_factor: {target_bin.ion_scaling_factor:.6f}")
            print(f"  atom_view_factor: {getattr(target_bin, 'atom_view_factor', 1.0):.6f}")
        print("===========================================\n")
        
        # Compute results directory early so VTX checkpoints land in the right place
        material_name = target_bin.material.name.lower()
        mode_name = target_bin.mode.lower().replace("_", "")
        input_folder_name = os.path.basename(os.path.normpath(input_dir)) if input_dir else "results"
        results_dir = os.path.join(input_dir, f"results_{input_folder_name}")
        checkpoints_dir = os.path.join(input_dir, "checkpoints")
        os.makedirs(results_dir, exist_ok=True)
        os.makedirs(checkpoints_dir, exist_ok=True)
        
        # Run the bin using NewModel.run_bin() method
        print("Running bin using NewModel.run_bin()...")
        model, quantities = my_new_model.run_bin(target_bin, exports=True, folder=checkpoints_dir)
        
        # Get temperature function for recording
        from hisp.festim_models.new_mb_model import make_temperature_function
        temperature_function = make_temperature_function(
            scenario=scenario,
            plasma_data_handling=plasma_data_handling,
            bin=target_bin,
            coolant_temp=coolant_temp,
            temperature_model_overrides=temperature_model_overrides,
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
                # Skip if no data was exported (x will be None)
                if value.x is None or len(value.data) == 0:
                    print(f"  Warning: No profile data for {key} (no exports triggered)")
                    continue
                profile_data[key] = {
                    'x': value.x.tolist() if hasattr(value.x, 'tolist') else list(value.x),
                    't': value.t if isinstance(value.t, list) else list(value.t),
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
        csv_bin_data["sim_id"] = target_bin.sim_id
        csv_bin_data["flux_id"] = target_bin.flux_id
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

        # Calculate temperature at x=0 (plasma-facing surface)
        x_eval = np.array([[0.0]])  # x = 0
        temperature_values = [float(temperature_function(x_eval, float(t))[0]) for t in t_sampled]
        csv_bin_data["temperature_at_x0"] = temperature_values

        # Calculate temperature at x=thickness (rear surface)
        x_rear = np.array([[target_bin.thickness]])  # x = thickness
        temperature_rear_values = [float(temperature_function(x_rear, float(t))[0]) for t in t_sampled]
        csv_bin_data["temperature_at_rear"] = temperature_rear_values

        # Save results to JSON files
        # (material_name, mode_name, input_folder_name, results_dir computed earlier)
        profiles_dir = os.path.join(input_dir, f"profiles_{input_folder_name}")
        
        base_filename = f"{results_dir}/sim_{target_bin.sim_id}_flux_{target_bin.flux_id}_{material_name}_{mode_name}"
        output_file = f"{base_filename}.json"
        
        profiles_base = f"{profiles_dir}/sim_{target_bin.sim_id}_flux_{target_bin.flux_id}_{material_name}_{mode_name}"
        profiles_file = f"{profiles_base}_profiles.json"
        
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

        total_runtime = time.perf_counter() - start_time
        print(f"  Total runtime: {total_runtime:.2f} seconds = {total_runtime/60:.2f} minutes")
        print(f"{'='*60}\n")

    except Exception as e:
        print(f"Failed to process Sim ID {sim_id}: {e}")
        import traceback
        traceback.print_exc()


def make_milestones(scenario, bin_config):
    """
    Create milestone times for adaptive timestepping based on scenario pulses.
    
    Note: This function is not currently used. HISP provides its own milestone generation.
    """
    return []


if __name__ == "__main__":
    run_new_csv_bin_scenario(scenario, sim_id)
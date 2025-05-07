import os
import json
# import pandas as pd
import subprocess

from iter_bins.make_iter_bins import FW_bins, Div_bins

from bin_data.bin_data import load_geometry, create_bins, read_dat_file, read_div_solps, bin_fluxes_div, bin_fluxes_wall

from imas_data.wall_loads import wall_loads # includes dataclasses for loading and storing the IMAS data

def call_merge_results():
    subprocess.run(["python", "merge_results.py"])

# def run_scenario(scenario: Scenario, results_file: str):

#     global_data = {}
#     processed_data = []
#     call_submit_div_jobs()
#     call_merge_results()

def submit_wall_jobs(FW_bins, scenario_folder, scenario_name, slurm_script):
    """
    Submits jobs for each FW bin and sub-bin using SLURM.

    Parameters:
    - FW_bins: Object containing bins and sub_bins
    - slurm_script: SLURM script to be executed (default: "slurm_wall_job.sh")
    - results_file: Path to store results (default: "wall_results.json")

    Returns:
    - List of submitted job IDs
    """

    # Ensure necessary directories exist
    os.makedirs("logs", exist_ok=True)
    os.makedirs("job_data", exist_ok=True)

    job_ids = []

    for fw_bin in FW_bins.bins:
        for sub_bin in fw_bin.sub_bins:
            # Prepare job data
            job_data = {
                "fw_bin_index": fw_bin.index,
                "sub_bin_mode": sub_bin.mode,
                "sub_bin_parent": sub_bin.parent_bin_index
            }
            job_json_file = f"job_data/wall_bin_{fw_bin.index}_sub_bin_{sub_bin.mode}.json"

            # Write job data to JSON file
            with open(job_json_file, "w") as f:
                json.dump(job_data, f)

            # Submit job using SLURM
            cmd = f"sbatch {slurm_script} {fw_bin.index} {sub_bin.mode} {scenario_folder} {scenario_name}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            if result.returncode == 0:
                job_id = result.stdout.strip().split()[-1]
                job_ids.append(job_id)
                print(f"✅ Submitted job {job_id} for wall bin {fw_bin.index}, sub_bin {sub_bin.mode}")
            else:
                print(f"❌ Failed to submit job for wall bin {fw_bin.index}, sub_bin {sub_bin.mode}")
                print("Error:", result.stderr)
        #     break
        # break
                
    # # Save job IDs to a file
    # with open("job_ids.json", "w") as f:
    #     json.dump(job_ids, f)

    return job_ids  # Return the list of submitted job IDs

def submit_div_jobs(Div_bins, scenario_folder, scenario_name, slurm_script):
    """
    Submits jobs for each divertor bin using SLURM.

    Parameters:
    - Div_bins: Object containing bins
    - slurm_script: SLURM script to be executed (default: "slurm_wall_job.sh")
    - results_file: Path to store results (default: "wall_results.json")

    Returns:
    - List of submitted job IDs
    """

    # Ensure necessary directories exist
    os.makedirs("logs", exist_ok=True)
    os.makedirs("job_data", exist_ok=True)

    job_ids = []

    for div_bin in Div_bins.bins:
        # Save job data to a JSON file
        job_json_file = f"job_data/div_bin_{div_bin.index}.json"
        job_data = {"bin_index": div_bin.index}

        with open(job_json_file, "w") as f:
            json.dump(job_data, f)

        # Submit the job using SLURM
        cmd = f"sbatch {slurm_script} {div_bin.index} {scenario_folder} {scenario_name}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            job_id = result.stdout.strip().split()[-1]
            job_ids.append(job_id)
            print(f"✅ Submitted job {job_id} for divertor bin {div_bin.index}")
        else:
            print(f"❌ Failed to submit job for divertor bin {div_bin.index}")
            print("Error:", result.stderr)
        # break
                
    return job_ids  # Return the list of submitted job IDs

if __name__ == "__main__":

    if 0:
        # Example of the input to the wall_loads script gathering data from IMAS record
        username          = "public"                 # IMAS database name
        device            = "iter"                   # IMAS device name
        label_list        = ['SRO_A'  ,   'SRO_B']   # Labels used to find appropriate pulse in the workflow
        shot_list         = [106000   ,   106001 ]   # IMAS shot numbers
        run_list          = [  1      ,     1    ]   # IMAS run numbers
        slice_list        = [  1      ,     1    ]   # Time slice in the IMAS record (should be 1 for stationary cases)
        code_origin_list  = ['SOLEDGE', 'SOLEDGE']   # Code used to produce data 
        # Currently only "SOLEDGE" or likewise wall ids writers are supported), "SOLPS" can be used to write the target loads data to files only
        write_data        = False                    # If True data will be written to text files (for debugging and plotting)

        plasma_data = wall_loads(username,device,label_list,shot_list,run_list,slice_list,code_origin_list,write_data)

        ### create bins
        # load geometry file TODO: input file should contain start point and end point for each bin on a 
        # line (assume no continuous piecewise linear line, can be broken where gaps exist, e.g. in divertor))
        wall_z, wall_r = load_geometry('./iter_bins/FWpanelcorners.txt')
        div_z, div_r = load_geometry('./iter_bins/Divbincorners.txt', wall=False)
        wall_bins = create_bins(wall_z, wall_r)
        div_bins = create_bins(div_z, div_r)
        print(f'There are {len(wall_bins)+len(div_bins)} bins.')

        ### bin data:
        # Read input files and assign data to bins.
        # Save binned data to input files
        # All bin files are store following data
        # segment (r1 r2 z1 z2),Flux_Ion,Flux_Atom,E_ion,E_atom,alpha_ion,alpha_atom,heat_total,heat_ion
        # TODO: instead of writing and reading files, create a dataclass for each pulse type
        # TODO: move this into a separate script that takes as input argument
        # - input file path (main chamber or divertor) or 
        # - IMAS ids (main chamber or divertor)
        # and a dataclass with binned data as output (main chamber or divertor)
        ## FP pulse
        # load wall data
        data_wall = read_dat_file('./wdn_data/Background_Flux_Data')
        # read divertor data from IMAS --> TODO: make sure all the needed columns are written
        # divertor_target_loads("public","iter",[122481],1,'SOLPS') # 122258
        # read IMAS output files --> TODO: make sure to update script to final column formatting
        inner_data, outer_data, data_div = read_div_solps('./imas_data/fp_tg_i.2481.dat',
                                                            './imas_data/fp_tg_o.2481.dat',
                                                            './imas_data/ld_tg_i.2481.dat',
                                                            './imas_data/ld_tg_o.2481.dat',
                                                            './imas_data/inner_target.shot122481.run1.dat',
                                                            './imas_data/outer_target.shot122481.run1.dat')
        # bin the data: TODO: separate script for main chamber and divertor
        # ion_flux_total, atom_flux_total, E_ion_total, E_atom_total, alpha_ion_total, alpha_atom_total, heat_total, wall_F_ion, wall_F_atom, div_F_ion, div_F_atom, div_E_ion, div_E_atom, div_alpha_ion, div_alpha_atom, div_heat, wall_E_ion, wall_E_atom, wall_alpha_ion, wall_alpha_atom, wall_heat, heat_ion_total = bin_fluxes(data_wall, data_div, wall_bins, div_bins)
        plotbins = 1
        # TODO: remove bins that are gaps, as Kaelyn...
        # TODO: add missing data for horizontal plates and dome...
        div_F_ion, div_F_atom, div_E_ion, div_E_atom, div_alpha_ion, div_alpha_atom, div_heat, div_heat_ion = bin_fluxes_div(data_div, div_bins, plotbins)
        # TODO: remove divertor data from wall plot
        wall_F_ion, wall_F_atom, wall_E_ion, wall_E_atom, wall_alpha_ion, wall_alpha_atom, wall_heat, wall_heat_ion = bin_fluxes_wall(data_wall, wall_bins, plotbins)

        # save total fluxes to .dat file
        # for now no data is saved (avoid overwriting of patched data of DT study)
        # TODO: instead of a point, each line should have start en end coordinate of bin (r1, r2, z1, z2)
        # header = "Z_Coord             \tR_Coord                      \tFlux_Ion                      \tFlux_Atom                          \tE_ion                          \tE_atom              \talpha_ion           \talpha_atom         \theat_total        \theat_ion"
        # data_to_save = np.array([
        #     [z_coord, r_coord, ion_flux, atom_flux, E_ion, E_atom, alpha_ion, alpha_atom, heat, heat_ion_val]
        #     for ((z_coord, _), (r_coord, _)), ion_flux, atom_flux, E_ion, E_atom, alpha_ion, alpha_atom, heat, heat_ion_val in zip(bins+div_bins, ion_flux_total, atom_flux_total, E_ion_total, E_atom_total, alpha_ion_total, alpha_atom_total, heat_total, heat_ion_total)
        # ])
        # np.savetxt(home+"/hisp/flux_data/Binned_Flux_Data.dat", data_to_save, delimiter='\t', header=header, comments='')

    job_ids_wall = submit_wall_jobs(FW_bins, "iter_scenarios", "testcase", "run_on_cluster/slurm_wall_job.sh") # , "wall_results.json"
    job_ids_div = submit_div_jobs(Div_bins, "iter_scenarios", "testcase", "run_on_cluster/slurm_div_job.sh") # , "wall_results.json"

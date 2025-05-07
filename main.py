import json
import pandas as pd

from hisp.plamsa_data_handling import PlasmaDataHandling

from iter_bins.make_iter_bins import FW_bins, Div_bins, my_reactor
from bin_data.bin_data import load_geometry, create_bins, read_dat_file, read_div_solps, bin_fluxes_div, bin_fluxes_wall

from hisp.model import Model
from hisp.scenario import Scenario

from imas_data.wall_loads import wall_loads # includes dataclasses for loading and storing the IMAS data

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
    # TODO: instead of a point, each line should have start en end coordinate of bin (r1, r2, z1, z2)
    header = "Z_Coord             \tR_Coord                      \tFlux_Ion                      \tFlux_Atom                          \tE_ion                          \tE_atom              \talpha_ion           \talpha_atom         \theat_total        \theat_ion"
    data_to_save = np.array([
        [z_coord, r_coord, ion_flux, atom_flux, E_ion, E_atom, alpha_ion, alpha_atom, heat, heat_ion_val]
        for ((z_coord, _), (r_coord, _)), ion_flux, atom_flux, E_ion, E_atom, alpha_ion, alpha_atom, heat, heat_ion_val in zip(bins+div_bins, ion_flux_total, atom_flux_total, E_ion_total, E_atom_total, alpha_ion_total, alpha_atom_total, heat_total, heat_ion_total)
    ])
    # np.savetxt(home+"/hisp/flux_data/Binned_Flux_Data.dat", data_to_save, delimiter='\t', header=header, comments='')

# Make a plasma data handling object
data_folder = "data"
plasma_data_handling = PlasmaDataHandling(
    pulse_type_to_data={
        "FP": pd.read_csv(data_folder + "/Binned_Flux_Data.dat", delimiter=","),
        "ICWC": pd.read_csv(data_folder + "/ICWC_data.dat", delimiter=","),
        "GDC": pd.read_csv(data_folder + "/GDC_data.dat", delimiter=","),
    },
    path_to_ROSP_data=data_folder + "/ROSP_data",
    path_to_RISP_data=data_folder + "/RISP_data",
    path_to_RISP_wall_data=data_folder + "/RISP_Wall_data.dat",
)

def run_scenario(scenario: Scenario, results_file: str):

    # Make a HISP model object
    my_hisp_model = Model(
        reactor=my_reactor,
        scenario=scenario,
        plasma_data_handling=plasma_data_handling,
        coolant_temp=343.0,
    )

    global_data = {}
    processed_data = []

    # # first wall bins
    for fw_bin in FW_bins.bins:
        global_data[fw_bin] = {}
        fw_bin_data = {"bin_index": fw_bin.index, "sub_bins": []}
        processed_data.append(fw_bin_data)

        for sub_bin in fw_bin.sub_bins:
            try:
                print(f"Running bin FW {fw_bin.index}, {sub_bin.mode}")
                _, quantities = my_hisp_model.run_bin(sub_bin)

                global_data[fw_bin][sub_bin] = quantities

                subbin_data = {
                    key: {"t": value.t, "data": value.data}
                    for key, value in quantities.items()
                }
                subbin_data["mode"] = sub_bin.mode
                subbin_data["parent_bin_index"] = sub_bin.parent_bin_index

                fw_bin_data["sub_bins"].append(subbin_data)


                # write the processed data to JSON
                with open(results_file, "w+") as f:
                    json.dump(processed_data, f, indent=4)
            except KeyboardInterrupt:
                print("Process interrupted by user. Exiting...")
                return
            except: 
                print(f"Failed to run bin FW {fw_bin.index}, {sub_bin.mode}")

    # divertor bins
    # for div_bin in Div_bins.bins:
    #     try:
    #         print(f"Running bin div {div_bin.index}")
    #         _, quantities = my_hisp_model.run_bin(div_bin)

    #         global_data[div_bin] = quantities

    #         bin_data = {
    #             key: {"t": value.t, "data": value.data} for key, value in quantities.items()
    #         }
    #         bin_data["bin_index"] = div_bin.index

    #         processed_data.append(bin_data)
    #         # write the processed data to JSON
    #         with open(results_file, "w+") as f:
    #             json.dump(processed_data, f, indent=4)
    #     except KeyboardInterrupt:
    #         print("Process interrupted by user. Exiting...")
    #         return
    #     except: 
    #         print(f"Failed to run bin div {div_bin.index}")


if __name__ == "__main__":

    from iter_scenarios.benchmark import scenario as scenario_benchmark
    from iter_scenarios.clean_every_2_days import (
        scenario as scenario_clean_every_2_days,
    )
    from iter_scenarios.clean_every_5_days import (
        scenario as scenario_clean_every_5_days,
    )
    from iter_scenarios.do_nothing import scenario as scenario_do_nothing
    from iter_scenarios.no_glow import scenario as scenario_no_glow
    from iter_scenarios.just_glow import scenario as scenario_just_glow

    for scenario, name in [
        (scenario_benchmark, "benchmark_fw_bins"),
        # (scenario_clean_every_2_days, "clean_every_2_days"),
        # (scenario_clean_every_5_days, "clean_every_5_days"),
        # (scenario_do_nothing, "do_nothing"),
        # (scenario_no_glow, "no_glow"),
        # (scenario_just_glow, "just_glow"),
    ]:
        print(f"Running scenario: {name}")
        run_scenario(scenario, f"results_{name}.json")

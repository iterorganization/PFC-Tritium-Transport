#!/usr/bin/env python3
"""
Generate CSV with ion and atom fluxes per bin/subbin and pulse type.
Produces: results_fluxes_by_case.csv in repository root.
"""
import os
import pandas as pd
from make_iter_bins import FW_bins, Div_bins, my_reactor

# locate data folder (one level up from this script)
this_dir = os.path.dirname(os.path.abspath(__file__))
data_folder = os.path.normpath(os.path.join(this_dir, '..', 'data'))

# read data files
fp_df = pd.read_csv(os.path.join(data_folder, 'Binned_Flux_Data.dat'), delimiter=',')
fp_d_df = pd.read_csv(os.path.join(data_folder, 'Binned_Flux_Data_just_D_pulse.dat'), delimiter=',', comment='#')
icwc_df = pd.read_csv(os.path.join(data_folder, 'ICWC_data.dat'), delimiter=',')
gdc_df = pd.read_csv(os.path.join(data_folder, 'GDC_data.dat'), delimiter=',')
risp_wall_df = pd.read_csv(os.path.join(data_folder, 'RISP_Wall_data.dat'), delimiter=',')

pulse_types = {
    'FP': fp_df,
    'FP_D': fp_d_df,
    'ICWC': icwc_df,
    'GDC': gdc_df,
    'RISP_WALL': risp_wall_df,
}

rows = []

# helper to get value safely
def get_from_df(df, bin_index, col):
    try:
        if 'Bin_Index' in df.columns:
            sel = df.loc[df['Bin_Index'] == bin_index]
            if sel.shape[0] == 0:
                return 0.0
            val = sel.iloc[0][col]
            return float(val)
        else:
            return float(df[col].iloc[bin_index])
    except Exception:
        return 0.0

# iterate FW bins
for fw_bin in FW_bins.bins:
    for subbin in fw_bin.sub_bins:
        for p_name, df in pulse_types.items():
            bin_idx = fw_bin.index
            # incident hydrogen particle flux (ion and atom)
            flux_ion = get_from_df(df, bin_idx, 'Flux_Ion')
            flux_atom = get_from_df(df, bin_idx, 'Flux_Atom')

            # ion flux is scaled by wetted fraction for subbins
            flux_ion_sub = flux_ion * subbin.wetted_frac
            flux_atom_sub = flux_atom  # atom flux not scaled per code

            # compute isotope splits for two example tritium fractions
            for tr_frac in (0.5, 0.0):
                d_frac = 1.0 - tr_frac
                row = {
                    'bin_index': bin_idx,
                    'subbin_mode': subbin.mode,
                    'parent_bin_index': subbin.parent_bin_index,
                    'pulse_type': p_name,
                    'tritium_fraction': tr_frac,
                    'incident_ion_flux': flux_ion_sub,
                    'incident_atom_flux': flux_atom_sub,
                    'D_ion_flux': flux_ion_sub * d_frac,
                    'T_ion_flux': flux_ion_sub * tr_frac,
                    'D_atom_flux': flux_atom_sub * d_frac,
                    'T_atom_flux': flux_atom_sub * tr_frac,
                }
                rows.append(row)

# iterate Div bins (only wetted)
for div_bin in Div_bins.bins:
    for p_name, df in pulse_types.items():
        bin_idx = div_bin.index
        flux_ion = get_from_df(df, bin_idx, 'Flux_Ion')
        flux_atom = get_from_df(df, bin_idx, 'Flux_Atom')
        # for div bins flux_frac = 1
        flux_ion_sub = flux_ion
        flux_atom_sub = flux_atom
        for tr_frac in (0.5, 0.0):
            d_frac = 1.0 - tr_frac
            row = {
                'bin_index': bin_idx,
                'subbin_mode': 'wetted',
                'parent_bin_index': bin_idx,
                'pulse_type': p_name,
                'tritium_fraction': tr_frac,
                'incident_ion_flux': flux_ion_sub,
                'incident_atom_flux': flux_atom_sub,
                'D_ion_flux': flux_ion_sub * d_frac,
                'T_ion_flux': flux_ion_sub * tr_frac,
                'D_atom_flux': flux_atom_sub * d_frac,
                'T_atom_flux': flux_atom_sub * tr_frac,
            }
            rows.append(row)

out_df = pd.DataFrame(rows)
out_csv = os.path.normpath(os.path.join(this_dir, '..', 'results_fluxes_by_case.csv'))
out_df.to_csv(out_csv, index=False)
print('Wrote', out_csv)

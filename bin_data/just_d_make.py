import pandas as pd
import numpy as np

df = pd.read_csv("data/Binned_Flux_Data.dat", delimiter=",")

# 1FP DD, decrease fluxes and loads by 5

ion_fluxes = df["Flux_Ion"]/5
atom_fluxes = df["Flux_Atom"]/5
bin_idxs = df["Bin_Index"]
E_ion = df["E_ion"]
E_atom = df["E_atom"]
alpha_ion = df["alpha_ion"]
alpha_atom = df["alpha_atom"]
heat_total = df["heat_total"]/5
heat_ion = df["heat_ion"]/5

header = "Bin_Index,Flux_Ion,Flux_Atom,E_ion,E_atom,alpha_ion,alpha_atom,heat_total,heat_ion"
to_save = np.array([
    [bin_idx, ion_f, atom_f, ion_E, atom_E, ion_alpha, atom_alpha, total_heat, ion_heat]
    for bin_idx, ion_f, atom_f, ion_E, atom_E, ion_alpha, atom_alpha, total_heat, ion_heat in zip(bin_idxs,ion_fluxes,atom_fluxes,E_ion,E_atom,alpha_ion,alpha_atom,heat_total,heat_ion)
])

np.savetxt("data/Binned_Flux_Data_just_D_pulse.dat", to_save, delimiter=",", header=header, fmt=['%d']  + ['%.18e'] * (to_save.shape[1] - 1))
"""
Plasma Data Handling Module

This module handles plasma data retrieval and processing for PFC simulations.
It manages binned flux data, heat loads, and time-dependent plasma conditions.

Migrated from hisp package to PFC-Tritium-Transport for better separation of concerns:
- hisp: simulation engine (FESTIM models)
- PFC-Tritium-Transport: data management, reactor configuration, scenarios
"""

import numpy as np
from numpy.typing import NDArray
from .helpers import periodic_step_function, periodic_pulse_function
from scenario import Pulse
import pandas as pd

from typing import Dict
from hisp.bin import Bin


class PlasmaDataHandling:
    _time_to_RISP_data: Dict[str, pd.DataFrame]

    def __init__(
        self,
        pulse_type_to_data: Dict[str, pd.DataFrame],
        path_to_RISP_data: str,
        path_to_ROSP_data: str,
        path_to_RISP_wall_data: str,
    ):
        self.pulse_type_to_data = pulse_type_to_data or {}
        self.path_to_RISP_data = path_to_RISP_data
        self.path_to_ROSP_data = path_to_ROSP_data
        self.path_to_RISP_wall_data = path_to_RISP_wall_data
        # check that the values in pulse_type_to_data are pandas DataFrames
        for value in self.pulse_type_to_data.values():
            if not isinstance(value, pd.DataFrame):
                raise TypeError(
                    f"Expected a pandas DataFrame in pulse_type_to_data, got {type(value)} instead"
                )

        self._time_to_RISP_data = {}

    def get_particle_flux(
        self, pulse: Pulse, bin: Bin, t_rel: float, ion=True
    ) -> float:
        """Returns the particle flux for a given pulse type

        Args:
            pulse: the pulse object
            bin: Bin object
            t_rel: Relative time (in seconds).
                t_rel = t - t_pulse_start where t_pulse_start is the start of the pulse in seconds
            ion (bool, optional): Whether to get ion flux or atom flux. Defaults to True.

        Returns:
            float: particle flux in part/m2/s
        """
        # Use bin_number for CSV bins (convert from 1-based to 0-based index)
        bin_index = bin.bin_number - 1
        
        if ion:
            flux_header = "Flux_Ion"
            # For ion flux: apply ion_scaling_factor from CSV bin
            flux_frac = bin.ion_scaling_factor
        else:
            flux_header = "Flux_Atom"
            # For atom flux: use parsed value directly (no scaling)
            flux_frac = 1.0

        if pulse.pulse_type == "FP":
            flux = self.pulse_type_to_data[pulse.pulse_type][flux_header][bin_index]
        elif pulse.pulse_type == "RISP":
            assert isinstance(
                t_rel, float
            ), f"t_rel should be a float, not {type(t_rel)}"

            t_rel_within_a_single_risp = t_rel % pulse.total_duration

            data = self.RISP_data(bin, t_rel=t_rel_within_a_single_risp)

            flux = data[flux_header]

            # take the single value from the series
            if isinstance(flux, pd.Series):
                if flux.values.size == 0:
                    flux = 0.0
                else:
                    assert (
                        flux.values.size == 1
                    ), f"flux should be a single value, values: {flux.values}"
                    flux = flux.values[0]
        elif pulse.pulse_type == "BAKE":
            flux = 0.0
        else:
            flux = self.pulse_type_to_data[pulse.pulse_type][flux_header][bin_index]

        value = flux * flux_frac

        # Apply pulse-level flux scaling factor
        value = value * pulse.flux_scaling

        # check that value is a float
        assert isinstance(
            value, (float, np.float64)
        ), f"value should be a float, not {type(value)}"

        # add in the step function for the pulse
        total_time_on = pulse.duration_no_waiting
        total_time_pulse = pulse.total_duration

        return periodic_pulse_function(
            t_rel,
            pulse=pulse,
            value=value,
            value_off=0,
        )

    def RISP_data(self, bin: Bin, t_rel: float | int) -> pd.DataFrame:
        """Returns the correct RISP data file for indicated bin

        Args:
            bin: Bin object
            t_rel: relative time (in seconds).
                t_rel = t - t_pulse_start where t_pulse_start is the start of the pulse in seconds

        Returns:
            data: data from correct file as a numpy array
        """
        # Use zero-based bin index for CSV bins (match get_particle_flux)
        bin_index = bin.bin_number - 1
        
        # Determine if it's a divertor based on location
        div = bin.is_divertor
        
        # For CSV bins, determine strike point based on specific modes or locations
        # This can be refined based on your specific CSV data structure
        strike_point = False  # Default to False, can be customized later
        
        if div and strike_point:
            # Use RISP or ROSP data paths (this logic can be refined)
            folder = self.path_to_RISP_data
        elif div:
            # For divertor bins without strike point
            folder = self.path_to_RISP_data
            strike_point = False

        t_rel = int(t_rel)

        if div and strike_point:
            if 0 <= t_rel <= 9:
                key = f"{folder}_1_9"
                if key not in self._time_to_RISP_data.keys():
                    self._time_to_RISP_data[key] = pd.read_csv(
                        f"{folder}/time0.dat", delimiter=","
                    )
                data = self._time_to_RISP_data[key]
            elif 10 <= t_rel <= 98:
                key = f"{folder}_10_98"
                if key not in self._time_to_RISP_data.keys():
                    self._time_to_RISP_data[key] = pd.read_csv(
                        f"{folder}/time10.dat", delimiter=","
                    )
                data = self._time_to_RISP_data[key]
            elif 100 <= t_rel <= 260:
                key = f"{folder}_{t_rel}"
                if key not in self._time_to_RISP_data.keys():
                    self._time_to_RISP_data[key] = pd.read_csv(
                        f"{folder}/time{t_rel}.dat", delimiter=","
                    )
                data = self._time_to_RISP_data[key]
            elif 261 <= t_rel <= 270:
                key = f"{folder}_261_269"
                if key not in self._time_to_RISP_data.keys():
                    self._time_to_RISP_data[key] = pd.read_csv(
                        f"{folder}/time260.dat", delimiter=","
                    )
                data = self._time_to_RISP_data[key]
            else:  # NOTE: so if time is too large a MB transforms into a FW element???
                key = "wall_data"
                if key not in self._time_to_RISP_data.keys():
                    self._time_to_RISP_data[key] = pd.read_csv(
                        self.path_to_RISP_wall_data, delimiter=","
                    )
                data = self._time_to_RISP_data[key]
        else:
            key = "wall_data"
            if key not in self._time_to_RISP_data.keys():
                self._time_to_RISP_data[key] = pd.read_csv(
                    self.path_to_RISP_wall_data, delimiter=","
                )
            data = self._time_to_RISP_data[key]

        data_for_bin = data.loc[data["Bin_Index"] == bin_index]

        # check there is only one row for this bin
        assert (
            data_for_bin.shape[0] <= 1
        ), f"More than one row for bin {bin_index}. t_rel: {t_rel}, div: {div}, strike_point: {strike_point}"
        return data_for_bin

    def get_heat(self, pulse: Pulse, bin: Bin, t_rel: float) -> float:
        """Returns the surface heat flux (W/m2) for a given pulse type

        Args:
            pulse: the pulse object
            bin: CSVBin object
            t_rel: Relative time (in seconds).
                t_rel = t - t_pulse_start where t_pulse_start is the start of the pulse in seconds

        Raises:
            ValueError: if the pulse type is unknown

        Returns:
            the surface heat flux in W/m2
        """
        # Use bin_number for CSV bins
        bin_index = bin.bin_number-1

        if pulse.pulse_type == "RISP":
            t_rel_within_a_single_risp = t_rel % pulse.total_duration
            data = self.RISP_data(bin, t_rel=t_rel_within_a_single_risp)
        elif pulse.pulse_type in self.pulse_type_to_data.keys():
            data = self.pulse_type_to_data[pulse.pulse_type]
        else:
            raise ValueError(f"Invalid pulse type {pulse.pulse_type}")

        if pulse.pulse_type == "FP":
            photon_heat_radiation = 0.11e6  # W/m2
            heat_total = data["heat_total"][bin_index] + photon_heat_radiation 
            heat_ion = data["heat_ion"][bin_index]
            
            # Use ion_scaling_factor as wetted fraction (same logic as original)
            heat_val = heat_total - heat_ion * (1 - bin.ion_scaling_factor)
                
        elif pulse.pulse_type == "RISP":
            photon_radiation_heat = 0.11e6  # W/m2
            
            # For CSV bins - use ion_scaling_factor as wetted fraction
            heat_total = data["heat_total"] + photon_radiation_heat 
            heat_ion = data["heat_ion"]
            heat_val = heat_total - heat_ion * (1 - bin.ion_scaling_factor)

            # if heat_val is an empty pandas Series set it at 0.0 (no heat)
            # otherwise take the single value from the series
            if isinstance(heat_val, pd.Series):
                if heat_val.values.size == 0:
                    heat_val = 0.0
                else:
                    assert (
                        heat_val.values.size == 1
                    ), f"heat_val should be a single value, values: {heat_val.values}"
                    heat_val = heat_val.values[0]
        else:
            heat_val = data["heat_total"][bin_index]

        # Apply pulse-level heat scaling factor
        heat_val = heat_val * pulse.heat_scaling

        # check that heat_val is a float
        assert isinstance(
            heat_val, (float, np.float64)
        ), f"heat_val should be a float, not {type(heat_val)}"

        # add in the step function for the pulse
        total_time_on = pulse.duration_no_waiting
        total_time_pulse = pulse.total_duration

        return periodic_pulse_function(
            t_rel,
            pulse=pulse,
            value=heat_val,
            value_off=0,
        )

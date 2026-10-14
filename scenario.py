import pandas as pd
from typing import List
import warnings
import numpy as np
import sys


class Pulse:
    pulse_type: str
    pulse_def: str
    nb_pulses: int
    ramp_up: float
    steady_state: float
    ramp_down: float
    waiting: float
    timing_flux: List[float]
    timing_heat: List[float]
    fraction: List[float]
    fraction_flux: List[float]
    fraction_heat: List[float]
    steady_STATE: List[float]
    tritium_fraction: float
    heat_scaling: float
    flux_scaling: float

    def __init__(
        self,
        pulse_type: str,
        nb_pulses: int,
        ramp_up: float = 0,
        steady_state: float = 0 ,
        ramp_down: float = 0,
        waiting: float = 0,
        tritium_fraction: float = 0.5,  # tritium fraction = T/D
        transition: List[float] = [],
        steady_STATE: List[float] = [],
        fraction: List[float] = [],
        fraction_flux: List[float] = [],
        fraction_heat: List[float] = [],
        timing_flux: List[float] = [],
        timing_heat: List[float] = [],
        pulse_def: str = 'classic',
        heat_scaling: float = 1.0,  # scaling factor for heat loads
        flux_scaling: float = 1.0,  # scaling factor for particle fluxes
        gdc_ramp_up: float = None,  # GDC sub-pulse ramp-up (for Bake+GDC)
        gdc_steady_state: float = None,  # GDC sub-pulse steady-state (for Bake+GDC)
        gdc_ramp_down: float = None,  # GDC sub-pulse ramp-down (for Bake+GDC)
    ):
        self.pulse_type = pulse_type
        self.nb_pulses = nb_pulses
        self.pulse_def = pulse_def
        if self.pulse_def == 'classic':
            self.ramp_up = ramp_up
            self.steady_state = steady_state
            self.ramp_down = ramp_down
            self.waiting = waiting
            self.transition = []
            self.timing_flux = []
            self.timing_heat = []
            self.fraction = []
            self.fraction_flux = []
            self.fraction_heat = []
            self.steady_STATE = []
        elif self.pulse_def == 'steps':
            self.steady_STATE = steady_STATE
            if len(transition) == len(steady_STATE)+1:
                self.transition = transition
                self.ramp_up = transition[0]             # first value of transition
                self.ramp_down = transition[-1]          # last value of transition
                self.steady_state = sum(steady_STATE)+sum(transition[1:-1])
            else:
                print('ERROR: len(transition) != len(steady_STATE)+1')
                sys.exit('exiting ...')
            if len(fraction) == len(steady_STATE):
                self.fraction = fraction
            else:
                print('ERROR: len(fraction) != len(steady_STATE)')
                sys.exit('exiting ...')
            self.waiting = waiting
        elif self.pulse_def == 'timing':
            timing_flux.sort()
            timing_heat.sort()
            if len(timing_flux) <= 2:
                print('ERROR: len(timing_flux) <= 2')
                print('please use len(timing_flux) >= 3')
                sys.exit('exiting ...')
            else:
                self.timing_flux = timing_flux
            if len(fraction_flux) != len(timing_flux):
                print('ERROR: len(fraction_flux) != len(timing_flux)')
                sys.exit('exiting ...')
            else:
                self.fraction_flux = fraction_flux
            if len(timing_heat) <= 2:
                print('ERROR: len(timing_heat) <= 2')
                print('please use len(timing_heat) >= 3')
                sys.exit('exiting ...')
            else:
                self.timing_heat = timing_heat
            if len(fraction_heat) != len(timing_heat):
                print('ERROR: len(fraction_heat) != len(timing_heat)')
                sys.exit('exiting ...')
            else:
                self.fraction_heat = fraction_heat
            time_heat = np.asarray(self.timing_heat)
            time_flux = np.asarray(self.timing_flux)
            frac_heat = np.asarray(self.fraction_heat)
            frac_flux = np.asarray(self.fraction_flux)
            idx_heat = np.where(frac_heat == 1.0)[0]
            gaps_heat = np.diff(time_heat[idx_heat])
            i_heat = np.argmax(gaps_heat)
            heat_ramp_up_end = time_heat[idx_heat[i_heat]] #largest gap between two "1" values is assumed to be the flattop.
            heat_ramp_down_start = time_heat[idx_heat[i_heat + 1]]
            idx_flux = np.where(frac_flux == 1.0)[0]
            gaps_flux = np.diff(time_flux[idx_flux])
            i_flux = np.argmax(gaps_flux)
            flux_ramp_up_end = time_flux[idx_flux[i_flux]]
            flux_ramp_down_start = time_flux[idx_flux[i_flux + 1]]
            self.ramp_up = max(flux_ramp_up_end, heat_ramp_up_end)
            self.waiting = waiting
            self.ramp_down = max(time_flux[-1], time_heat[-1]) - max(flux_ramp_down_start, heat_ramp_down_start)
            self.steady_state = max(time_flux[-1], time_heat[-1]) - self.ramp_up - self.ramp_down
        self.tritium_fraction = tritium_fraction
        self.heat_scaling = heat_scaling
        self.flux_scaling = flux_scaling
        self.gdc_ramp_up = gdc_ramp_up
        self.gdc_steady_state = gdc_steady_state
        self.gdc_ramp_down = gdc_ramp_down

        # Validate Bake+GDC has sub-timing defined
        if pulse_type == "Bake+GDC":
            if any(v is None for v in (gdc_ramp_up, gdc_steady_state, gdc_ramp_down)):
                raise ValueError(
                    "Bake+GDC pulse requires gdc_ramp_up, gdc_steady_state, "
                    "and gdc_ramp_down to be set."
                )
            gdc_total = gdc_ramp_up + gdc_steady_state + gdc_ramp_down
            bake_active = ramp_up + steady_state + ramp_down
            if gdc_total > bake_active:
                raise ValueError(
                    f"GDC sub-pulse duration ({gdc_total}s) exceeds "
                    f"baking active duration ({bake_active}s)."
                )

    @property
    def total_duration(self) -> float:
        if self.pulse_def == 'classic':
            all_zeros = (
                self.ramp_up == 0
                and self.steady_state == 0
                and self.ramp_down == 0
                and self.waiting == 0
            )
        elif self.pulse_def == 'steps':
            all_zeros = (
                    sum(self.transition) == 0
                    and sum(self.steady_STATE) == 0
                    and self.waiting == 0
                    )
        elif self.pulse_def == 'timing':
            all_zeros = (
                    self.timing_flux[-1] == 0
                    and self.timing_heat[-1] == 0
                    )
        if self.pulse_type == "RISP" and all_zeros:
            msg = "RISP pulse has all zeros for ramp_up, steady_state, ramp_down, waiting. "
            msg += "Setting hardcoded values. Please check the values in the scenario file."
            warnings.warn(msg, UserWarning)
            self.pulse_def = 'classic'
            self.ramp_up = 10
            self.steady_state = 250
            self.ramp_down = 10
            self.waiting = 1530
            self.transition = []
            self.timing_flux = []
            self.timing_heat = []
            self.fraction = []
            self.fraction_flux = []
            self.fraction_heat = []
            self.steady_STATE = []
            tot = self.ramp_up + self.steady_state + self.ramp_down + self.waiting
        elif all_zeros:
            msg = "pulse has all zeros for ramp_up, steady_state, ramp_down, waiting. "
            msg += "Setting hardcoded values. Please check the values in the scenario file."
            warnings.warn(msg, UserWarning)
            self.pulse_def = 'classic'
            self.ramp_up = 10
            self.steady_state = 250
            self.ramp_down = 10
            self.waiting = 1530
            self.transition = []
            self.timing_flux = []
            self.timing_heat = []
            self.fraction = []
            self.fraction_flux = []
            self.fraction_heat = []
            self.steady_STATE = []
            tot = self.ramp_up + self.steady_state + self.ramp_down + self.waiting
        else:
            if self.pulse_def == 'classic':
                tot = self.ramp_up + self.steady_state + self.ramp_down + self.waiting
            elif self.pulse_def == 'steps':
                tot = sum(self.transition) + sum(self.steady_STATE) + self.waiting
            elif self.pulse_def == 'timing':
                tot = max(self.timing_flux[-1] - self.timing_flux[0], self.timing_heat[-1] - self.timing_heat[0]) + self.waiting
        return tot

    @property
    def duration_no_waiting(self) -> float:
        return self.total_duration - self.waiting


class Scenario:
    def __init__(self, pulses: List[Pulse] = None, baking_temp: float = None):
        """Initializes a Scenario object containing several pulses.

        Args:
            pulses: The list of pulses in the scenario. Each pulse is a Pulse object.
            baking_temp: Temperature (K) during baking pulses. Required if any
                pulse has pulse_type="BAKE".
        """
        self._pulses = pulses if pulses is not None else []
        self.baking_temp = baking_temp

        # Validate: if there are BAKE or Bake+GDC pulses, baking_temp must be set
        has_bake = any(p.pulse_type in ("BAKE", "Bake+GDC") for p in self._pulses)
        if has_bake and self.baking_temp is None:
            raise ValueError(
                "Scenario contains BAKE/Bake+GDC pulses but baking_temp was not set. "
                "Pass baking_temp=<value_in_K> to Scenario()."
            )

    @property
    def pulses(self) -> List[Pulse]:
        return self._pulses

    def to_txt_file(self, filename: str):
        df = pd.DataFrame(
            [
                {
                    "pulse_type": pulse.pulse_type,
                    "nb_pulses": pulse.nb_pulses,
                    "ramp_up": pulse.ramp_up,
                    "steady_state": pulse.steady_state,
                    "ramp_down": pulse.ramp_down,
                    "waiting": pulse.waiting,
                    "tritium_fraction": pulse.tritium_fraction,
                    "heat_scaling": pulse.heat_scaling,
                    "flux_scaling": pulse.flux_scaling,
                    "baking_temp": self.baking_temp,
                    "gdc_ramp_up": pulse.gdc_ramp_up,
                    "gdc_steady_state": pulse.gdc_steady_state,
                    "gdc_ramp_down": pulse.gdc_ramp_down,
                }
                for pulse in self.pulses
            ]
        )
        df.to_csv(filename, index=False)

    @staticmethod
    def from_txt_file(filename: str, old_format=False) -> "Scenario":
        if old_format:
            pulses = []
            with open(filename, "r") as f:
                for line in f:
                    # skip first line
                    if line.startswith("#"):
                        continue

                    # skip empty lines
                    if not line.strip():
                        continue

                    # assume this is the format
                    pulse_type, nb_pulses, ramp_up, steady_state, ramp_down, waiting = (
                        line.split()
                    )
                    pulses.append(
                        Pulse(
                            pulse_type=pulse_type,
                            pulse_def = 'classic',
                            nb_pulses=int(nb_pulses),
                            ramp_up=float(ramp_up),
                            steady_state=float(steady_state),
                            ramp_down=float(ramp_down),
                            waiting=float(waiting),
                        )
                    )
            return Scenario(pulses)
        df = pd.read_csv(filename)
        pulses = [
            Pulse(
                pulse_type=row["pulse_type"],
                pulse_def = 'classic',
                nb_pulses=int(row["nb_pulses"]),
                ramp_up=float(row["ramp_up"]),
                steady_state=float(row["steady_state"]),
                ramp_down=float(row["ramp_down"]),
                waiting=float(row["waiting"]),
                tritium_fraction=float(row["tritium_fraction"]),
                heat_scaling=float(row.get("heat_scaling", 1.0)),
                flux_scaling=float(row.get("flux_scaling", 1.0)),
                gdc_ramp_up=float(row["gdc_ramp_up"]) if "gdc_ramp_up" in row and pd.notna(row.get("gdc_ramp_up")) else None,
                gdc_steady_state=float(row["gdc_steady_state"]) if "gdc_steady_state" in row and pd.notna(row.get("gdc_steady_state")) else None,
                gdc_ramp_down=float(row["gdc_ramp_down"]) if "gdc_ramp_down" in row and pd.notna(row.get("gdc_ramp_down")) else None,
            )
            for _, row in df.iterrows()
        ]
        # Read baking_temp from CSV if present as a column (same value in all rows)
        if "baking_temp" in df.columns:
            baking_temp = float(df["baking_temp"].iloc[0])
        else:
            baking_temp = None  # will be validated in Scenario.__init__
        return Scenario(pulses, baking_temp=baking_temp)

    def get_row(self, t: float) -> int:
        """
        Returns the index of the pulse at time t.
        If t is greater than the maximum time in the scenario, a
        warning is raised and the last pulse index is returned.

        Args:
            t: the time in seconds

        Returns:
            the index of the pulse at time t
        """
        current_time = 0
        for i, pulse in enumerate(self.pulses):
            phase_duration = pulse.nb_pulses * pulse.total_duration
            if t < current_time + phase_duration:
                return i
            else:
                current_time += phase_duration

        warnings.warn(
            f"Time t {t} is out of bounds of the scenario file. Valid times are t < {self.get_maximum_time()}",
            UserWarning,
        )
        return i

    def get_pulse(self, t: float) -> Pulse:
        """
        Returns the pulse at time t.
        If t is greater than the maximum time in the scenario, a
        warning is raised and the last pulse is returned.

        Args:
            t: the time in seconds

        Returns:
            Pulse: the pulse at time t
        """
        row_idx = self.get_row(t)
        return self.pulses[row_idx]

    def get_pulse_type(self, t: float) -> str:
        """Returns the pulse type as a string at time t.

        Args:
            t: time in seconds

        Returns:
            pulse type (eg. FP, ICWC, RISP, GDC, BAKE)
        """
        return self.get_pulse(t).pulse_type

    def get_maximum_time(self) -> float:
        """Returns the maximum time of the scenario in seconds.

        Returns:
            the maximum time of the scenario in seconds
        """
        return sum([pulse.nb_pulses * pulse.total_duration for pulse in self.pulses])

    def get_time_start_current_pulse(self, t: float):
        """Returns the time (s) at which the current pulse started.

        Args:
            t: the time in seconds

        Returns:
            the time at which the current pulse started
        """
        pulse_index = self.get_row(t)
        return sum(
            [
                pulse.nb_pulses * pulse.total_duration
                for pulse in self.pulses[:pulse_index]
            ]
        )

    # TODO this is the same as get_time_start_current_pulse, remove
    def get_time_till_row(self, row: int) -> float:
        """Returns the time (s) until the row in the scenario file.

        Args:
            row: the row index in the scenario file

        Returns:
            the time until the row in the scenario file
        """
        return sum(
            [pulse.nb_pulses * pulse.total_duration for pulse in self.pulses[:row]]
        )

    # TODO remove
    def get_pulse_duration_no_waiting(self, row: int) -> float:
        """Returns the total duration (without the waiting time) of a pulse in seconds for a given row in the file.

        Args:
            row: the row index in the scenario file

        Returns:
            the total duration of the pulse in seconds
        """
        return self.pulses[row].duration_no_waiting

    # TODO remove
    def get_pulse_duration(self, row: int) -> float:
        """Returns the total duration of a pulse in seconds for a given row in the file.

        Args:
            row: the row index in the scenario file

        Returns:
            the total duration of the pulse in seconds
        """
        return self.pulses[row].total_duration

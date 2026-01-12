from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class Trap:
    Trap_density: float
    k_0: Optional[float] = None
    E_k: Optional[float] = None
    p_0: Optional[float] = None
    E_p: Optional[float] = None


@dataclass
class Material:
    """Simple material container.

    Expected `material` dict keys (recommended):
        - name: material name (str)
        - Mat_density: float (atoms/m3)
        - D0: float (m2/s)
        - E_D: float (eV)
        - N_traps: int
        - traps: list of dicts with keys: Trap_density, k_0, E_k, p_0, E_p
    """

    name: str
    Mat_density: float
    D0: float
    E_D: float
    N_traps: int = 0
    traps: List[Trap] = field(default_factory=list)
    # Recombination parameters (optional)
    K_R: Optional[float] = None
    E_R: Optional[float] = None
    # Note: no 'extras' field — all known keys are parsed into structured fields

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Material":
        # normalize keys to be tolerant to capitalization and alternate names
        get = lambda *keys, default=None: next((data[k] for k in keys if k in data and data[k] is not None), default)

        name = str(get('name', 'Name', 'material', 'Material', 'Material_name', 'Material name', default='unknown')).strip()
        Mat_density = float(get('Mat_density', 'mat_density', 'Mat density', default=0.0))
        D0 = float(get('D0', 'D_0', default=0.0))
        E_D = float(get('E_D', 'E_D_eV', default=0.0))
        # recombination (optional)
        K_R = _maybe_float(get('K_R', 'K R', default=None))
        E_R = _maybe_float(get('E_R', 'E R', default=None))
        N_traps = int(get('N_traps', 'n_traps', default=0))

        traps_list = []
        # if a 'traps' key already present and is a list, use it
        existing_traps = data.get('traps')
        if isinstance(existing_traps, list):
            for t in existing_traps:
                traps_list.append(Trap(
                    Trap_density=float(t.get('Trap_density', t.get('n', 0.0))),
                    k_0=t.get('k_0'),
                    E_k=t.get('E_k'),
                    p_0=t.get('p_0'),
                    E_p=t.get('E_p'),
                ))
        else:
            # Collect trap indices from keys present in the data. Accept both unsuffixed
            # keys (e.g., 'Trap_density') and suffixed keys ('Trap_density_1', ...).
            trap_keys = ['Trap_density', 'k_0', 'E_k', 'p_0', 'E_p']
            indices = set()
            for key in data.keys():
                for tk in trap_keys:
                    if key == tk:
                        indices.add(1)
                    elif key.startswith(tk + "_"):
                        try:
                            idx = int(key.split("_")[-1])
                            indices.add(idx)
                        except Exception:
                            continue

            # If no explicit trap keys found but N_traps provided, use that
            if not indices and N_traps > 0:
                indices = set(range(1, N_traps + 1))

            for i in sorted(indices):
                # keys may be like 'Trap_density' (unsuffixed) or 'Trap_density_1'
                td_key = f'Trap_density_{i}' if f'Trap_density_{i}' in data else ('Trap_density' if 'Trap_density' in data and i == 1 else None)
                if td_key is None or data.get(td_key) in (None, '', float('nan')):
                    # no trap density for this index -> skip
                    continue
                traps_list.append(Trap(
                    Trap_density=float(data.get(td_key, 0.0)),
                    k_0=_maybe_float(data.get(f'k_0_{i}')) if f'k_0_{i}' in data else _maybe_float(data.get('k_0')) if i == 1 else None,
                    E_k=_maybe_float(data.get(f'E_k_{i}')) if f'E_k_{i}' in data else _maybe_float(data.get('E_k')) if i == 1 else None,
                    p_0=_maybe_float(data.get(f'p_0_{i}')) if f'p_0_{i}' in data else _maybe_float(data.get('p_0')) if i == 1 else None,
                    E_p=_maybe_float(data.get(f'E_p_{i}')) if f'E_p_{i}' in data else _maybe_float(data.get('E_p')) if i == 1 else None,
                ))

        # Return a Material constructed only from the canonical fields and
        # structured traps. Any unknown keys are ignored (no `extras` preserved).
        return cls(
            name=name,
            Mat_density=Mat_density,
            D0=D0,
            E_D=E_D,
            N_traps=len(traps_list),
            traps=traps_list,
            K_R=K_R,
            E_R=E_R,
        )

    def to_dict(self) -> Dict[str, Any]:
        d = {
            'name': self.name,
            'Mat_density': self.Mat_density,
            'D0': self.D0,
            'E_D': self.E_D,
            'K_R': self.K_R,
            'E_R': self.E_R,
            'N_traps': self.N_traps,
            'traps': [t.__dict__ for t in self.traps],
        }
        return d


def _maybe_float(x):
    try:
        if x is None or (isinstance(x, float) and (x != x)):
            return None
        return float(x)
    except Exception:
        return None

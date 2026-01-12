"""Load materials from `input_files/materials.csv` into Material objects.

This loader is intentionally tolerant to column naming variations used in
the materials CSV (e.g., `D0` vs `D_0`, `Mat_density` vs `mat_density`,
repeated trap columns like `Trap_density_1`, `k_0_1`, ...).
"""
from pathlib import Path
from typing import Dict

import pandas as pd

from materials.materials import Material


def _is_nan(x):
    return x is None or (isinstance(x, float) and (x != x))


def load_materials(csv_path: str | Path = "input_files/materials.csv") -> Dict[str, Material]:
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"Materials CSV not found: {csv_path}")

    # Try to detect two common layouts by reading raw cells (header=None):
    # 1) Vertical: standard CSV where each ROW is one material and columns are fields.
    # 2) Horizontal/transposed: each material occupies a pair of columns (key,value), repeated
    #    across the sheet (often with blank separator columns between blocks).

    df_raw = pd.read_csv(csv_path, header=None, dtype=object)
    # Temporarily collect raw flat dicts per material name (to allow merging blocks)
    flats_per_material: Dict[str, list[Dict[str, object]]] = {}

    # Inspect the first row of raw cells: presence of 'Material_name' tokens indicates
    # the horizontal/transposed layout used in your CSV example. For the fixed layout
    # we expect blocks of two columns (key, value) repeated across the sheet. When
    # the file follows the fixed order, we can deterministically parse each block by
    # reading rows in the expected parameter order.
    first_row = [str(x).strip().lower() if pd.notna(x) else '' for x in df_raw.iloc[0].tolist()]
    arr = df_raw.values
    nrows, ncols = arr.shape

    # Find candidate key columns where the first row indicates a material block
    block_cols = [i for i, v in enumerate(first_row) if v in ('material_name', 'material name')]

    if block_cols:
        # Deterministic parser using the known input order
        expected_header_order = [
            'Material_name', 'Mat_density', 'D0', 'E_D', 'K_R', 'E_R', 'N_traps'
        ]
        trap_block_order = ['Trap_density', 'k_0', 'E_k', 'p_0', 'E_p']

        for col in block_cols:
            val_col = col + 1
            flat: Dict[str, object] = {}
            r = 0
            # read the expected header order in sequence; if a row does not match the expected
            # key label we still read the value (tolerant), but we advance the row pointer.
            for hdr in expected_header_order:
                if r >= nrows:
                    break
                key_cell = arr[r, col]
                value_cell = arr[r, val_col] if val_col < ncols else None
                # store using canonical header name
                flat[hdr] = None if _is_nan(value_cell) else value_cell
                r += 1

            # determine number of traps (may be string); coerce to int if possible
            try:
                N_traps_val = flat.get('N_traps')
                N_traps = int(float(N_traps_val)) if N_traps_val is not None else 0
            except Exception:
                N_traps = 0

            # read traps: each trap is represented by trap_block_order rows
            for ti in range(1, N_traps + 1):
                for tk in trap_block_order:
                    if r >= nrows:
                        break
                    value_cell = arr[r, val_col] if val_col < ncols else None
                    # name numbered trap keys: Trap_density_1, k_0_1, ...
                    flat_key = f"{tk}_{ti}"
                    flat[flat_key] = None if _is_nan(value_cell) else value_cell
                    r += 1

            # store this flat dict under the detected material name (from Material_name)
            mat_name = flat.get('Material_name') or flat.get('Material') or flat.get('name')
            if mat_name is None:
                # fallback: try to read the value from the material name cell if present elsewhere
                # search the column for a first non-empty value in the value column
                for rr in range(nrows):
                    v = arr[rr, val_col] if val_col < ncols else None
                    if not _is_nan(v) and str(v).strip() != '':
                        mat_name = str(v).strip()
                        break
            if mat_name is None:
                mat_name = f"material_col_{col}"

            flats_per_material.setdefault(str(mat_name), []).append(flat)

    # If nothing found using markers, try a fallback: interpret every pair of columns as a material block
    if not flats_per_material:
        for col in range(0, ncols - 1, 2):
            flat = {}
            counts = {}
            trap_key_set = {'Trap_density', 'k_0', 'E_k', 'p_0', 'E_p'}
            for r in range(nrows):
                key = arr[r, col]
                val = arr[r, col + 1] if col + 1 < ncols else None
                if _is_nan(key) or str(key).strip() == '':
                    continue
                key_s = str(key).strip()
                if key_s in trap_key_set:
                    counts[key_s] = counts.get(key_s, 0) + 1
                    new_key = f"{key_s}_{counts[key_s]}"
                else:
                    new_key = key_s
                flat[new_key] = None if _is_nan(val) else val
                if flat:
                    # name detection: prefer explicit 'Material_name' or 'Material' keys
                    name_guess = None
                    for k in ('Material_name', 'Material', 'name', 'Name'):
                        if k in flat and flat[k] is not None:
                            name_guess = str(flat[k]).strip()
                            break
                    if not name_guess:
                        # fallback to column index label
                        name_guess = f"material_col_{col}"
                    flats_per_material.setdefault(name_guess, []).append(flat)

    # Merge collected flats per material name into a single flat dict per material
    materials: Dict[str, Material] = {}
    trap_key_set = {'Trap_density', 'k_0', 'E_k', 'p_0', 'E_p'}
    for name, flats in flats_per_material.items():
        merged: Dict[str, object] = {}
        trap_counts: Dict[str, int] = {}
        for flat in flats:
            for k, v in flat.items():
                if k in trap_key_set or any(k.startswith(tk + '_') for tk in trap_key_set):
                    # normalize trap keys: if key already suffixed, keep as-is; otherwise number
                    base = k.split('_')[0]
                    if base in trap_key_set:
                        # if already suffixed like Trap_density_2, keep numeric suffix
                        if '_' in k:
                            # ensure no collision
                            merged[k] = v
                        else:
                            # unsuffixed trap key -> assign next index
                            trap_counts[base] = trap_counts.get(base, 0) + 1
                            merged[f"{base}_{trap_counts[base]}"] = v
                    else:
                        merged[k] = v
                else:
                    # non-trap key: prefer first non-null value
                    if k not in merged or merged.get(k) is None:
                        merged[k] = v

        # Ensure the material has a name in the merged dict
        if 'Material_name' not in merged and 'Material' not in merged and 'name' not in merged:
            merged['Material_name'] = name

        mat = Material.from_dict(merged)
        materials[mat.name] = mat

    return materials

    # If not horizontal, attempt vertical layout reading with header row
    df = pd.read_csv(csv_path, header=0)
    for _, row in df.iterrows():
        row_dict = {k: (v if pd.notna(v) else None) for k, v in row.to_dict().items()}
        mat = Material.from_dict(row_dict)
        materials[mat.name] = mat

    return materials


if __name__ == "__main__":
    m = load_materials()
    print(f"Loaded materials: {list(m.keys())}")

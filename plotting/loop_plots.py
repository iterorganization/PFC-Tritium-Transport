
import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import re

# ----------- CONFIG -----------
RESULTS_DIR = Path("../results_test_adri_csv")
PLOTS_DIR = Path("./plots_test_adri_csv")
FIGSIZE = (5.5, 4.5)
LEFT_XLIM_HOURS = 0.05
RIGHT_XLIM_HOURS = 250
TOP_YLABEL = "Tritium Inventory (atms/m^2)"
# ------------------------------

def extract_bin_from_name(name: str):
    m = re.search(r"bin[_\- ]?(\d+)", name)
    return m.group(1) if m else None

def parse_filename(stem: str):
    # Determine component: wall or divertor
    component = "wall" if "wall" in stem else "divertor"
    # Extract bin number
    bin_match = re.search(r"bin[_\- ]?(\d+)", stem)
    bin_id = bin_match.group(1) if bin_match else None
    # Extract sub-bin description if present
    sub_bin_match = re.search(r"sub[_\- ]?bin[_\- ]?(.*)", stem)
    sub_bin_desc = sub_bin_match.group(1).replace("_", " ") if sub_bin_match else ""
    return component, bin_id, sub_bin_desc

def get_material(data):
    traps = [k for k in data.keys() if "trap" in k.lower()]
    return "Tungsten" if len(traps) == 4 else "Boron"

def main():
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    json_files = sorted(RESULTS_DIR.glob("*.json"))
    if not json_files:
        print(f"[WARN] No JSON files found in {RESULTS_DIR.resolve()}")
        return

    for jf in json_files:
        try:
            with open(jf, "r") as f:
                data = json.load(f)

            if "t" not in data:
                print(f"[WARN] Skipping {jf.name}: missing 't' array.")
                continue

            # Time in hours
            t_hours = np.array(data["t"], dtype=float) / 3600.0

            # Matplotlib figure with two stacked subplots
            fig, (ax_top, ax_bottom) = plt.subplots(
                2, 1, sharex=True, figsize=FIGSIZE, height_ratios=[3, 1]
            )

            total_T = None
            total_D = None

            # Iterate over all series
            for key, values in data.items():
                if key == "t":
                    continue

                # Handle temperature_at_x0 which is stored as direct array
                if key == "temperature_at_x0":
                    arr = np.array(values, dtype=float)
                    ax_bottom.plot(t_hours, arr, label="Surface temperature, K", color="tab:red")
                    continue

                if isinstance(values, dict) and "data" in values:
                    arr = np.array(values["data"], dtype=float)

                    # Initialize totals lazily
                    if total_T is None:
                        total_T = np.zeros_like(arr)
                        total_D = np.zeros_like(arr)

                    # Sum totals (exclude flux-like keys)
                    if "flux" not in key.lower():
                        if ("T" in key):
                            total_T += arr
                        # Only count pure D (avoid double counting if key has both D and T)
                        if ("D" in key) and ("T" not in key):
                            total_D += arr

                    # Top panel: plot individual series except T, D, and flux
                    if key != "T" and ("D" not in key) and ("flux" not in key.lower()):
                        ax_top.plot(t_hours, arr, label=f"{key}")

            # Plot total T
            if total_T is not None:
                ax_top.plot(t_hours, total_T, label="Total T", linestyle='-', linewidth=2, color='black')

            # ---- Formatting (top) ----
            ax_top.set_xscale("log")
            ax_top.set_xlim(left=LEFT_XLIM_HOURS, right=RIGHT_XLIM_HOURS)
            ax_top.set_ylabel(TOP_YLABEL)
            ax_top.grid(which="both", linestyle="--", linewidth=0.5)
            ax_top.legend(loc='upper left')

            # Build title
            stem = jf.stem
            component, bin_id, sub_bin_desc = parse_filename(stem)
            material = get_material(data)
            title_parts = [material, component]
            if bin_id:
                title_parts.append(f"bin {bin_id}")
            if sub_bin_desc:
                title_parts.append(sub_bin_desc)
            title = " ".join(title_parts)
            ax_top.set_title(title)

            # ---- Formatting (bottom) ----
            ax_bottom.set_xlabel("Time (hours)")
            ax_bottom.grid(which="both", linestyle="--", linewidth=0.5)

            plt.tight_layout()

            # Save outputs
            out_png = PLOTS_DIR / f"{stem}.png"
            fig.savefig(out_png, dpi=300, bbox_inches="tight")
            plt.close(fig)

            print(f"[OK] Saved {out_png.name}")

        except Exception as e:
            print(f"[ERROR] Failed processing {jf.name}: {e}")

if __name__ == "__main__":
    main()

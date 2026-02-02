import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import re
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

# ----------- CONFIG -----------
RESULTS_DIR = Path("../results_CV36ST_v1_2")
PLOTS_DIR = Path("./plots_CV36ST_v1_2")
FIGSIZE = (12, 4.5)
TOP_YLABEL = "Tritium Inventory (atoms/m²)"
# ------------------------------

# FPO phases timing (in hours)
FPO_PHASES = [
    {'fpo': 1, 'start': 0.0, 'end': 591.8},
    {'fpo': 2, 'start': 759.8, 'end': 1471.5},
    {'fpo': 3, 'start': 1639.5, 'end': 2229.5},
    {'fpo': 4, 'start': 2397.5, 'end': 4749.1},
    {'fpo': 5, 'start': 4917.1, 'end': 7262.2},
]

# BAKE phases timing (in hours)
BAKE_PHASES = [
    {'start': 591.8, 'end': 759.8},
    {'start': 1471.5, 'end': 1639.5},
    {'start': 2229.5, 'end': 2397.5},
    {'start': 4749.1, 'end': 4917.1},
    {'start': 7262.2, 'end': 7430.2},
]

# FPO colors (alternating light shading)
FPO_COLORS = ['lightblue', 'lightgreen', 'lightyellow', 'lightcoral', 'plum']

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

def add_fpo_shading(ax, y_max):
    """Add shading for FPO phases and BAKE phases"""
    # Add FPO phase shading
    for i, phase in enumerate(FPO_PHASES):
        ax.axvspan(phase['start'], phase['end'], 
                   alpha=0.15, color=FPO_COLORS[i], zorder=0)
        # Add FPO label in the middle of the phase
        mid_point = (phase['start'] + phase['end']) / 2
        ax.text(mid_point, y_max * 0.95, f"FPO {phase['fpo']}", 
                ha='center', va='top', fontsize=9, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                         edgecolor=FPO_COLORS[i], alpha=0.8))
    
    # Add BAKE phase shading (darker, with hatch pattern)
    for phase in BAKE_PHASES:
        ax.axvspan(phase['start'], phase['end'], 
                   alpha=0.25, color='gray', hatch='///', zorder=0)

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
            
            # Get temperature data
            temperature = None
            if "temperature_at_x0" in data:
                temperature = np.array(data["temperature_at_x0"], dtype=float)

            # Collect all data series
            total_T = None
            total_D = None
            t_trap_data = {}  # Store T trap data for second plot
            
            for key, values in data.items():
                if key == "t" or key == "temperature_at_x0":
                    continue

                if isinstance(values, dict) and "data" in values:
                    arr = np.array(values["data"], dtype=float)

                    # Initialize totals lazily
                    if total_T is None:
                        total_T = np.zeros_like(arr)
                        total_D = np.zeros_like(arr)

                    # Sum totals (exclude flux-like keys and mobile T)
                    if "flux" not in key.lower() and key != "T":
                        if "T" in key:
                            total_T += arr
                            t_trap_data[key] = arr
                        # Count pure D (avoid double counting if key has both D and T)
                        if ("D" in key) and ("T" not in key):
                            total_D += arr

            # ===== PLOT 1: T and D totals =====
            fig1, (ax1_top, ax1_bottom) = plt.subplots(
                2, 1, sharex=True, figsize=FIGSIZE, height_ratios=[3, 1]
            )

            # Plot total T and total D
            if total_T is not None:
                ax1_top.plot(t_hours, total_T, label="Total T", linestyle='-', linewidth=2.5, color='black')
            if total_D is not None:
                ax1_top.plot(t_hours, total_D, label="Total D", linestyle='-', linewidth=2.5, color='darkblue')

            # Get y-axis limits for shading
            y_min, y_max = ax1_top.get_ylim()
            add_fpo_shading(ax1_top, y_max)
            ax1_top.set_ylim(y_min, y_max)

            # Formatting (top)
            ax1_top.set_xlim(left=0, right=t_hours[-1])
            ax1_top.set_ylabel(TOP_YLABEL)
            ax1_top.grid(which="both", linestyle="--", linewidth=0.5, alpha=0.5)
            ax1_top.legend(loc='upper left', fontsize=8)

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
            ax1_top.set_title(title + " - Total T and D", fontsize=12, fontweight='bold')

            # Formatting (bottom)
            if temperature is not None:
                ax1_bottom.plot(t_hours, temperature, label="Surface temperature (K)", color="tab:red")
            ax1_bottom.set_xlabel("Time (hours)", fontsize=10)
            ax1_bottom.set_ylabel("Temperature (K)", fontsize=9)
            ax1_bottom.grid(which="both", linestyle="--", linewidth=0.5, alpha=0.5)
            ax1_bottom.legend(loc='upper right', fontsize=8)
            
            y_min_bot, y_max_bot = ax1_bottom.get_ylim()
            add_fpo_shading(ax1_bottom, y_max_bot)
            ax1_bottom.set_ylim(y_min_bot, y_max_bot)

            plt.tight_layout()

            # Save plot 1
            out_png1 = PLOTS_DIR / f"{stem}_T_and_D.png"
            fig1.savefig(out_png1, dpi=300, bbox_inches="tight")
            plt.close(fig1)
            print(f"[OK] Saved {out_png1.name}")

            # ===== PLOT 2: T with traps =====
            fig2, (ax2_top, ax2_bottom) = plt.subplots(
                2, 1, sharex=True, figsize=FIGSIZE, height_ratios=[3, 1]
            )

            # Plot individual T traps
            for key, arr in t_trap_data.items():
                ax2_top.plot(t_hours, arr, label=f"{key}")
            
            # Plot total T
            if total_T is not None:
                ax2_top.plot(t_hours, total_T, label="Total T", linestyle='-', linewidth=2.5, color='black')

            # Get y-axis limits for shading
            y_min, y_max = ax2_top.get_ylim()
            add_fpo_shading(ax2_top, y_max)
            ax2_top.set_ylim(y_min, y_max)

            # Formatting (top)
            ax2_top.set_xlim(left=0, right=t_hours[-1])
            ax2_top.set_ylabel(TOP_YLABEL)
            ax2_top.grid(which="both", linestyle="--", linewidth=0.5, alpha=0.5)
            ax2_top.legend(loc='upper left', fontsize=8)
            ax2_top.set_title(title + " - T with traps", fontsize=12, fontweight='bold')

            # Formatting (bottom)
            if temperature is not None:
                ax2_bottom.plot(t_hours, temperature, label="Surface temperature (K)", color="tab:red")
            ax2_bottom.set_xlabel("Time (hours)", fontsize=10)
            ax2_bottom.set_ylabel("Temperature (K)", fontsize=9)
            ax2_bottom.grid(which="both", linestyle="--", linewidth=0.5, alpha=0.5)
            ax2_bottom.legend(loc='upper right', fontsize=8)
            
            y_min_bot, y_max_bot = ax2_bottom.get_ylim()
            add_fpo_shading(ax2_bottom, y_max_bot)
            ax2_bottom.set_ylim(y_min_bot, y_max_bot)

            plt.tight_layout()

            # Save plot 2
            out_png2 = PLOTS_DIR / f"{stem}_T_with_traps.png"
            fig2.savefig(out_png2, dpi=300, bbox_inches="tight")
            plt.close(fig2)
            print(f"[OK] Saved {out_png2.name}")

        except Exception as e:
            print(f"[ERROR] Failed processing {jf.name}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()

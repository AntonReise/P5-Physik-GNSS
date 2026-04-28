"""
Pass 4 — sky plots side by side, with and without C/N0 filter.

The cumulative sky plot from pass 3 shows every Status record over the
whole session, including sats the phone *knows about* (from almanac)
but is not actually receiving.  Filtering to C/N0 >= 25 dB-Hz
collapses to the satellites that are physically being decoded — which
is what the GnssLogger app shows in its sky-view at any instant.

Output:
- 04_skyplot_compare.png  (2x2 grid: hilltop/urban x all/filtered)
"""
from __future__ import annotations
import os
from pathlib import Path

_CACHE = Path(__file__).resolve().parents[1] / "cache"
os.environ.setdefault("MPLCONFIGDIR", str(_CACHE / "mpl"))
os.environ.setdefault("XDG_CACHE_HOME", str(_CACHE / "xdg"))

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

import sys
sys.path.insert(0, str(Path(__file__).parent))
from importlib import import_module
mod3 = import_module("03_raw_overview")  # reuse parse_status_records, CONST_COLORS

ROOT = Path("/Users/anton/Projects/P5 Physik")
PLOTS = ROOT / "analysis" / "plots"

DATASETS = {
    "hilltop (open sky)":       ROOT / "GNSSLogger Messurments ON (No RINIX, only NMEA), Outdoor Hilltop, ~180 Degree open sky" / "gnss_log_2026_04_26_16_34_46.txt",
    "urban canyon (raw on)":    ROOT / "GNSSLogger Messurments ON Urban Canyon" / "gnss_log_2026_04_27_18_19_26.txt",
}

CN0_THRESHOLD = 25.0   # dB-Hz — "actually being received"


def make_skyplot(ax, df, title, color_by_const=False, point_size=4):
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    az = np.deg2rad(df["AzimuthDegrees"].to_numpy())
    r  = 90.0 - df["ElevationDegrees"].to_numpy()
    if color_by_const:
        for c in df["constellation"].unique():
            sub = df[df["constellation"] == c]
            ax.scatter(np.deg2rad(sub["AzimuthDegrees"]),
                       90 - sub["ElevationDegrees"],
                       s=point_size, alpha=0.7,
                       color=mod3.CONST_COLORS.get(c, "grey"),
                       label=c)
        ax.legend(loc="lower right", fontsize=8, bbox_to_anchor=(1.25, -0.10))
    else:
        sc = ax.scatter(az, r, c=df["Cn0DbHz"].to_numpy(), s=point_size,
                        cmap="viridis", vmin=10, vmax=45, alpha=0.6)
        plt.colorbar(sc, ax=ax, fraction=0.046, label="C/N₀ [dB-Hz]")
    ax.set_rlim(0, 90)
    ax.set_rticks([15, 30, 45, 60, 75])
    ax.set_yticklabels(["75°", "60°", "45°", "30°", "15°"])
    ax.set_title(title, pad=12)


def main():
    fig = plt.figure(figsize=(16, 14))
    gs = fig.add_gridspec(2, 2, hspace=0.35, wspace=0.30)

    sessions = {name: mod3.parse_status_records(p) for name, p in DATASETS.items()}

    for col, (name, df) in enumerate(sessions.items()):
        # Top row: ALL records (no filter)
        ax = fig.add_subplot(gs[0, col], projection="polar")
        make_skyplot(ax, df,
                     f"{name}\nALL Status records  (n={len(df)})\n"
                     f"includes sats with C/N₀ ≈ 0 (NLOS / blocked)")

        # Bottom row: filtered to C/N0 >= threshold
        ax = fig.add_subplot(gs[1, col], projection="polar")
        df_f = df[df["Cn0DbHz"] >= CN0_THRESHOLD]
        n_sats = df_f.groupby(["constellation","Svid"]).ngroups
        make_skyplot(ax, df_f,
                     f"{name}\nC/N₀ ≥ {CN0_THRESHOLD:.0f} dB-Hz only  "
                     f"(n={len(df_f)}, {n_sats} unique sats)\n"
                     "≈ what the GnssLogger app shows live",
                     color_by_const=True, point_size=8)

    fig.suptitle(
        "Sky plots: cumulative over the whole session\n"
        "Top row: every Status record (incl. NLOS / silent sats).  "
        "Bottom row: only sats actually being received (C/N₀ ≥ "
        f"{CN0_THRESHOLD:.0f} dB-Hz).\n"
        "In urban canyon (right column, bottom) the strip-of-sky aligned with the street should be visible.",
        fontsize=12, y=0.995,
    )
    out = PLOTS / "04_skyplot_compare.png"
    fig.savefig(out, dpi=140, bbox_inches="tight")
    print(f"wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

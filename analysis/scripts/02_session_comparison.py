"""
Pass 2 — single comparison figure: all three GNSS-fix sessions side by side
on a common ENU axis range, plus a small bar chart of σ values + DRMS.

Run after 01_fix_overview.py.
"""
from __future__ import annotations
import os
from pathlib import Path

_CACHE = Path(__file__).resolve().parents[1] / "cache"
os.environ.setdefault("MPLCONFIGDIR", str(_CACHE / "mpl"))
os.environ.setdefault("XDG_CACHE_HOME", str(_CACHE / "xdg"))

import numpy as np
import matplotlib.pyplot as plt
import gnss_lib_py as glp
import pymap3d as pm

ROOT = Path("/Users/anton/Projects/P5 Physik")
PLOTS = ROOT / "analysis" / "plots"

DATASETS = {
    "hilltop\n(open sky)":      ROOT / "GNSSLogger Messurments ON (No RINIX, only NMEA), Outdoor Hilltop, ~180 Degree open sky" / "gnss_log_2026_04_26_16_34_46.txt",
    "urban canyon\n(raw on)":   ROOT / "GNSSLogger Messurments ON Urban Canyon" / "gnss_log_2026_04_27_18_19_26.txt",
    "urban canyon\n(force on)": ROOT / "GNSSLogger Messurments Off, Force messurments On Urban Canyon" / "gnss_log_2026_04_27_18_32_22.txt",
}


def load_enu(path: Path):
    nav = glp.AndroidRawFixes(str(path))
    nav = nav.where("fix_provider", "gnss")
    lat = np.asarray(nav["lat_rx_deg"]).ravel()
    lon = np.asarray(nav["lon_rx_deg"]).ravel()
    alt = np.asarray(nav["alt_rx_m"]).ravel()
    rep = np.asarray(nav["AccuracyMeters"]).ravel()
    e, n, u = pm.geodetic2enu(lat, lon, alt, lat.mean(), lon.mean(), alt.mean())
    return dict(e=np.asarray(e), n=np.asarray(n), u=np.asarray(u), rep=rep)


def stats(d):
    se = d["e"].std(ddof=1); sn = d["n"].std(ddof=1); su = d["u"].std(ddof=1)
    drms = np.sqrt(se**2 + sn**2)
    horiz = np.hypot(d["e"], d["n"])
    return dict(se=se, sn=sn, su=su, drms=drms, cep50=np.median(horiz),
                r95=np.quantile(horiz, 0.95), rms_h=np.sqrt(np.mean(horiz**2)),
                rep_mean=float(np.mean(d["rep"])))


def main():
    sessions = {n: load_enu(p) for n, p in DATASETS.items()}
    metas = {n: stats(d) for n, d in sessions.items()}

    # Common axis range (use max from any session for fair visual comparison)
    lim = max(max(abs(d["e"]).max(), abs(d["n"]).max()) for d in sessions.values()) * 1.1

    fig = plt.figure(figsize=(15, 9))
    gs = fig.add_gridspec(2, 3, height_ratios=[2.3, 1])

    # Top row: scatter plots
    for i, (name, d) in enumerate(sessions.items()):
        ax = fig.add_subplot(gs[0, i])
        sc = ax.scatter(d["e"], d["n"], s=8, alpha=0.5,
                        c=np.arange(len(d["e"])), cmap="viridis")
        ax.set_aspect("equal")
        ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim)
        ax.axhline(0, lw=0.5, c="grey"); ax.axvline(0, lw=0.5, c="grey")
        ax.grid(True, alpha=0.3)
        ax.set_xlabel("East [m] vs session mean")
        if i == 0:
            ax.set_ylabel("North [m] vs session mean")
        m = metas[name]
        ax.set_title(f"{name}\n"
                     f"σE={m['se']:.2f}  σN={m['sn']:.2f}  σE/σN={m['se']/m['sn']:.2f}\n"
                     f"DRMS={m['drms']:.2f}  R95={m['r95']:.2f}",
                     fontsize=10)

    # Bottom row: bar chart of all stats side by side
    labels = list(sessions.keys())
    metrics = ["se", "sn", "su", "drms", "cep50", "r95", "rep_mean"]
    metric_pretty = ["σ_E", "σ_N", "σ_U", "DRMS", "CEP50", "R95", "phone\nreported"]
    x = np.arange(len(metrics))
    w = 0.27
    ax_bar = fig.add_subplot(gs[1, :])
    colors = ["#1b9e77", "#d95f02", "#7570b3"]
    for i, name in enumerate(labels):
        m = metas[name]
        vals = [m[k] for k in metrics]
        bars = ax_bar.bar(x + (i - 1) * w, vals, w,
                          label=name.replace("\n", " "), color=colors[i])
        for bar, v in zip(bars, vals):
            ax_bar.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                        f"{v:.1f}", ha="center", va="bottom", fontsize=8)
    ax_bar.set_xticks(x)
    ax_bar.set_xticklabels(metric_pretty)
    ax_bar.set_ylabel("metres")
    ax_bar.set_title("Per-session statistics")
    ax_bar.legend(loc="upper left", fontsize=9)
    ax_bar.grid(True, axis="y", alpha=0.3)

    fig.suptitle("Phone-reported fix scatter: open sky vs. urban canyon  "
                 "(Realme RMX3393, single-frequency)", fontsize=12)
    fig.tight_layout()
    out = PLOTS / "02_session_comparison.png"
    fig.savefig(out, dpi=140)
    print(f"wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

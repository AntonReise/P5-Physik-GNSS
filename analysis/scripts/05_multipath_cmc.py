"""
Pass 5 — Code-Minus-Carrier (CMC) — direct measurement of code multipath.

CMC = ρ_code  - φ_carrier  ≈  2·I + (M_code - M_phase) - N·λ
After per-arc linear detrending (removes Nλ + slow ionospheric drift),
the residual is dominated by code multipath:  σ(CMC_resid) ≈ |M_code|.

For each (gnss_id, sv_id):
- sort by gps_millis
- detect arcs by AccumulatedDeltaRangeState bits 2 (RESET) | 4 (CYCLE_SLIP)
  and by time gaps > 5 s
- per arc, fit linear trend, take residual
- aggregate σ(residual) per sat

Outputs:
- 05_cmc_per_sat.png      per-sat CMC residual time-series, hilltop vs urban
- 05_cmc_summary.png      box plot of σ(CMC) per sat, both sessions
- 05_cmc_per_sat.csv      per-sat statistics
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
import gnss_lib_py as glp

ROOT = Path("/Users/anton/Projects/P5 Physik")
PLOTS = ROOT / "analysis" / "plots"

DATASETS = {
    "hilltop":      ROOT / "GNSSLogger Messurments ON (No RINIX, only NMEA), Outdoor Hilltop, ~180 Degree open sky" / "gnss_log_2026_04_26_16_34_46.txt",
    "urban_raw_on": ROOT / "GNSSLogger Messurments ON Urban Canyon" / "gnss_log_2026_04_27_18_19_26.txt",
}

CONST_COLORS = {
    "gps":      "#1f77b4",
    "galileo":  "#2ca02c",
    "glonass":  "#d62728",
    "beidou":   "#ff7f0e",
    "qzss":     "#9467bd",
    "sbas":     "#8c564b",
    "unknown":  "#7f7f7f",
}

# AccumulatedDeltaRangeState bits
ADR_VALID            = 1
ADR_RESET            = 2
ADR_CYCLE_SLIP       = 4


def load_cmc_table(path: Path) -> pd.DataFrame:
    raw = glp.AndroidRawGnss(input_path=str(path),
                             filter_measurements=True,
                             measurement_filters={"sv_time_uncertainty": 500.},
                             verbose=False)
    df = pd.DataFrame({
        "t_ms":     np.asarray(raw["gps_millis"]).ravel(),
        "gnss_id":  np.asarray(raw["gnss_id"]).ravel(),
        "sv_id":    np.asarray(raw["sv_id"]).ravel(),
        "pr_m":     np.asarray(raw["raw_pr_m"]).ravel(),
        "adr_m":    np.asarray(raw["accumulated_delta_range_m"]).ravel(),
        "adr_state":np.asarray(raw["AccumulatedDeltaRangeState"]).ravel(),
        "cn0":      np.asarray(raw["cn0_dbhz"]).ravel(),
    })
    # Sane PR range only (drop the time-of-week wrapped Galileo etc.)
    df = df[(df["pr_m"] > 1.5e7) & (df["pr_m"] < 5e7)]
    # Need ADR_VALID bit set
    df = df[(df["adr_state"] & ADR_VALID) != 0]
    df["t_s"] = (df["t_ms"] - df["t_ms"].min()) / 1000.0
    return df.sort_values(["gnss_id", "sv_id", "t_s"]).reset_index(drop=True)


def cmc_per_sat(df: pd.DataFrame):
    """Yield (key, arc_df) for each continuous arc per (gnss_id,sv_id)."""
    for (gid, sid), sub in df.groupby(["gnss_id", "sv_id"]):
        sub = sub.copy().sort_values("t_s").reset_index(drop=True)
        # Mark arc breaks from explicit flags and time gaps
        reset_mask = (sub["adr_state"] & (ADR_RESET | ADR_CYCLE_SLIP)) != 0
        gap_mask = sub["t_s"].diff().fillna(0) > 5.0
        # Add automatic cycle-slip detection: if Δ(pr - adr) jumps by more than
        # 5 m between consecutive epochs (impossible from physics for a static
        # receiver in 1 s), it's an unreported cycle slip.
        cmc_raw_init = sub["pr_m"] - sub["adr_m"]
        jump_mask = cmc_raw_init.diff().abs() > 5.0
        arc_id = (reset_mask | gap_mask | jump_mask).cumsum()
        sub["arc"] = arc_id
        sub["cmc_raw"] = cmc_raw_init
        residuals = []
        for arc, g in sub.groupby("arc"):
            if len(g) < 8:                       # need a few samples
                residuals.append(pd.Series(np.nan, index=g.index))
                continue
            x = g["t_s"].to_numpy()
            y = g["cmc_raw"].to_numpy()
            a, b = np.polyfit(x, y, 1)
            res = y - (a * x + b)
            # Reject pathological arcs (still > 30 m residual after detrend
            # = obvious slip we missed, or signal-corrupt PR)
            if np.nanstd(res) > 15.0:
                residuals.append(pd.Series(np.nan, index=g.index))
                continue
            residuals.append(pd.Series(res, index=g.index))
        if not residuals:
            continue
        sub["cmc_resid"] = pd.concat(residuals).sort_index()
        sub = sub.dropna(subset=["cmc_resid"])
        if len(sub) < 10:
            continue
        yield (gid, sid), sub


def main():
    sessions = {n: load_cmc_table(p) for n, p in DATASETS.items()}

    # --- Per-sat statistics
    rows = []
    sat_data = {}
    for sname, df in sessions.items():
        sat_data[sname] = {}
        for (gid, sid), arc_df in cmc_per_sat(df):
            sigma = float(arc_df["cmc_resid"].std(ddof=1))
            n = len(arc_df)
            cn0_mean = float(arc_df["cn0"].mean())
            n_arcs = arc_df["arc"].nunique()
            rows.append(dict(session=sname, gnss=gid, sv=int(sid), n=n,
                             n_arcs=n_arcs, cn0_mean=cn0_mean, sigma_cmc=sigma))
            sat_data[sname][(gid, int(sid))] = arc_df
    summary = pd.DataFrame(rows)
    summary.to_csv(PLOTS / "05_cmc_per_sat.csv", index=False)
    print("=== σ(CMC) per session, summary ===")
    print(summary.groupby("session")["sigma_cmc"]
          .describe(percentiles=[0.25, 0.5, 0.75, 0.95]).round(2)
          .to_string())
    print()
    print("=== σ(CMC) per session per constellation ===")
    print(summary.groupby(["session", "gnss"])["sigma_cmc"]
          .agg(["count", "median", "mean", "max"]).round(2).to_string())

    # --- Plot 1: per-sat residual traces, hilltop vs urban (top 8 by sigma in each)
    fig, axes = plt.subplots(2, 1, figsize=(14, 10), sharex=False)
    for i, sname in enumerate(sessions.keys()):
        ax = axes[i]
        sat_sigmas = (summary[summary["session"] == sname]
                      .sort_values("sigma_cmc", ascending=False))
        # Pick top 8 worst (multipath signature) + 2 best (clean)
        worst = sat_sigmas.head(8)
        best  = sat_sigmas.tail(2)
        pick  = pd.concat([worst, best])
        for _, r in pick.iterrows():
            key = (r["gnss"], int(r["sv"]))
            arc_df = sat_data[sname][key]
            label = (f"{r['gnss'][:3].upper()}{int(r['sv']):02d}  "
                     f"σ={r['sigma_cmc']:.2f} m")
            color = CONST_COLORS.get(r["gnss"], "grey")
            # one line per arc
            for arc, g in arc_df.groupby("arc"):
                ax.plot(g["t_s"], g["cmc_resid"], lw=0.7, color=color, alpha=0.7,
                        label=label if arc == arc_df["arc"].iloc[0] else None)
        ax.axhline(0, lw=0.4, color="grey")
        ax.set_xlabel("time [s]")
        ax.set_ylabel("CMC residual [m]")
        ax.set_title(f"{sname} — Code-Minus-Carrier residual per sat (top 8 worst + 2 best)\n"
                     f"σ value  ≈  RMS code-multipath in metres")
        ax.legend(fontsize=8, ncol=2, loc="upper right")
        ax.grid(alpha=0.3)
        # symmetric ylim, capped
        ymax = min(np.nanpercentile(np.abs(arc_df["cmc_resid"]), 99) * 2, 30)
        ax.set_ylim(-ymax, ymax) if ymax > 1 else None
    fig.suptitle("Code-Minus-Carrier — direct measurement of code-multipath", fontsize=13)
    fig.tight_layout()
    out = PLOTS / "05_cmc_per_sat.png"
    fig.savefig(out, dpi=130); plt.close(fig)
    print(f"wrote {out.relative_to(ROOT)}")

    # --- Plot 2: σ(CMC) distribution comparison
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    # left: box plot per session
    ax = axes[0]
    data = [summary[summary["session"] == s]["sigma_cmc"].values
            for s in sessions]
    bp = ax.boxplot(data, labels=list(sessions.keys()),
                    showmeans=True, meanline=True)
    ax.set_ylabel("σ(CMC residual) per sat [m]")
    ax.set_title("σ(CMC) distribution per session\n"
                 "= per-sat code-multipath magnitude")
    ax.grid(axis="y", alpha=0.3)
    # annotate medians
    for i, vals in enumerate(data, start=1):
        med = np.median(vals)
        ax.text(i, med, f"med={med:.1f} m", ha="center", va="bottom", fontsize=9,
                bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.7))

    # right: σ(CMC) vs C/N0
    ax = axes[1]
    for sname, marker in zip(sessions.keys(), ["o", "s"]):
        sub = summary[summary["session"] == sname]
        for c in sub["gnss"].unique():
            ss = sub[sub["gnss"] == c]
            ax.scatter(ss["cn0_mean"], ss["sigma_cmc"], marker=marker, s=40,
                       color=CONST_COLORS.get(c, "grey"), alpha=0.7,
                       label=f"{sname[:5]}/{c[:3]}")
    ax.set_xlabel("mean C/N₀ per sat [dB-Hz]")
    ax.set_ylabel("σ(CMC) per sat [m]")
    ax.set_title("multipath magnitude vs signal strength\n"
                 "(low C/N₀ → tracker noisier and more multipath-susceptible)")
    ax.set_yscale("log")
    ax.legend(fontsize=7, ncol=3, loc="upper right")
    ax.grid(alpha=0.3, which="both")
    fig.suptitle("Multipath magnitude — hilltop vs urban canyon", fontsize=13)
    fig.tight_layout()
    out = PLOTS / "05_cmc_summary.png"
    fig.savefig(out, dpi=130); plt.close(fig)
    print(f"wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

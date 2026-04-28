"""
Pass 3 — raw-measurement overview for Hilltop and Urban-Canyon (Raw ON).

The Realme RMX3393 (MTK) does NOT populate SvPositionEcef in Raw rows
(all NaN), but it DOES populate AzimuthDegrees/ElevationDegrees in
Status rows. So this script:

- parses Status,... lines manually for sky-plot, C/N0, sat count
- parses Raw,... lines via gnss_lib_py.AndroidRawGnss for pseudoranges
  and chipset-clock metrics

Outputs:
- 03_raw_overview_<session>.png — 6-panel summary (sat count, C/N0 vs time,
  C/N0 vs elevation, sky plot, raw pseudorange, C/N0 histogram)
- 03_per_sat_cn0_<session>.png — per-satellite C/N0 traces (multipath search)
- 03_clock_drift_<session>.png — phone-clock drift + hardware-clock jumps
- raw_summary.csv — per-constellation statistics
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
PLOTS.mkdir(parents=True, exist_ok=True)

DATASETS = {
    "hilltop":      ROOT / "GNSSLogger Messurments ON (No RINIX, only NMEA), Outdoor Hilltop, ~180 Degree open sky" / "gnss_log_2026_04_26_16_34_46.txt",
    "urban_raw_on": ROOT / "GNSSLogger Messurments ON Urban Canyon" / "gnss_log_2026_04_27_18_19_26.txt",
}

# ConstellationType encoding (Android):
# 0=UNKNOWN 1=GPS 2=SBAS 3=GLONASS 4=QZSS 5=BEIDOU 6=GALILEO 7=IRNSS
CONST_LOOKUP = {0:"unknown", 1:"gps", 2:"sbas", 3:"glonass",
                4:"qzss", 5:"beidou", 6:"galileo", 7:"irnss"}

CONST_COLORS = {
    "gps":      "#1f77b4",
    "galileo":  "#2ca02c",
    "glonass":  "#d62728",
    "beidou":   "#ff7f0e",
    "qzss":     "#9467bd",
    "sbas":     "#8c564b",
    "irnss":    "#e377c2",
    "unknown":  "#7f7f7f",
}

STATUS_COLS = ["UnixTimeMillis","SignalCount","SignalIndex","ConstellationType",
               "Svid","CarrierFrequencyHz","Cn0DbHz","AzimuthDegrees",
               "ElevationDegrees","UsedInFix","HasAlmanacData",
               "HasEphemerisData","BasebandCn0DbHz"]


def parse_status_records(path: Path) -> pd.DataFrame:
    rows = []
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            if not line.startswith("Status,"):
                continue
            parts = line.rstrip("\n").split(",")
            # Status,<UnixTimeMillis or empty>,<SignalCount>,...
            # Skip blank fields
            try:
                rec = parts[1:1+len(STATUS_COLS)]
                if len(rec) < len(STATUS_COLS):
                    continue
                rows.append(rec)
            except Exception:
                continue
    df = pd.DataFrame(rows, columns=STATUS_COLS)
    # cast numerics
    for c in ["SignalCount","SignalIndex","ConstellationType","Svid",
              "CarrierFrequencyHz","Cn0DbHz","AzimuthDegrees",
              "ElevationDegrees","UsedInFix","HasAlmanacData",
              "HasEphemerisData","BasebandCn0DbHz"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["UnixTimeMillis"] = pd.to_numeric(df["UnixTimeMillis"], errors="coerce")
    df["constellation"] = df["ConstellationType"].map(CONST_LOOKUP).fillna("unknown")
    # When UnixTimeMillis blank, fill with the most recent valid time
    df["UnixTimeMillis"] = df["UnixTimeMillis"].ffill()
    df = df.dropna(subset=["ElevationDegrees", "AzimuthDegrees", "Cn0DbHz"])
    df["t_s"] = (df["UnixTimeMillis"] - df["UnixTimeMillis"].min()) / 1000.0
    return df


def load_raw(path: Path):
    return glp.AndroidRawGnss(input_path=str(path),
                              filter_measurements=True,
                              measurement_filters={"sv_time_uncertainty": 500.},
                              verbose=False)


def plot_session(name: str, status: pd.DataFrame, raw_df: pd.DataFrame):
    fig = plt.figure(figsize=(17, 11))
    gs = fig.add_gridspec(3, 3, height_ratios=[1, 1, 1.1])

    constellations = sorted(status["constellation"].unique())

    # --- (1) sat count over time
    ax = fig.add_subplot(gs[0, 0])
    sat_count = (status.groupby([pd.cut(status["t_s"], np.arange(0, status["t_s"].max()+10, 5)),
                                 "constellation"])["Svid"].nunique().unstack(fill_value=0))
    sat_count.index = [iv.left for iv in sat_count.index]
    bottom = np.zeros(len(sat_count))
    for c in sorted(sat_count.columns):
        ax.fill_between(sat_count.index.values, bottom, bottom + sat_count[c].values,
                        color=CONST_COLORS.get(c, "grey"), label=c, alpha=0.7,
                        step="pre")
        bottom += sat_count[c].values
    ax.set_xlabel("time [s]"); ax.set_ylabel("# tracked sats (5-s bins)")
    ax.set_title("tracked satellites over time"); ax.legend(fontsize=8); ax.grid(alpha=0.3)

    # --- (2) C/N0 vs time
    ax = fig.add_subplot(gs[0, 1])
    for c in constellations:
        sub = status[status["constellation"] == c]
        ax.scatter(sub["t_s"], sub["Cn0DbHz"], s=2, alpha=0.4,
                   color=CONST_COLORS.get(c, "grey"), label=c)
    ax.set_xlabel("time [s]"); ax.set_ylabel("C/N₀ [dB-Hz]")
    ax.set_title("C/N₀ vs time, all sats"); ax.legend(fontsize=8, markerscale=3); ax.grid(alpha=0.3)

    # --- (3) C/N0 vs elevation
    ax = fig.add_subplot(gs[0, 2])
    for c in constellations:
        sub = status[status["constellation"] == c]
        ax.scatter(sub["ElevationDegrees"], sub["Cn0DbHz"], s=3, alpha=0.4,
                   color=CONST_COLORS.get(c, "grey"), label=c)
    # Add reference curve: ideal C/N0 ~ const + log term in elevation
    xs = np.linspace(5, 90, 50)
    ax.plot(xs, 25 + 12*np.log10(np.sin(np.deg2rad(xs))) + 12, "--",
            color="black", alpha=0.5, label="open-sky envelope")
    ax.set_xlabel("elevation [°]"); ax.set_ylabel("C/N₀ [dB-Hz]")
    ax.set_title("C/N₀ vs elevation"); ax.set_xlim(0, 90)
    ax.legend(fontsize=8, markerscale=3); ax.grid(alpha=0.3)

    # --- (4) Skyplot
    ax = fig.add_subplot(gs[1, 0], projection="polar")
    ax.set_theta_zero_location("N"); ax.set_theta_direction(-1)
    az_rad = np.deg2rad(status["AzimuthDegrees"].to_numpy())
    r = 90.0 - status["ElevationDegrees"].to_numpy()
    sc = ax.scatter(az_rad, r, c=status["Cn0DbHz"].to_numpy(), s=4,
                    cmap="viridis", vmin=15, vmax=45, alpha=0.5)
    ax.set_rlim(0, 90); ax.set_rticks([15, 30, 45, 60, 75])
    ax.set_yticklabels(["75°", "60°", "45°", "30°", "15°"])
    ax.set_title("sky plot — colour = C/N₀")
    plt.colorbar(sc, ax=ax, fraction=0.046, label="C/N₀ [dB-Hz]")

    # --- (5) raw pseudorange / 1e6 over time, per sat (from raw_df)
    ax = fig.add_subplot(gs[1, 1])
    if raw_df is not None and not raw_df.empty:
        for c in raw_df["gnss_id"].unique():
            sub = raw_df[raw_df["gnss_id"] == c]
            ax.scatter(sub["t_s"], sub["raw_pr_m"]/1e6, s=2, alpha=0.5,
                       color=CONST_COLORS.get(c, "grey"), label=c)
        ax.legend(fontsize=8, markerscale=3)
    ax.set_xlabel("time [s]"); ax.set_ylabel("raw pseudorange [×10⁶ m]")
    ax.set_title("raw pseudorange (each line = one sat)")
    ax.grid(alpha=0.3)

    # --- (6) C/N0 histogram per constellation
    ax = fig.add_subplot(gs[1, 2])
    for c in constellations:
        sub = status[status["constellation"] == c]
        ax.hist(sub["Cn0DbHz"], bins=np.arange(10, 50, 1), alpha=0.5,
                color=CONST_COLORS.get(c, "grey"),
                label=f"{c} (n={len(sub)}, μ={sub['Cn0DbHz'].mean():.1f})")
    ax.set_xlabel("C/N₀ [dB-Hz]"); ax.set_ylabel("# measurements")
    ax.set_title("C/N₀ distribution"); ax.legend(fontsize=8); ax.grid(alpha=0.3)

    # --- (7,8,9) per-satellite C/N0 traces of the brightest 16 sats
    ax_traces = fig.add_subplot(gs[2, :])
    sat_mean = (status.groupby(["constellation", "Svid"])["Cn0DbHz"]
                  .mean().sort_values(ascending=False))
    pick = sat_mean.head(16).index.tolist()
    for (c, s) in pick:
        sub = status[(status["constellation"] == c) & (status["Svid"] == s)].sort_values("t_s")
        if len(sub) < 5: continue
        ax_traces.plot(sub["t_s"], sub["Cn0DbHz"], lw=0.8, alpha=0.75,
                       label=f"{c[:3].upper()}{int(s):02d}",
                       color=CONST_COLORS.get(c, "grey"))
    ax_traces.set_xlabel("time [s]"); ax_traces.set_ylabel("C/N₀ [dB-Hz]")
    ax_traces.set_title("per-satellite C/N₀ traces — top 16 by mean C/N₀")
    ax_traces.legend(fontsize=7, ncol=8, loc="lower center")
    ax_traces.grid(alpha=0.3)

    fig.suptitle(f"raw-measurement overview — {name}   "
                 f"(status_n={len(status)}, n_sats={status.groupby(['constellation','Svid']).ngroups}, "
                 f"duration={status['t_s'].max():.0f} s)", fontsize=13)
    fig.tight_layout()
    out = PLOTS / f"03_raw_overview_{name}.png"
    fig.savefig(out, dpi=130); plt.close(fig)
    print(f"  -> wrote {out.relative_to(ROOT)}")


def plot_per_sat_grid(name: str, status: pd.DataFrame):
    sats = (status.groupby(["constellation", "Svid"])
                  .agg(n=("Cn0DbHz", "size"),
                       cn0_mean=("Cn0DbHz", "mean"),
                       cn0_std=("Cn0DbHz", "std"),
                       el_mean=("ElevationDegrees", "mean"))
                  .sort_values("cn0_mean", ascending=False))
    sats = sats[(sats["n"] >= 30) & (sats["cn0_mean"] > 5)]
    n = len(sats)
    if n == 0: return
    cols = 5
    rows = int(np.ceil(n / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(18, 1.8*rows), sharex=True)
    axes = np.atleast_2d(axes).ravel()
    for i, ((c, s), row) in enumerate(sats.iterrows()):
        ax = axes[i]
        sub = status[(status["constellation"] == c) & (status["Svid"] == s)].sort_values("t_s")
        ax.plot(sub["t_s"], sub["Cn0DbHz"], lw=0.8,
                color=CONST_COLORS.get(c, "grey"))
        ax.axhline(row["cn0_mean"], lw=0.5, c="grey", linestyle=":")
        flag = " 🌊" if row["cn0_std"] > 4 else ""  # ad-hoc multipath suspect
        ax.set_title(f"{c[:3].upper()}{int(s):02d}  el={row['el_mean']:.0f}°  "
                     f"μ={row['cn0_mean']:.1f}  σ={row['cn0_std']:.1f}{flag}",
                     fontsize=9)
        ax.grid(alpha=0.3); ax.set_ylim(15, 50)
    for j in range(n, len(axes)):
        axes[j].axis("off")
    fig.suptitle(f"per-satellite C/N₀ — {name}  "
                 "(σ > 4 dB flagged as suspect for multipath/blockage)", fontsize=12)
    fig.tight_layout()
    out = PLOTS / f"03_per_sat_cn0_{name}.png"
    fig.savefig(out, dpi=130); plt.close(fig)
    print(f"  -> wrote {out.relative_to(ROOT)}")


def plot_clock_drift(name: str, raw):
    """Phone hardware-clock drift over time + hardware discontinuity count."""
    df = pd.DataFrame({
        "gps_millis": np.asarray(raw["gps_millis"]).ravel(),
        "drift_ns_s": np.asarray(raw["DriftNanosPerSecond"]).ravel(),
        "drift_unc": np.asarray(raw["DriftUncertaintyNanosPerSecond"]).ravel(),
        "hw_disc":   np.asarray(raw["HardwareClockDiscontinuityCount"]).ravel(),
        "full_bias": np.asarray(raw["FullBiasNanos"]).ravel(),
        "bias":      np.asarray(raw["BiasNanos"]).ravel(),
    })
    df["t_s"] = (df["gps_millis"] - df["gps_millis"].min())/1000.0
    df = df.drop_duplicates(subset="t_s")  # one row per epoch suffices
    fig, axes = plt.subplots(3, 1, figsize=(14, 9), sharex=True)
    axes[0].plot(df["t_s"], df["drift_ns_s"], lw=0.8)
    axes[0].fill_between(df["t_s"], df["drift_ns_s"]-df["drift_unc"],
                         df["drift_ns_s"]+df["drift_unc"], alpha=0.2)
    axes[0].set_ylabel("Phone-clock drift [ns/s]")
    axes[0].set_title(f"{name} — phone hardware clock\n"
                      f"σ(drift) over session = {df['drift_ns_s'].std():.1f} ns/s, "
                      f"|mean| = {df['drift_ns_s'].mean():.1f} ns/s")
    axes[0].grid(alpha=0.3)
    # FullBias evolution: should be ~roughly constant within a continuous segment
    axes[1].plot(df["t_s"], df["full_bias"]/1e9, lw=0.8, label="FullBiasNanos / 1e9 [s]")
    axes[1].plot(df["t_s"], df["bias"]/1e9, lw=0.6, label="BiasNanos / 1e9 [s]", alpha=0.7)
    axes[1].set_ylabel("phone GNSS time bias [s]")
    axes[1].set_title("phone-vs-GNSS-time bias (FullBiasNanos = full integer offset; BiasNanos = sub-ns residual)")
    axes[1].grid(alpha=0.3); axes[1].legend(fontsize=9)
    axes[2].plot(df["t_s"], df["hw_disc"], lw=0.8, drawstyle="steps-post")
    axes[2].set_xlabel("time [s]"); axes[2].set_ylabel("HardwareClockDiscontinuityCount")
    n_jumps = df["hw_disc"].nunique() - 1
    axes[2].set_title(f"hardware-clock discontinuities (every step ≈ ~256 ns / 3 s phone-clock jump) — {n_jumps} jumps")
    axes[2].grid(alpha=0.3)
    fig.tight_layout()
    out = PLOTS / f"03_clock_drift_{name}.png"
    fig.savefig(out, dpi=130); plt.close(fig)
    print(f"  -> wrote {out.relative_to(ROOT)}")


def main():
    summary = []
    for name, path in DATASETS.items():
        print(f"\n=== {name} ===")
        if not path.exists():
            print("  MISSING"); continue

        # parse Status records (manual)
        status = parse_status_records(path)
        print(f"  Status records: {len(status)} valid, "
              f"constellations = {sorted(status['constellation'].unique())}")

        # parse Raw via gnss_lib_py (for pseudorange + clock)
        raw = load_raw(path)
        raw_df = pd.DataFrame({
            "gps_millis": np.asarray(raw["gps_millis"]).ravel(),
            "gnss_id":    np.asarray(raw["gnss_id"]).ravel(),
            "sv_id":      np.asarray(raw["sv_id"]).ravel(),
            "raw_pr_m":   np.asarray(raw["raw_pr_m"]).ravel(),
            "cn0_dbhz":   np.asarray(raw["cn0_dbhz"]).ravel(),
        })
        raw_df["t_s"] = (raw_df["gps_millis"] - raw_df["gps_millis"].min())/1000.0
        # drop rows with absurd pseudoranges (Galileo SVs with bad time-of-week wrap)
        raw_df = raw_df[(raw_df["raw_pr_m"] > 1.5e7) & (raw_df["raw_pr_m"] < 5e7)]

        plot_session(name, status, raw_df)
        plot_per_sat_grid(name, status)
        plot_clock_drift(name, raw)

        for c in sorted(status["constellation"].unique()):
            sub = status[status["constellation"] == c]
            summary.append(dict(
                session=name, constellation=c,
                n_sats=int(sub["Svid"].nunique()),
                n_meas=int(len(sub)),
                cn0_median=float(sub["Cn0DbHz"].median()),
                cn0_p10=float(sub["Cn0DbHz"].quantile(0.10)),
                cn0_p90=float(sub["Cn0DbHz"].quantile(0.90)),
                el_median=float(sub["ElevationDegrees"].median()),
                used_in_fix_pct=float(sub["UsedInFix"].mean()*100),
                has_eph_pct=float(sub["HasEphemerisData"].mean()*100),
            ))

    out_csv = PLOTS / "raw_summary.csv"
    pd.DataFrame(summary).to_csv(out_csv, index=False)
    print(f"\nsummary -> {out_csv.relative_to(ROOT)}")
    print(pd.DataFrame(summary).to_string(index=False))


if __name__ == "__main__":
    main()

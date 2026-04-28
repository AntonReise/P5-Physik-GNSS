"""
Pass 1 — overview of every dataset at the position-fix level.

For each of the four sessions:
- parse Fix records via gnss_lib_py.AndroidRawFixes
- compute ENU scatter relative to session-mean
- compute sigma per axis, DRMS, CEP50, R95
- compare phone-reported accuracy vs measured RMS
- save: map (lat/lon), ENU scatter, reported-vs-measured accuracy timeseries

All plots written to analysis/plots/. A summary CSV is written to
analysis/plots/fix_summary.csv.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

_CACHE = Path(__file__).resolve().parents[1] / "cache"
os.environ.setdefault("MPLCONFIGDIR", str(_CACHE / "mpl"))
os.environ.setdefault("XDG_CACHE_HOME", str(_CACHE / "xdg"))
os.environ.setdefault("FONTCONFIG_PATH", "/opt/homebrew/etc/fonts")
for sub in ("mpl", "xdg", "xdg/fontconfig"):
    (_CACHE / sub).mkdir(parents=True, exist_ok=True)

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import gnss_lib_py as glp
import pymap3d as pm

ROOT = Path("/Users/anton/Projects/P5 Physik")
PLOTS = ROOT / "analysis" / "plots"
PLOTS.mkdir(parents=True, exist_ok=True)

DATASETS = {
    "hilltop":        ROOT / "GNSSLogger Messurments ON (No RINIX, only NMEA), Outdoor Hilltop, ~180 Degree open sky" / "gnss_log_2026_04_26_16_34_46.txt",
    "urban_raw_on":   ROOT / "GNSSLogger Messurments ON Urban Canyon" / "gnss_log_2026_04_27_18_19_26.txt",
    "urban_force_on": ROOT / "GNSSLogger Messurments Off, Force messurments On Urban Canyon" / "gnss_log_2026_04_27_18_32_22.txt",
    "indoor":         ROOT / "GNSSLogger Messurments ON Indoor" / "gnss_log_2026_04_27_18_43_35.txt",
}


def load_fixes(path: Path):
    """Return a NavData of GNSS-provider fixes only, or None if no fixes."""
    nav = glp.AndroidRawFixes(str(path))
    if "fix_provider" not in nav.rows:
        print("  WARN: no Fix records in this log")
        return None
    providers = np.unique(nav["fix_provider"]).tolist()
    target = None
    for p in providers:
        if str(p).lower() in ("gps", "gnss"):
            target = p
            break
    if target is None:
        print(f"  WARN: no GNSS-provider fixes; providers seen = {providers}")
        return None
    print(f"  providers = {providers}, using '{target}'")
    return nav.where("fix_provider", target)


def fixes_to_df(nav) -> pd.DataFrame:
    """Best-effort dump of a NavData to pandas DataFrame."""
    rows = nav.rows
    data = {r: np.asarray(nav[r]).ravel() for r in rows}
    return pd.DataFrame(data)


def enu_from_lla(lat, lon, alt, lat0, lon0, alt0):
    e, n, u = pm.geodetic2enu(lat, lon, alt, lat0, lon0, alt0)
    return np.asarray(e), np.asarray(n), np.asarray(u)


def session_stats(df: pd.DataFrame) -> dict:
    lat = df["lat_rx_deg"].to_numpy()
    lon = df["lon_rx_deg"].to_numpy()
    alt = df["alt_rx_m"].to_numpy()
    lat0, lon0, alt0 = lat.mean(), lon.mean(), alt.mean()
    e, n, u = enu_from_lla(lat, lon, alt, lat0, lon0, alt0)
    horiz = np.hypot(e, n)

    sig_e = e.std(ddof=1)
    sig_n = n.std(ddof=1)
    sig_u = u.std(ddof=1)
    drms = np.sqrt(sig_e**2 + sig_n**2)
    drms2 = 2 * drms
    cep50 = np.median(horiz)        # 50% radius (median horizontal error vs mean)
    r95 = np.quantile(horiz, 0.95)
    rms_h = np.sqrt(np.mean(horiz**2))

    # Phone-reported accuracy (1-sigma horizontal in metres). May be in
    # column "?accuracy_m" or similar — search.
    rep_col = None
    for cand in ("accuracy_m", "horiz_acc_m", "h_acc_m", "AccuracyMeters"):
        if cand in df.columns:
            rep_col = cand
            break
    rep_mean = float(df[rep_col].mean()) if rep_col else float("nan")
    vacc_col = "VerticalAccuracyMeters" if "VerticalAccuracyMeters" in df.columns else None
    vacc_mean = float(df[vacc_col].mean()) if vacc_col else float("nan")

    return dict(
        n_fix=len(df),
        lat0=lat0, lon0=lon0, alt0=alt0,
        sig_e=sig_e, sig_n=sig_n, sig_u=sig_u,
        sig_e_over_n=sig_e / sig_n if sig_n > 0 else float("nan"),
        drms=drms, drms2=drms2, cep50=cep50, r95=r95, rms_h=rms_h,
        rep_mean=rep_mean, rep_col=rep_col or "<missing>",
        vacc_mean=vacc_mean,
        e=e, n_arr=n, u=u, horiz=horiz, df=df,
    )


def plot_session(name: str, st: dict):
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    # --- ENU scatter (E vs N) ---
    ax = axes[0]
    ax.scatter(st["e"], st["n_arr"], s=4, alpha=0.4, c=np.arange(len(st["e"])), cmap="viridis")
    ax.set_aspect("equal", adjustable="datalim")
    lim = max(abs(st["e"]).max(), abs(st["n_arr"]).max(), 1.0) * 1.15
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim)
    ax.axhline(0, lw=0.5, c="grey"); ax.axvline(0, lw=0.5, c="grey")
    ax.set_xlabel("East [m] (rel. to mean)")
    ax.set_ylabel("North [m] (rel. to mean)")
    ax.set_title(f"{name}: ENU horizontal scatter\n"
                 f"σ_E = {st['sig_e']:.2f} m, σ_N = {st['sig_n']:.2f} m, "
                 f"σ_E/σ_N = {st['sig_e_over_n']:.2f}\n"
                 f"DRMS = {st['drms']:.2f} m, CEP50 = {st['cep50']:.2f} m, R95 = {st['r95']:.2f} m")
    ax.grid(True, alpha=0.3)

    # --- Up vs time ---
    ax = axes[1]
    t = np.arange(len(st["u"]))
    ax.plot(t, st["u"], lw=0.8)
    ax.axhline(0, lw=0.5, c="grey")
    ax.set_xlabel("Sample # (1 Hz)")
    ax.set_ylabel("Up [m] (rel. to mean)")
    ax.set_title(f"Vertical drift\nσ_U = {st['sig_u']:.2f} m  ({st['sig_u']/st['drms']:.1f}× DRMS)")
    ax.grid(True, alpha=0.3)

    # --- Horizontal error timeseries vs reported accuracy ---
    ax = axes[2]
    ax.plot(t, st["horiz"], lw=0.8, label="measured |horiz| vs mean")
    df = st["df"]
    if st["rep_col"] in df.columns:
        ax.plot(t, df[st["rep_col"]].to_numpy(), lw=0.8, c="orange",
                label=f"phone-reported {st['rep_col']}")
    ax.set_xlabel("Sample # (1 Hz)")
    ax.set_ylabel("metres")
    ax.set_title(f"Reported vs measured horizontal error\n"
                 f"reported mean = {st['rep_mean']:.2f} m, measured RMS = {st['rms_h']:.2f} m")
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(True, alpha=0.3)

    fig.suptitle(f"Session: {name}  (n = {st['n_fix']} fixes)", fontsize=13)
    fig.tight_layout()
    out = PLOTS / f"01_fix_overview_{name}.png"
    fig.savefig(out, dpi=130)
    plt.close(fig)
    print(f"  -> wrote {out.relative_to(ROOT)}")


def main():
    summary_rows = []
    for name, path in DATASETS.items():
        print(f"\n=== {name} ===  ({path.name})")
        if not path.exists():
            print("  MISSING")
            continue
        nav = load_fixes(path)
        if nav is None:
            summary_rows.append(dict(session=name, n_fix=0, note="no GNSS fixes"))
            continue
        df = fixes_to_df(nav)
        # Dump available columns once for inspection
        print("  columns:", list(df.columns))
        st = session_stats(df)
        print(f"  n={st['n_fix']}  σE={st['sig_e']:.2f}  σN={st['sig_n']:.2f}  "
              f"σU={st['sig_u']:.2f}  σE/σN={st['sig_e_over_n']:.2f}  "
              f"DRMS={st['drms']:.2f}  reported~{st['rep_mean']:.2f}")
        plot_session(name, st)
        summary_rows.append(dict(
            session=name, n=st["n_fix"],
            sig_e=st["sig_e"], sig_n=st["sig_n"], sig_u=st["sig_u"],
            sig_e_over_n=st["sig_e_over_n"],
            drms=st["drms"], cep50=st["cep50"], r95=st["r95"], rms_h=st["rms_h"],
            reported_mean=st["rep_mean"], reported_col=st["rep_col"],
        ))

    summary = pd.DataFrame(summary_rows)
    out_csv = PLOTS / "fix_summary.csv"
    summary.to_csv(out_csv, index=False)
    print(f"\nsummary -> {out_csv.relative_to(ROOT)}")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()

"""
Pass 6 — multipath evidence summary, hilltop vs urban canyon.

The cleanest multipath story has three layers, in order of directness:

  (a) ADR_VALID rate — fraction of measurements where the phone's
      carrier-phase tracking loop could maintain lock.  Multipath /
      reflection / blockage are what make the loop lose lock.
      Drop = direct multipath / NLOS evidence.

  (b) Code-Minus-Carrier residual σ — for the surviving sats, this
      is the per-sat code-multipath in metres (after detrending
      out the integer ambiguity and slow ionospheric drift).

  (c) Per-sat C/N0 trace shape — slow oscillations on top of the
      mean show interference between direct and reflected ray.

This script renders (a) + (b) in a single dashboard panel and writes
out 06_multipath_evidence.png.
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

import sys
sys.path.insert(0, str(Path(__file__).parent))
from importlib import import_module
mp = import_module("05_multipath_cmc")

ROOT = Path("/Users/anton/Projects/P5 Physik")
PLOTS = ROOT / "analysis" / "plots"

DATASETS = {
    "hilltop":      ROOT / "GNSSLogger Messurments ON (No RINIX, only NMEA), Outdoor Hilltop, ~180 Degree open sky" / "gnss_log_2026_04_26_16_34_46.txt",
    "urban_raw_on": ROOT / "GNSSLogger Messurments ON Urban Canyon" / "gnss_log_2026_04_27_18_19_26.txt",
}

CONST_COLORS = mp.CONST_COLORS


def adr_rates(path: Path):
    raw = glp.AndroidRawGnss(input_path=str(path),
                             filter_measurements=True,
                             measurement_filters={"sv_time_uncertainty": 500.},
                             verbose=False)
    s = np.asarray(raw["AccumulatedDeltaRangeState"]).ravel()
    cn = np.asarray(raw["cn0_dbhz"]).ravel()
    gid = np.asarray(raw["gnss_id"]).ravel()
    n = len(s)
    rates = {}
    for c in np.unique(gid):
        mask = gid == c
        valid = ((s[mask] & 1) != 0).sum()
        rates[c] = dict(n=int(mask.sum()), n_valid=int(valid),
                        rate=100.0 * valid / max(int(mask.sum()), 1),
                        cn0_p90=float(np.nanpercentile(cn[mask], 90)) if mask.sum() else np.nan)
    rates["__all__"] = dict(n=n, n_valid=int(((s & 1) != 0).sum()),
                            rate=100.0 * int(((s & 1) != 0).sum()) / max(n, 1),
                            cn0_p90=float(np.nanpercentile(cn, 90)))
    return rates


def main():
    # --- gather ADR rates per session per constellation
    rates = {n: adr_rates(p) for n, p in DATASETS.items()}

    # --- gather per-sat CMC σ via the same routine as pass 5
    cmc_rows = []
    cmc_traces = {}
    for sname, path in DATASETS.items():
        df = mp.load_cmc_table(path)
        cmc_traces[sname] = {}
        for (gid, sid), arc_df in mp.cmc_per_sat(df):
            sigma = float(arc_df["cmc_resid"].std(ddof=1))
            cmc_rows.append(dict(session=sname, gnss=gid, sv=int(sid),
                                 cn0_mean=float(arc_df["cn0"].mean()),
                                 sigma_cmc=sigma, n=len(arc_df)))
            cmc_traces[sname][(gid, int(sid))] = arc_df
    cmc = pd.DataFrame(cmc_rows)

    # =================================================================
    fig = plt.figure(figsize=(17, 11))
    gs = fig.add_gridspec(3, 3, height_ratios=[1.1, 1, 1.2],
                          hspace=0.45, wspace=0.30)

    # --- (top left) ADR_VALID rate per session per constellation
    ax = fig.add_subplot(gs[0, 0])
    constellations = ["gps", "galileo", "glonass", "beidou"]
    x = np.arange(len(constellations))
    w = 0.35
    for i, sname in enumerate(rates):
        rs = rates[sname]
        vals = [rs.get(c, {}).get("rate", 0) for c in constellations]
        bars = ax.bar(x + (i - 0.5)*w, vals, w,
                      label=sname,
                      color=("#1b9e77" if "hill" in sname else "#d95f02"))
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    f"{v:.0f}%", ha="center", fontsize=9)
    ax.set_xticks(x); ax.set_xticklabels(constellations, fontsize=9)
    ax.set_ylabel("% ADR_VALID")
    ax.set_title("(a) carrier-phase tracking survival rate\n"
                 "fraction of measurements where the phone could keep carrier lock\n"
                 "loss-of-lock = direct multipath / NLOS evidence")
    ax.legend(fontsize=9); ax.grid(alpha=0.3, axis="y")
    ax.set_ylim(0, 100)

    # --- (top middle) overall ADR_VALID rate
    ax = fig.add_subplot(gs[0, 1])
    overall = [(s, rates[s]["__all__"]["rate"],
                rates[s]["__all__"]["n_valid"], rates[s]["__all__"]["n"])
               for s in rates]
    sx = np.arange(len(overall))
    bars = ax.bar(sx, [o[1] for o in overall], 0.5,
                  color=["#1b9e77", "#d95f02"])
    for bar, (s, r, v, n) in zip(bars, overall):
        ax.text(bar.get_x() + bar.get_width()/2, r + 1,
                f"{r:.1f}%\n({v}/{n})", ha="center", fontsize=10)
    ax.set_xticks(sx); ax.set_xticklabels([o[0] for o in overall])
    ax.set_ylabel("% ADR_VALID, all constellations")
    ax.set_title("overall carrier-tracking survival\n"
                 "headline number for the talk")
    ax.set_ylim(0, max(o[1] for o in overall) * 1.4)
    ax.grid(alpha=0.3, axis="y")

    # --- (top right) C/N0 p90 per constellation
    ax = fig.add_subplot(gs[0, 2])
    for i, sname in enumerate(rates):
        vals = [rates[sname].get(c, {}).get("cn0_p90", np.nan) for c in constellations]
        bars = ax.bar(x + (i - 0.5)*w, vals, w,
                      color=("#1b9e77" if "hill" in sname else "#d95f02"))
        for bar, v in zip(bars, vals):
            if np.isfinite(v):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                        f"{v:.1f}", ha="center", fontsize=9)
    ax.set_xticks(x); ax.set_xticklabels(constellations, fontsize=9)
    ax.set_ylabel("C/N₀ p90 [dB-Hz]")
    ax.set_title("(b) signal strength p90\n"
                 "high p90 = some clean signal exists; low = even best sats are weak")
    ax.grid(alpha=0.3, axis="y")

    # --- (middle row) σ(CMC) box plot + scatter
    ax = fig.add_subplot(gs[1, 0])
    sessions = list(DATASETS.keys())
    data = [cmc[cmc["session"] == s]["sigma_cmc"].values for s in sessions]
    bp = ax.boxplot(data, tick_labels=sessions, showmeans=True, meanline=True,
                    patch_artist=True)
    for patch, c in zip(bp["boxes"], ["#1b9e77", "#d95f02"]):
        patch.set_facecolor(c); patch.set_alpha(0.4)
    for i, vals in enumerate(data, start=1):
        if len(vals) == 0: continue
        med = np.median(vals)
        ax.text(i, med, f"med={med:.2f} m\nn={len(vals)}",
                ha="center", va="bottom", fontsize=9,
                bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8))
    ax.set_ylabel("σ(CMC residual) per sat [m]")
    ax.set_title("(c) σ(CMC) per surviving sat\n"
                 "≈ code-multipath magnitude in metres\n"
                 "⚠ urban sample biased: only sats that *kept* lock survive")
    ax.grid(alpha=0.3, axis="y")

    # --- (middle middle) σ(CMC) per constellation
    ax = fig.add_subplot(gs[1, 1])
    for i, sname in enumerate(sessions):
        sub = cmc[cmc["session"] == sname]
        for c in sub["gnss"].unique():
            ss = sub[sub["gnss"] == c]
            ax.scatter(np.full(len(ss), i + (0.15 if "hill" in sname else -0.15)),
                       ss["sigma_cmc"],
                       color=CONST_COLORS.get(c, "grey"),
                       s=80, alpha=0.7, label=f"{c}" if i == 0 else None)
    ax.set_xticks([0, 1]); ax.set_xticklabels(sessions)
    ax.set_ylabel("σ(CMC) per sat [m]")
    ax.set_title("σ(CMC) per sat coloured by constellation")
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels, fontsize=8, loc="upper right")
    ax.grid(alpha=0.3, axis="y")

    # --- (middle right) urban evidence summary table-as-text
    ax = fig.add_subplot(gs[1, 2]); ax.axis("off")
    h = rates["hilltop"]["__all__"]
    u = rates["urban_raw_on"]["__all__"]
    cmc_h = cmc[cmc["session"] == "hilltop"]["sigma_cmc"]
    cmc_u = cmc[cmc["session"] == "urban_raw_on"]["sigma_cmc"]
    txt = (
        "summary  hilltop  vs  urban canyon\n"
        "—————————————————————————\n"
        f"ADR_VALID rate     {h['rate']:5.1f} %    {u['rate']:5.1f} %"
        f"   ({h['rate']/u['rate']:.1f}× drop)\n"
        f"C/N₀ p90 (all)     {h['cn0_p90']:5.1f}      {u['cn0_p90']:5.1f}"
        f"   (−{h['cn0_p90']-u['cn0_p90']:.1f} dB-Hz)\n"
        f"σ(CMC) median      {np.median(cmc_h):5.2f} m   "
        f"{np.median(cmc_u):5.2f} m  ⚠ small n in urban\n"
        f"# sats survived    {len(cmc_h):3d}        {len(cmc_u):3d}\n\n"
        "interpretation\n"
        "—————————————————————————\n"
        "• In the urban canyon, the carrier-tracking\n"
        "  loop fails on 9/10 measurements — direct\n"
        "  evidence of multipath / NLOS disrupting\n"
        "  the phase-locked loop.\n"
        "• Of the few that survive, σ(CMC) is small\n"
        "  because they are by definition the cleanest\n"
        "  signals (selection bias).\n"
        "• In the open-sky hilltop, ~3/10 still fail —\n"
        "  the rest show ~1.5 m code-multipath, the\n"
        "  expected open-sky floor (ground reflection,\n"
        "  rocks, body of the phone)."
    )
    ax.text(0.0, 1.0, txt, ha="left", va="top", family="monospace", fontsize=10)

    # --- (bottom) one annotated CMC trace per session
    ax_h = fig.add_subplot(gs[2, 0:2])
    # pick worst-sigma sat in hilltop
    if len(cmc_h) > 0:
        worst = cmc[cmc["session"] == "hilltop"].sort_values("sigma_cmc", ascending=False).iloc[0]
        key = (worst["gnss"], int(worst["sv"]))
        arc_df = cmc_traces["hilltop"][key]
        for arc, g in arc_df.groupby("arc"):
            ax_h.plot(g["t_s"], g["cmc_resid"], lw=0.9,
                      color=CONST_COLORS.get(worst["gnss"], "grey"))
        ax_h.set_title(f"hilltop — worst-multipath sat: "
                       f"{worst['gnss'][:3].upper()}{int(worst['sv']):02d}  "
                       f"σ(CMC) = {worst['sigma_cmc']:.2f} m   "
                       f"(C/N₀ avg {worst['cn0_mean']:.1f} dB-Hz)")
        ax_h.axhline(0, lw=0.4, c="grey")
        ax_h.set_xlabel("time [s]"); ax_h.set_ylabel("CMC residual [m]")
        ax_h.grid(alpha=0.3)

    ax_u = fig.add_subplot(gs[2, 2])
    if len(cmc_u) > 0:
        worst = cmc[cmc["session"] == "urban_raw_on"].sort_values("sigma_cmc", ascending=False).iloc[0]
        key = (worst["gnss"], int(worst["sv"]))
        arc_df = cmc_traces["urban_raw_on"][key]
        for arc, g in arc_df.groupby("arc"):
            ax_u.plot(g["t_s"], g["cmc_resid"], lw=0.9,
                      color=CONST_COLORS.get(worst["gnss"], "grey"))
        ax_u.set_title(f"urban — worst-multipath surviving sat:\n"
                       f"{worst['gnss'][:3].upper()}{int(worst['sv']):02d}  "
                       f"σ(CMC) = {worst['sigma_cmc']:.2f} m")
        ax_u.axhline(0, lw=0.4, c="grey")
        ax_u.set_xlabel("time [s]"); ax_u.set_ylabel("CMC residual [m]")
        ax_u.grid(alpha=0.3)

    fig.suptitle("Multipath evidence dashboard — Code-Minus-Carrier + ADR-VALID rate", fontsize=13)
    out = PLOTS / "06_multipath_evidence.png"
    fig.savefig(out, dpi=130, bbox_inches="tight")
    print(f"wrote {out.relative_to(ROOT)}")
    cmc.to_csv(PLOTS / "06_multipath_evidence.csv", index=False)


if __name__ == "__main__":
    main()

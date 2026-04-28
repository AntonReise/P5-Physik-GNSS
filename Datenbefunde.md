# Datenbefunde — GNSS-Messreihen, Realme RMX3393

Working summary of everything the analysis pipeline (`analysis/scripts/01_…06_`) has produced so far. All plots live in `analysis/plots/`.

---

## 1. The four datasets at a glance

| Dataset (folder) | Date | Duration | Fix lines | Raw lines | Status lines | Verdict |
|---|---|---:|---:|---:|---:|---|
| Hilltop "open sky" | 2026-04-26 | ~11.6 min | 698 | 29 249 | 35 020 | **most important** — long, clean, all four constellations, full carrier-phase data |
| Urban Canyon "Raw ON" *(after rename)* | 2026-04-27 | ~10 min | 599 | 9 970 | 28 034 | **second most important** — direct hilltop counterpart, full Raw stream |
| Urban Canyon "Force ON" *(after rename)* | 2026-04-27 | ~5 min | 300 | 0 | 13 665 | **fix-level only** — no Raw measurements (Force-Measurements switch did not capture Raw on this MTK chipset). Useful for position-scatter comparison only. |
| Indoor | 2026-04-27 | ~10 min | **0** | 0 | 7 303 | **negative example** — phone never obtained a single GNSS fix indoors. One slide-worthy fact, then drop. |

> Note: the two urban folders had been mislabelled at recording time and were renamed in this round. The "Raw ON" folder now genuinely contains the Raw measurements.

> Note 2: `CLAUDE.md` originally claimed Hilltop measured RMS = 3.8 m vs reported 1.25 m. Real numbers are **1.51 m measured vs 1.25 m reported** — a 21 % under-estimate, not a factor of 3. The "factor 3" anecdote should not be used in the talk.

---

## 2. Plot inventory

| File | What it shows |
|---|---|
| `01_fix_overview_<session>.png` | Per-session ENU scatter, vertical drift, reported-vs-measured horizontal error |
| `02_session_comparison.png` | Three sessions side-by-side ENU scatter + bar chart of σ_E, σ_N, σ_U, DRMS, CEP50, R95, reported |
| `03_raw_overview_<session>.png` | Sat count over time, C/N₀ vs time, C/N₀ vs elevation, sky plot, raw pseudorange, C/N₀ histogram, top-16 per-sat traces |
| `03_per_sat_cn0_<session>.png` | Grid of per-satellite C/N₀ time series (multipath visual search) |
| `03_clock_drift_<session>.png` | Phone hardware-clock drift, FullBias evolution, hardware-clock discontinuity counter |
| `04_skyplot_compare.png` | 2×2 sky-plot grid: hilltop / urban × all-records / C/N₀≥25 dB-Hz only |
| `05_cmc_per_sat.png` | Code-Minus-Carrier residuals per sat, hilltop vs urban (8 worst + 2 best) |
| `05_cmc_summary.png` | σ(CMC) box plot + σ(CMC) vs mean C/N₀ |
| `06_multipath_evidence.png` | Multipath dashboard: ADR-VALID rate per constellation, σ(CMC), worst-multipath trace |
| `fix_summary.csv`, `raw_summary.csv`, `05_cmc_per_sat.csv`, `06_multipath_evidence.csv` | Tabular per-session / per-sat statistics |

---

## 3. Per-dataset findings

### 3.1 Hilltop (open sky) — primary

- 698 GNSS-provider fixes over 11.6 min.
- σ_E = 1.49 m, σ_N = 0.25 m, σ_U = 2.91 m → **σ_E/σ_N = 5.96** (massive horizontal anisotropy).
- DRMS = 1.51 m, CEP50 = 1.34 m, R95 = 2.59 m.
- Phone-reported `AccuracyMeters` mean = 1.25 m → 21 % under-estimate.
- Vertical drift shows a single large excursion around sample 350–400 s (≈ 30 m peak) — a loss-of-lock event followed by a step-shift in the mean horizontal position.
- Raw stream sees **5 constellations** (GPS, Galileo, GLONASS, BeiDou, SBAS), median C/N₀ best for GPS (33.2 dB-Hz).
- Filtered sky plot at C/N₀ ≥ 25 dB-Hz → 49 unique sats actually received (full-sky coverage).
- Carrier-phase tracking succeeds 40.2 % of the time (ADR_VALID).
- Code-multipath floor: σ(CMC) median ≈ 1.5 m. Worst sat: BEI 25 with σ = 3.07 m.

### 3.2 Urban Canyon "Raw ON" — primary

- 599 fixes over 10 min.
- σ_E = 1.21 m, σ_N = 2.15 m, σ_U = 0.14 m → **σ_E/σ_N = 0.57** (anisotropy axis *flipped* relative to hilltop).
- DRMS = 2.47 m, CEP50 = 2.48 m, R95 = 3.30 m.
- σ_U = 0.14 m is non-physical — phone is clamping altitude (Kalman lock or barometer fusion).
- Same 5 constellations visible, but C/N₀ p90 collapses: GPS 22.9 (−16 dB vs hilltop), Galileo 17.7 (−19 dB).
- Galileo "Used-in-Fix" rate drops from 74 % to 21 %.
- Filtered sky plot → only **10 unique sats** actually received, clustered in a narrow strip (the open-sky window of the street).
- Carrier-phase tracking succeeds only 10.3 % of the time — a 4× drop from hilltop.

### 3.3 Urban Canyon "Force ON" — secondary

- 599 fixes over ~10 min, no Raw measurements.
- DRMS = 3.48 m, CEP50 = 1.64 m, **R95 = 8.94 m** → R95/CEP50 = 5.4 (heavy-tailed, non-Gaussian).
- One single large excursion (~9 m) drives the R95 — classical NLOS spike signature.
- Useful exclusively as a third position-scatter point in `02_session_comparison.png`. Cannot be used for any raw-level analysis.

### 3.4 Indoor — negative example

- 0 GNSS fixes in 7 303 status records over ~10 min. Phone *was aware of* satellites (almanac data only) but never decoded a single signal hard enough to fix. Single slide-worthy fact.

---

## 4. Conclusions, easiest → hardest

### 4.1 (Easy) An open-sky hilltop yields a far better fix than an urban canyon

Side-by-side numbers in `02_session_comparison.png`:

| Metric | Hilltop | Urban (Force ON) | Ratio |
|---|---:|---:|---:|
| DRMS | 1.51 m | 3.48 m | 2.3× |
| R95 | 2.59 m | 8.94 m | 3.4× |

Stating "urban canyon is worse" is no longer a hand-wave — we have the numbers.

### 4.2 (Easy) Indoors, phone GNSS does not work at all

7 300 seconds of recording, zero fixes. Pure visual demonstration.

### 4.3 (Easy) The phone reports an over-confident accuracy

Hilltop: phone says ±1.25 m, real DRMS is 1.51 m — measured error is 21 % larger. Urban (Force ON): phone says ±2.35 m, real DRMS is 3.48 m — 48 % larger. The handset's `AccuracyMeters` field is systematically too optimistic, especially when the geometry degrades.

### 4.4 (Easy) The horizontal scatter is anisotropic, not symmetric

In the open-sky hilltop, σ_East = 1.49 m but σ_North = 0.25 m → 5.96× difference. In the urban canyon the ratio is **0.57** — the anisotropy direction *flips* relative to hilltop. This is pure DOP-geometry: which axis is bad depends on which strip of sky the satellites occupy. The "circle of error around your dot" mental model is wrong; real GNSS scatter is an ellipse whose orientation is set by the visible sky.

### 4.5 (Easy) Vertical accuracy is not what the phone claims

In two of the three outdoor sessions the phone clamps σ_U to 0.14 m and 0.91 m — physically impossible for L1 single-frequency GNSS, where σ_U should run 2–3× σ_horizontal. The MTK chipset is using barometer fusion or a Kalman altitude prior; the displayed "VerticalAccuracyMeters" is more about software policy than measurement.

### 4.6 (Medium) The urban distribution is heavy-tailed (NLOS spikes)

Urban Force-ON: CEP50 = 1.64 m (very good!) but R95 = 8.94 m. Ratio R95/CEP50 = **5.4**. A Gaussian distribution gives R95/CEP50 ≈ 2.1; we see 2.6× more tail. The "heavy tail" is exactly the signature of intermittent NLOS / multipath spikes pushing rare measurements far away while most stay close. The median user experience is fine; the worst-case user experience is ten metres off.

### 4.7 (Medium) Signal strength collapses in the urban canyon

Per-constellation C/N₀ p90 dropping from hilltop to urban:

| Constellation | Hilltop p90 | Urban p90 | Δ |
|---|---:|---:|---:|
| GPS | 38.8 dB-Hz | 22.9 | **−16 dB** |
| Galileo | 36.7 | 17.7 | **−19 dB** |
| GLONASS | 36.0 | 23.8 | −12 dB |
| BeiDou | 37.0 | 28.1 | −9 dB |

Galileo degrades hardest. Plausible cause: the E1 BOC modulation has narrower effective bandwidth than GPS L1 C/A, making it more rauschanfällig at low SNR. The "Used-in-Fix" rate for Galileo drops from 74 % to 21 % — three quarters of Galileo measurements stop contributing in the canyon.

### 4.8 (Medium) The number of satellites that *actually feed the fix* drops 5×

Sky plots in `04_skyplot_compare.png`, filtered to C/N₀ ≥ 25 dB-Hz:

- Hilltop: **49** unique sats received → full sky coverage.
- Urban canyon: **10** unique sats received → narrow strip aligned with the street.

The unfiltered sky plot looks similar between sessions because the phone *knows* about almanac sats it cannot decode. The filtered plot collapses to what is physically being received and visually reproduces the strip-of-sky the GnssLogger app shows live.

### 4.9 (Medium) The phone's quartz oscillator is ~10⁹× worse than a Galileo PHM

`03_clock_drift_<session>.png`:
- Phone-clock drift evolves from −2300 ns/s to −100 ns/s during the 11-minute hilltop session — a 2 200 ns/s sweep that looks like temperature equilibration of the oscillator.
- σ(drift) over the session ≈ 477 ns/s (hilltop), 211 ns/s (urban).

Galileo PHM stability: ~10⁻¹⁴ at 10⁴ s ≈ 1 ns over an entire day. The phone is 10⁸–10⁹× less stable. **This is exactly the reason a single phone needs four satellites to solve for $(x, y, z, c\,\delta t_R)$ — its own clock is nowhere near good enough to be assumed known.** A useful Block-1 contrast slide that was not in the original presentation plan.

### 4.10 (Medium-hard) The "BeiDou-12 50–100 s C/N₀ oscillation" claim from the project memory does not hold

`03_per_sat_cn0_hilltop.png`. BEI 12 has σ = 3.4 dB without a clear periodic structure. Other satellites with worse signatures exist — e.g. **BEI 25 with σ(CMC) = 3.07 m** is the actual worst-multipath sat in the hilltop dataset. The original anecdote should be either retired or replaced with the BEI-25 finding.

### 4.11 (Hard) The carrier-phase tracking-loop failure rate is itself the cleanest multipath measurement

`06_multipath_evidence.png`. The Android `AccumulatedDeltaRangeState` field carries an `ADR_VALID` bit that toggles on/off depending on whether the phase-locked loop is keeping integer-cycle alignment. Multipath is exactly the thing that breaks PLL lock (the reflected ray drags the tracking loop off the direct ray).

| Session | ADR_VALID rate | GLONASS specifically |
|---|---:|---:|
| Hilltop | 40.2 % | 22 % |
| Urban canyon | 10.3 % | **2 %** |

A 4× drop overall, an 11× drop for GLONASS. **In the urban canyon, 9 out of 10 carrier-phase measurements never reach a valid lock state** — that is the most direct quantitative multipath evidence in this dataset. It does not need a position-fix, an ephemeris download, or any external truth; it falls out of the receiver's own tracking-loop telemetry.

### 4.12 (Hard) Code-Minus-Carrier directly measures multipath in metres — and its open-sky floor is ~1.5 m

CMC = ρ_code − φ_carrier ≈ 2·I + (M_code − M_φ) − Nλ. Per-arc linear detrending removes the integer ambiguity and the slow ionospheric drift, leaving the residual ≈ pure code multipath. `05_cmc_per_sat.png` and `06_multipath_evidence.png`.

For the hilltop sats that survived the ADR_VALID + cycle-slip filter, σ(CMC) median = **1.5 m**, worst sat 3.07 m. This is the open-sky multipath floor of a smartphone — driven by ground reflections, the body of the phone (RHCP→LHCP leakage), and L1-bandwidth code-tracking noise. It is **not zero in open sky**, contrary to what a naive reading of the multipath chapter might suggest. Any further multipath improvement requires geodetic antennas (choke ring + RHCP filter) or wider-bandwidth signals (Galileo E5 AltBOC, 51 MHz vs L1's 2 MHz), neither of which a phone has.

### 4.13 (Hard) The urban σ(CMC) being smaller than hilltop's is a survivorship-bias artefact, not a contradiction

The naive read of `05_cmc_summary.png` says urban has *lower* code multipath than hilltop (median 0.5 m vs 1.5 m). This is wrong as a multipath statement. The urban CMC is computed only on the 10 % of measurements that survived the ADR_VALID filter — by construction these are the strongest, cleanest urban signals, the ones with low multipath. The 90 % we cannot measure are exactly the multipath-affected ones. The honest reading is: **urban gives us σ(CMC) = NaN for 90 % of samples, σ(CMC) ≈ 0.5 m for the surviving 10 %.** This is a transferable methodological point that an examiner may pull on (AFB-III).

### 4.14 (Hard) The Realme tracks 19 SBAS PRNs but decodes none of them

In every session, ≈ 19 SBAS satellites appear in the Status records with C/N₀ = 0. The phone has the SBAS satellites' positions from almanac but the MTK chipset never decodes their signals — SBAS augmentation is silently switched off in Realme's GNSS firmware. EGNOS over Europe could in principle have given metre-level corrections; the consumer-phone vendor has chosen not to. Useful one-liner for AFB-III: *"my phone could be 5× more accurate for free; it isn't because of a vendor decision."*

---

## 5. Open methodology questions before next pass

- **σ_U clamping** — confirm whether `Pressure,…` records (barometer) drive the altitude lock, by correlating their time series with σ_U over the session.
- **WLS position solve** with broadcast ephemeris — would let us compute pseudorange residuals (a fourth multipath probe) and an independent receiver position.
- **RTKLIB 4× corrections matrix** (no-iono / Klobuchar / Saastamoinen / both) — turns the atmospheric block into hard numbers from our own pseudoranges.
- **Cycle-slip detection** in CMC — current arc-break heuristic catches 5 m jumps; a finer detector might recover more arcs and tighten the σ(CMC) statistics.
- Verify whether the BEI 25 σ = 3.07 m signature contains a coherent oscillation (FFT) — if yes, λ/4 → reflector geometry can be derived directly from data (AFB-II candidate).

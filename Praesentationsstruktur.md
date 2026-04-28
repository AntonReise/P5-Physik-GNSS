# P5 Präsentationsstruktur — Working Document

**Leitfrage:** *Welche physikalischen Limitierungen bestimmen derzeit die Genauigkeit von GNSS, und durch welche Maßnahmen könnten diese verbessert werden?*

**Format:** 10 min Vortrag, 10 min Kolloquium.

---

## Roter Faden: die Pseudoentfernungs-Gleichung

The whole talk hangs off this single equation, written once and revisited at the end:

$$\rho_{\text{obs}} = \rho_{\text{geom}} + c\,\delta t_R - c\,\delta t_S + I + T + M + \varepsilon$$

| Symbol | Was es ist | In welchem Block behandelt |
|---|---|---|
| $\rho_{\text{geom}}$ | wahre Entfernung Satellit–Empfänger | Intro (Trilateration, 4 Unbekannte) |
| $c\,\delta t_R$ | Empfängeruhrfehler | Intro (warum 4 Satelliten nötig sind) |
| $c\,\delta t_S$ | Satellitenuhrfehler (intrinsisch + relativistisch) | **Block 1: Satellitenuhren** |
| $I$ | Ionosphärische Verzögerung | **Block 2: Atmosphäre** |
| $T$ | Troposphärische Verzögerung | **Block 2: Atmosphäre** |
| $M$ | Mehrwege-Effekte (Multipath) | **Block 3: Multipath** |
| $\varepsilon$ | Empfängerrauschen, etc. | nur kurz erwähnt |

**Closing-Bewegung:** Im Schluss zeige die Gleichung wieder, jetzt mit den dominanten Termen je nach Szenario hervorgehoben (offener Himmel: $I$ groß; Häuserschlucht: $M$ groß; künftiges PPP-System: $c\,\delta t_S$ wird wieder relevant).

---

## Minutenplan (10:00 ± 0:15)

| Zeit | Dauer | Sektion | Inhaltskern |
|---|---|---|---|
| 0:00–0:30 | 0:30 | **Wow + Leitfrage** | Kurzer Hook, Leitfrage nennen |
| 0:30–2:00 | 1:30 | **Wie funktioniert GNSS? + Pseudoentfernung** | Trilateration, 4 Satelliten für 4 Unbekannte, Gleichung als Roter Faden |
| 2:00–5:30 | 3:30 | **Block 1: Satellitenuhren** ($c\,\delta t_S$) | Stabilität (2:00) + Relativität (1:30) |
| 5:30–7:30 | 2:00 | **Block 2: Atmosphäre** ($I + T$) + Hilltop-Daten | Ionosphäre, Troposphäre, Hilltop-Restfehler 1,51 m DRMS + Anisotropie σ_E ≈ 6·σ_N |
| 7:30–9:15 | 1:45 | **Block 3: Multipath** ($M$) + Urban Canyon vs. Open Sky | Wellenphysik, Open-Sky vs. Häuserschlucht: DRMS 2,3×, R95 3,4×, C/N₀ −16 dB, 49→10 Sats |
| 9:15–10:00 | 0:45 | **Schluss + Beantwortung Leitfrage** | Welcher Term dominiert wann? Markanter letzter Satz |

**Total: 10:00.** A 15-second buffer in either direction is fine; >30 s over is a problem.

---

## Sektion 1: Wow + Leitfrage (0:00–0:30, 30 s)

Three live candidates — **pick one**:

1. **Eigene Daten als Kontrast-Hook:** "Drei Orte, drei physikalische Welten: auf einem freien Hügel streut mein Handy um 1,5 m. In der Häuserschlucht — gleiche Stadt, gleiches Handy, fünf Minuten später — um über 3 m, mit einzelnen Ausreißern bis 9 m. Im Hausflur: 10 Minuten lang kein einziger Fix. Was hat sich physikalisch geändert?" *(Unique to your project, primes Block 2 + Block 3 + Indoor-Negativbeispiel auf einmal.)*
2. **Relativitäts-Schock:** "Ohne Einsteins Korrektur würde GPS pro Tag um über 11 Kilometer falsch liegen — eine Position, die sich in 8 Sekunden um 1 Meter verschiebt." *(Classic, but everyone hears this one.)*
3. **Genauigkeits-Spektrum:** Eine einzige Zahl — von 5 m (Handy) bis 1 mm (geodätisches PPP) — und die Frage, was dazwischen passiert.

> **Korrektur zu früheren Versionen:** Die früher genannte Zahl "Faktor 3 daneben (1,25 m vs 3,8 m)" war ein Auswertungsfehler. Die echte gemessene Streuung auf dem Hügel ist **1,51 m DRMS**. Was das Handy intern als Genauigkeit *meldet*, ist Software-Telemetrie und für die Physik des Vortrags irrelevant — wird im Vortrag nicht erwähnt.

Then drop the Leitfrage on screen. Done.

---

## Sektion 2: Wie funktioniert GNSS? + Pseudoentfernung (0:30–2:00, 1:30)

Tight but doable. Cover in this order:

1. **Konzept Trilateration** (~20 s): Satelliten senden zeitgestempelte Signale aus bekannten Bahnen. Empfänger misst Laufzeit → Entfernung.
2. **Drei Satelliten = 3D-Position** (~15 s): Schnitt dreier Kugelflächen.
3. **Aber die Empfängeruhr** (~25 s): Das Handy hat keine Atomuhr — sein Uhrfehler ist eine vierte Unbekannte. Deshalb braucht man **vier Satelliten für vier Unbekannte** $(x, y, z, \delta t_R)$.
4. **Pseudoentfernungs-Gleichung einführen** (~30 s): Die Gleichung an die Wand. "Jedes Glied hier ist eine physikalische Limitierung. Diese drei" — Block 1, 2, 3 markieren — "schauen wir uns gleich an."

**Slide:** Diagramm mit 4 Satelliten + Gleichung mit farbig markierten Blöcken.

**AFB-Abdeckung:** AFB I (Wiedergabe des Trilaterationsprinzips).

---

## Sektion 3: Block 1 — Satellitenuhren (2:00–5:30, 3:30)

### 3a. Intrinsische Stabilität (2:00–4:00, 2:00)

- **1 ns = 30 cm.** Das ist die ganze Motivation für hochstabile Uhren.
- **Allan-Abweichung** als Maß einführen — *qualitativ*, nicht als Formel. Niedriger = stabiler. Auf der Slide nur den log-log-Plot zeigen, kein σ_y(τ)-Term auf der Folie.
- **Q-Faktor qualitativ:** gespeicherte Energie / pro-Zyklus dissipierte Energie. Höhere Übergangsfrequenz → grundsätzlich höheres Q-Potenzial → schmalere Linie → bessere Frequenzbestimmung.
- **Sprung Mikrowelle → Optisch:** Cäsium-Hyperfein (9,19 GHz) vs. Strontium-Gitter (429 THz) — der reine Frequenzsprung ist Faktor ~47 000. (Vorsichtig formulieren: das ist der Frequenzanteil, nicht das Gesamt-Q-Verhältnis.)
- **Aktuell im Orbit:** GPS = Rb + Cs, Galileo = PHM (10⁻¹⁴ in 10⁴ s) + Rb. Aktuell im Labor: Al⁺ bei 9,4×10⁻¹⁹ (NIST 2019), Sr bei 2,0×10⁻¹⁸ (JILA 2019), Yb bei 1,4×10⁻¹⁸ (NIST 2018).
- **Im All bereits oder geplant:** ACES (ISS, seit 21. April 2025 — *brandaktuell*), DSAC (NASA, 2019–2021), Tiangong Sr-Uhr (China, erste echte optische Uhr im All), COMPASSO (DLR, geplant).

**Slide:** Allan-deviation log-log plot mit Cs / PHM / Sr-Linien — visuell selbsterklärend.

**AFB-Abdeckung:** AFB I (was ist eine Atomuhr), AFB II (Q-Faktor-Argument anwenden).

### 3b. Relativistische Korrekturen (4:00–5:30, 1:30)

- **Spezielle RT:** Bahngeschwindigkeit ~3,87 km/s → Zeitdilatation ≈ −7,2 µs/Tag.
- **Allgemeine RT:** Gravitationspotential im Orbit höher als am Boden → Rotverschiebung ≈ +45,7 µs/Tag.
- **Netto:** +38,5 µs/Tag → würde unkorrigiert ~11,4 km/Tag **Pseudoentfernungs-Drift** ergeben (vorsichtig formulieren — siehe Anker im Project-Instructions, das ist *kein* 11 km/Tag Positionsfehler).
- **Lösung:** Werkfrequenz-Vorkorrektur Δf/f = −4,4647×10⁻¹⁰ — die Bordoszillatoren werden vor dem Start absichtlich um diesen Bruchteil zu langsam abgestimmt, sodass sie im Orbit gerade richtig laufen.
- **Sagnac** kurz erwähnen (Erdrotation während Signallaufzeit).
- **Optische Uhren wieder ins Spiel:** Bei 10⁻¹⁸-Niveau wird die Uhr empfindlich auf Höhenunterschiede von 1 cm (g·Δh/c² ≈ 1,09×10⁻¹⁸ pro cm) — *chronometrische Geodäsie* als Bonbon.

**Slide:** Zwei farbige Balken (SR negativ, GR positiv, Netto), darunter die +38,5 µs/Tag-Zahl.

**AFB-Abdeckung:** AFB II (Korrekturwert berechnen), AFB III (warum Galileo G2 noch keine optische Uhr hat — Übergang zu Block 2 möglich).

---

## Sektion 4: Block 2 — Atmosphäre (5:30–7:30, 2:00)

- **Ionosphäre** (~45 s): Dispersives Plasma, Δρ = 40,3·TEC/f² Meter. Typische Größe: 1–10 m im Zenit, bis 50 m bei niedriger Elevation. *Zwei Wege, das zu korrigieren:*
  - **Dual-Frequenz-Trick:** weil der Effekt frequenzabhängig (1/f²) ist, kann man ihn durch zwei Frequenzen herausrechnen. Eliminiert die erste Ordnung komplett.
  - **Klobuchar-Modell** (für single-frequency Empfänger): empirisches Modell von John Klobuchar (1987). Nimmt acht Koeffizienten (α₀–α₃, β₀–β₃), die jeder GPS-Satellit mitsendet, und schätzt damit die Ionosphäre als halbe-Kosinus-Welle über den Tag. Reduziert den $I$-Fehler um etwa **50 %** — der Rest bleibt.
  **Für unsere Daten:** Realme RMX3393 ist single-frequency (nur L1/E1/B1) — der Dual-Freq-Trick *nicht möglich*, also Klobuchar-Restfehler ist da.
- **Troposphäre** (~25 s): Nicht-dispersiv → Dual-Frequenz hilft *nicht*. Aufgeteilt in zwei Anteile:
  - **Trockener Anteil (ZHD)** ≈ 2,31 m am Meeresspiegel — vom **Saastamoinen-Modell** (1972) aus Luftdruck + Temperatur sehr gut berechenbar.
  - **Feuchter Anteil (ZWD)** = 5–40 cm — *nicht* aus Bodengrößen modellierbar, weil Wasserdampf in der Atmosphäre nicht der Druck folgt. **Das ist der eigentliche Tropo-Restfehler.**
- **Eigene Daten — Hilltop (offener Himmel)** (~50 s):
  - **Ein-Satz-Setup** (~8 s, *muss hier kommen, weil §5 darauf aufbaut*): "Ich habe mit der Google-GnssLogger-App auf einem Realme-Handy vier Sessions aufgenommen — Hügel mit offenem Himmel, Häuserschlucht, indoor — und schaue mir hier zuerst die Hügel-Daten an."
  - 11,6 Min Aufnahme, **698 GNSS-Fixe**, 5 Konstellationen sichtbar (GPS, Galileo, GLONASS, BeiDou, +SBAS).
  - **Gemessene horizontale Streuung: DRMS = 1,51 m.** Das ist der zusammengesetzte Restfehler aus *allen* Termen der Pseudoentfernungs-Gleichung gemeinsam: Ionosphäre-Restfehler nach Klobuchar, feuchter Tropo-Anteil nach Saastamoinen, Multipath, Geometrie (DOP), Empfängerrauschen. Single-frequency Handy unter offenem Himmel — das ist physikalisch der Boden, nicht Software-Schlamperei.
  - **Anisotropie als Bonbon-Befund:** σ_East = 1,49 m, σ_North = 0,25 m → **Faktor 6 Unterschied zwischen den Achsen**. Reine DOP-Geometrie — welche Achse schlecht ist, hängt davon ab, in welchem Streifen des Himmels die sichtbaren Sats liegen. Die "Fehlerkreis-um-den-Punkt"-Vorstellung ist falsch; reale GNSS-Streuung ist eine Ellipse, deren Orientierung die Satellitengeometrie bestimmt.

**Slide:** Hilltop-Streudiagramm (`01_fix_overview_hilltop.png`) mit sichtbarer Anisotropie-Ellipse. Zwei Zahlen groß: **DRMS = 1,51 m · σ_E ≈ 6·σ_N**.

**Fächerübergreifend-Anker:** Das Wort "Kalman-Filter" einmal fallen lassen — die diskrete Sprungstruktur der vertikalen Drift zeigt, dass die Empfängersoftware das Rohrauschen glättet und teilweise mit dem Barometer fusioniert. Nicht ausweiten, ein Satz reicht.

**AFB-Abdeckung:** AFB II (Anwendung der Klobuchar-Formel), AFB III (warum reicht single-frequency nicht).

---

## Sektion 5: Block 3 — Multipath + Urban Canyon (7:30–9:15, 1:45)

Diesmal ausführlich genug, um die Wellenphysik wirklich zu erklären — und die Daten geben hier am meisten her.

- **Wellenphysik des Multipath** (~25 s): Dasselbe Satellitensignal erreicht das Handy auf zwei Wegen — direkt und über eine Reflexion. Die beiden Wellen interferieren am Empfänger. Wegunterschied = halbe Wellenlänge → Auslöschung. Wegunterschied = ganze Wellenlänge → Verstärkung. Bei L1 ist λ ≈ **19 cm** — schon eine Reflexion an einer Hauswand, deren Weg sich um wenige Zentimeter vom direkten Pfad unterscheidet, kann zwischen "klares Signal" und "fast nichts" kippen. Das ist Doppelspalt-Physik mit GHz-Wellen.
- **Warum Häuserschluchten katastrophal sind** (~25 s):
  - **Nicht-Sichtverbindung (NLOS):** Direktes Signal blockiert, Empfänger trackt nur das reflektierte → falsche, *längere* Pseudoentfernung.
  - **Geometrie-Kollaps:** Sky-Window auf einen schmalen Streifen reduziert → DOP explodiert, Anisotropie-Achse kippt.
  - **Mehrfachreflexionen:** Glasfassaden, nasse Straßen, Hauswände → komplexe Interferenzmuster, die sich beim Gehen jede Sekunde ändern.

- **Eigene Daten — Hilltop vs. Urban Canyon** (~55 s):

  | Metrik | Hilltop | Urban Canyon | Verhältnis |
  |---|---:|---:|---:|
  | **Typischer Fehler** (DRMS) | 1,51 m | 3,48 m | **2,3×** |
  | **Schlechtester 5 %-Fall** (R95) | 2,59 m | 8,94 m | **3,4×** |
  | **C/N₀ p90, GPS** | 38,8 dB-Hz | 22,9 | **−16 dB** |
  | **C/N₀ p90, Galileo** | 36,7 dB-Hz | 17,7 | **−19 dB** |
  | **Sichtbare Sats (C/N₀ ≥ 25 dB)** | 49 | 10 | **5× weniger** |

  Zwei Aussagen, die sich direkt aus der Tabelle lesen lassen:

  1. **Die seltenen Ausreißer dominieren.** Der typische Fehler (DRMS) verdoppelt sich, aber der schlechteste Fall (R95) verdreieinhalbfacht sich. Das heißt: ein paar wenige Messungen werden katastrophal weit weggezogen, während die meisten erträglich bleiben. *Genau die Signatur, die NLOS-Reflexionen vorhersagen* — wenn das direkte Signal blockiert ist und nur eine Reflexion ankommt, ist diese eine Messung weit daneben, ohne dass sich die anderen ändern.
  2. **Signalstärke und nutzbare Geometrie kollabieren gemeinsam.** GPS verliert 16 dB, Galileo 19 dB; nutzbare Sats fallen von 49 auf 10. Aus dem Vollhimmel wird ein schmaler Streifen — DOP explodiert, Anisotropie-Achse kippt. Die Atmosphäre hat sich nicht geändert; die Geometrie und die Reflexionen alles.

**Slide:** Side-by-side gefilterte Skyplots aus `04_skyplot_compare.png` (Hilltop 49 Sats vs. Urban 10 Sats, jeweils C/N₀ ≥ 25 dB-Hz) + die DRMS/R95-Tabelle.

**AFB-Abdeckung:** AFB I (Multipath-Definition), AFB II (Wellenlänge λ ≈ 19 cm → Wegunterschiede dieser Größenordnung entscheiden über Interferenz), AFB III (warum löst dual-frequency Multipath *nicht* — anders als $I$ ist Multipath nicht dispersiv und kann nicht durch zwei Frequenzen aufgehoben werden).

> Hinweis: die frühere "BeiDou-12 50–100 s C/N₀-Oszillation"-Anekdote hat die Datenanalyse nicht bestätigt (BEI-12 zeigt σ = 3,4 dB ohne klare Periodizität). Wird ersatzlos gestrichen.

---

## Sektion 6: Schluss + Leitfrage (9:15–10:00, 0:45)

1. **Pseudoentfernungs-Gleichung wieder einblenden** mit szenarienabhängiger Hervorhebung — und für jedes Szenario eine eigene Datenzahl:
   - **Offener Himmel** (Hilltop): $I + T$ dominieren → Restfehler 1,51 m DRMS, weil weder Klobuchar (Ionosphäre) noch Saastamoinen (Troposphäre) den vollen Effekt aus single-frequency-Daten herausrechnen können.
   - **Häuserschlucht** (Urban): $M$ + Geometrie dominieren → R95 = 8,9 m, nur 10 von 49 Sats nutzbar.
   - **Indoor:** Signal stirbt ganz → 0 Fixe in 10 Minuten, obwohl der Almanach die Sats kennt.
   - **Künftige PPP/RTK-Architektur:** $c\,\delta t_S$ wird wieder zum Engpass — *dann* greifen optische Uhren.
2. **Leitfrage explizit beantworten** — die ehrliche Antwort ist *kontextabhängig*: Es gibt keinen einzelnen dominanten Term. Die Verbesserung von GNSS heißt, jeden Term im richtigen Anwendungsbereich anzugehen. Bonusaussage aus den Daten: nicht jede Limitierung ist physikalisch — mein Handy verfolgt 19 SBAS-Satelliten und dekodiert keinen einzigen, obwohl EGNOS über Europa frei eine Meter-Korrektur liefert. Eine selbst-auferlegte Hersteller-Limitierung kann genauso teuer sein wie die Atmosphäre.
3. **Markanter letzter Satz** — Vorschläge:
   - *"Eine optische Uhr im Galileo-Satelliten würde die Position meines Handys nicht um einen Millimeter verbessern — die Atmosphäre über meinem Kopf interessiert sich nicht für die Stabilität in 23 000 km Höhe."*
   - *"GNSS ist Einsteins meistbenutzte Technologie — und Einstein war erst der Anfang."*
   - *"Die nächsten zehn Jahre gehören nicht der einen großen Korrektur, sondern dem koordinierten Angriff auf jeden Term der Pseudoentfernungs-Gleichung."*

---

## Offene Entscheidungen

1. **Wow-Effekt:** Datenhook (1) vs. Relativitätshook (2) vs. Spektrum-Hook (3)?
2. **Fächerübergreifend-Anker:** Kalman-Filter im Atmosphäre-Block (mein Vorschlag) oder lieber Statistik/Allan-Abweichung im Uhrenblock?
3. **AFB-III-Pointe:** Welche der drei Schluss-Sätze? Oder eine eigene Variante?
4. **Visualisierungs-Schwerpunkt:** Pseudoentfernungs-Gleichung als statisches Bild über alle Blöcke einblenden (z. B. links unten als ständige Referenz), oder nur in Sektion 2 + 6?

---

## AFB-Abdeckungs-Check

| AFB | Hauptort | Backup |
|---|---|---|
| **I — Wiedergabe** | Wie funktioniert GNSS (Sektion 2), Was ist eine Atomuhr (3a) | Multipath-Definition (5) |
| **II — Anwendung** | Q-Faktor-Sprung berechnen (3a), Relativitätskorrektur (3b), Klobuchar (4), λ/4 (5) | viele |
| **III — Beurteilung** | Schluss-Antwort + szenarioabhängige Term-Dominanz (6) | "Warum reicht dual-frequency nicht für Multipath?" (5) |

Alle drei Bereiche sind zweimal abgedeckt — das ist robust gegen Kolloquium-Druck.

---

## Daten-Aufhängungs-Übersicht (welcher Befund hängt an welchem Pseudoentfernungs-Term?)

Schnellnachschlagewerk beim Folienbau — jede Aussage hat eine Quelle in `Datenbefunde.md` und eine Plot-Datei.

| Term | Block | Daten-Befund | Quelle |
|---|---|---|---|
| $c\,\delta t_R$ | §2 | (kein eigener Datenbefund auf Slide — nur das Argument "Handy-Quarz reicht nicht, daher 4 Sats statt 3") | — |
| $c\,\delta t_S$ | §3a | (kein eigener Datenbefund — Lehrbuch-Material) | — |
| $I + T$ | §4 | Hilltop: **DRMS = 1,51 m** als Restfehler-Boden eines single-frequency Handys mit Klobuchar/Saastamoinen; Anisotropie σ_E ≈ 6·σ_N (DOP, nicht Atmosphäre); 5 Konstellationen × single-frequency → kein Dual-Freq-Trick möglich | §4.4, `01_fix_overview_hilltop.png`, `02_session_comparison.png` |
| $M$ | §5 | Open-Sky vs. Urban: DRMS 1,51 → 3,48 m (2,3×); R95 2,59 → 8,94 m (3,4×, NLOS-Ausreißer); C/N₀ p90 GPS −16 dB / Galileo −19 dB; 49 → 10 nutzbare Sats | §4.1, §4.7, §4.8, `04_skyplot_compare.png` |
| Indoor (alles stirbt) | §1 oder §6 | 7 303 Status-Records, **0 Fixe** in 10 min — Almanach kennt Sats, aber kein Signal kommt durch | §3.4 |
| Vendor-policy | §6 | 19 SBAS-PRNs verfolgt, 0 dekodiert (MTK firmware) — EGNOS-Korrektur frei verfügbar, aber abgeschaltet | §4.14 |

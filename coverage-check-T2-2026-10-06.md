# Coverage and upload-lag check for T2 (18 Aug 2026 ММТС-9 power failure) — 6 Oct 2026

Pre-checks before running T2 (`ooni-column-test-plan-2026-10-06.md`). Two questions: (1) do the networks behind ММТС-9 have OONI coverage at the event hours; (2) does the pull window (upload day D plus upload hours 00–05 of D+1, as in T0/T1) lose measurements from probes that submit late or not at all, which T1's finding makes a live concern: T1 showed the 14 Jan volume drop to be mostly sessions waiting out timeouts, so for a power failure the volume signal, if any, has to come from absent or delayed submissions instead. Code and data: `T2/`.

## 1. Which ASNs sit behind ММТС-9

No MSK-IX or M9 membership list is on this machine, so the ASN set is taken from the instrument that already observed the event: the Atlas controller session log (msm 7000, `msm7000/2026-08.ndjson`), joined to `reference/probes-RU-2026-09-22.json` for location. A probe counts if its outage began 16:30–18:30 UTC on 18 Aug and lasted ≥ 20 min. Script inline in the session; outputs `T2/atlas_18aug_probes.csv` (per probe) and `T2/coverage-check-T2-asns.csv` (per ASN).

- 64 probes in 55 ASNs; 56 of the 64 are located within ~1.5° of Moscow. On the same two hours of 11, 17 and 19 Aug the rule selects 2–4 probes, so about 60 are excess.
- Onsets per 10 min: 17:00 3, **17:10 9, 17:20 19, 17:30 18**, 17:40 3, 17:50 3; reconnects cluster at **17:50–18:10** (31 of 48 outages shorter than 4 h). Median outage 55 min (p25 33, p75 228). **Event window for T2: 17:10–18:10 UTC**, core 17:10–17:50; with the ±60 min margin the analysis window is 16:10–19:10 UTC.
- This is a different selection from the "38 probe-outages" in the mechanism table (which used ≥ 30 min and the labelling run's instant); the ASN set is what matters here.
- Limit: the Atlas list is a sample of the networks behind M9, biased towards small hosting and business ISPs where Atlas probes sit. The two large Moscow fixed-line ISPs with OONI coverage, AS25513 МГТС and AS12389 Rostelecom, had no Atlas outage in the window, so they are not in the affected set; whether M9 touched them is unknown, and they cannot serve as a clean within-country control either (Rostelecom is nationwide). Five of the 64 onsets fall outside 17:00–17:50 (AS8369 16:36, AS39238 16:47, AS8402 18:08 ×2, AS42610 18:15, AS204997 18:10) and may be unrelated churn; AS8402 Corbina's two probes went down together at 18:08 for 12.8 h, which is worth a look in T2 but is not the main cluster.

## 2. OONI coverage of those ASNs

Monthly volume from `T0/raw_api/monthly/2026.json`; the criterion is T0's (≥ 14,400 measurements in the month ≈ 20 per hour). Hourly counts at the event hours from the raw pull (§3), all uploads.

| ASN | Holder | Atlas probes out (Moscow) | First onset | Jul | Aug | Sep 2026 | Aug per h | Raw n 17h / 18h UTC, 18 Aug | 17 Aug same hours | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| 8402 | Corbina / Beeline | 2 (2) | 18:08 | 151,848 | 157,088 | 164,444 | 211 | 203 / 108 | 134 / 57 | usable |
| 42610 | NCNET (Rostelecom Moscow) | 1 (1) | 18:15 | 49,741 | 92,799 | 171,084 | 125 | 130 / 80 | 45 / 27 | usable |
| 8369 | Intersvyaz (Chelyabinsk) | 1 (0) | 16:36 | 100,400 | 75,990 | 68,215 | 102 | 116 / 213 | 166 / 251 | usable, but not Moscow and onset early: likely unrelated |
| 35598 | Inetcom Carrier | 1 (1) | 17:04 | 100,748 | 57,654 | 62,723 | 77 | 0 / 100 | 0 / 200 | monthly usable, but 2 reports in the whole 16–20h window: one prober, not a population |
| 29124 | Iskratelecom | 1 (1) | 17:35 | 79,901 | 50,436 | 37,623 | 68 | 4 / 109 | 115 / 129 | usable at 60 min only from 18h; 17h is empty on 18 Aug |
| 25490 | STC (Rostelecom, not Moscow) | 1 (0) | 17:53 | 61,749 | 47,702 | 56,990 | 64 | 93 / 96 | 0 / 0 | one 100-input session per hour; not Moscow |
| 12714 | MegaFon (mobile) | 1 (1) | 17:27 | 69,119 | 43,654 | 80,469 | 59 | 23 / 26 | 0 / 120 | mobile; dropped by the hygiene filter where annotated |
| 34602 | Megasvyaz | 1 (1) | 17:11 | 12,613 | 13,197 | 13,739 | 18 | — | — | marginal (400 per day, flat: one scheduled prober) |
| 201825 | ER-Telecom Moscow | 3 (3) | 17:31 | 1,900 | 2,956 | 23,800 | 4 | — | — | no coverage in Aug (89 on 18 Aug) |
| 3267, 29182, 41601, 196949, 207957 | | 1 each | | | 2,585–5,160 | | 3–7 | | | no coverage |
| 41 other ASNs | | 1–3 each | | | 0–868 | | < 1.2 | | | no coverage |

Together the 55 ASNs hold 559,727 August measurements, 9.7 % of all-RU (5,764,971). In 16:00–20:00 UTC on 18 Aug they contribute 3,005 measurements in 1,526 reports (the seven monthly-usable ASNs 2,710 in 1,231), about 750 per hour, against 19,883 in the other RU ASNs.

**Coverage verdict for T2.** Per-ASN cells at 60-min bins are possible for **AS8402** and **AS42610** (both Moscow, both ≥ 80 per hour in 17h and 18h); AS8369 and AS25490 have the numbers but are not Moscow networks; AS29124 and AS35598 are empty or single-session in the 17h bin. The **pooled group of 55 Atlas-affected ASNs** is the unit with ~750 per hour, enough for 15-min bins. All-RU remains the main unit, as in T1. Within-country controls should be RU ASNs with coverage and no Moscow footprint: AS39028 (Ulyanovsk), AS35807 (SkyNet SPb), AS31200 (Novosibirsk), AS8369 (Chelyabinsk, if its 16:36 outage is confirmed unrelated). Note that AS8402's hourly volume on 18 Aug (203, 108) is above 17 Aug (134, 57): any volume reading for it will need all three baseline days.

## 3. Upload lag of 18 Aug measurements against the pull window

**Data.** Raw RU web_connectivity jsonl for upload days 17, 18, 19 and 20 Aug 2026, all 24 hours each (`T2/pull_lag.sh`, `T2/pull_17.sh`; 600 files, 11 GB, `T2/manifest.sha256`, SHA-256 of the manifest `35ed771dc1e699ee…`; 8 prefixes of 20 Aug needed one retry pass, none missing). 680,644 rows, none unparseable (`T2/extract_lag.py` → `derived/lag_<uploadday>.csv.gz`). Lag = whole hours between the measurement's start hour and the S3 upload hour (the pipeline's bucket); 0 means same hour. Observable lag for 18 Aug starts runs to 20 Aug 23:59, i.e. ~47 h past the end of the day. The pipeline's own count of 18 Aug measurements, from one aggregation API call (`T2/raw_api/daily_17_19.json`, rate limit remaining 1,778), is **160,577**, which includes whatever was uploaded after 20 Aug. Analysis: `T2/analyse_lag.py` → `derived/lag_summary.txt`.

| Start day | Pipeline count (API) | Seen in raw through 20 Aug 23:59 | Within pull window | Outside window | Share outside | Observable tail |
|---|---|---|---|---|---|---|
| 17 Aug (control) | 169,403 | 169,157 | 169,041 | 116 | 0.07 % | ~71 h |
| **18 Aug (event)** | **160,577** | **160,342** | **160,243** | **99** | **0.06 %** | ~47 h |
| 19 Aug | 167,491 | 167,151 | 167,130 | 21 | 0.01 % | ~23 h |

Lag distribution for 18 Aug starts: 99.31 % same hour, 0.36 % one hour, 0.11 % 2–5 h, 0.06 % 6–11 h, 0.03 % 12–23 h, 0.03 % ≥ 24 h; 0.09 % negative (probe clock ahead of the pipeline). 17 Aug is the same shape. The pull window therefore holds 99.8 % of the pipeline's count for 18 Aug (160,243 of 160,577), and the 235 measurements not seen in the raw bucket by 20 Aug 23:59 are 0.15 %.

**Who is late.** All 99 outside-window measurements of 18 Aug come from the mobile apps (95 Android, 4 iOS unattended), from nine ASNs, none of them in the Atlas-affected set: AS12389 Rostelecom 53, AS56621 17, AS12958 10, AS44056 8, AS31133 7, four others 1 each. Their start hours are spread over the day (08h 22, 16h 17, 22h 16, 23h 14, 14h 10, 18h 8, 19h 6 …) and they were uploaded in batches (19 Aug 20h 31, 20 Aug 22h 22, 19 Aug 17h 17, 19 Aug 14h 10), which looks like phones re-uploading stored results when the app next ran, not like networks coming back. In the event window 16:00–20:00 UTC, the 55 Atlas-affected ASNs have **zero** measurements outside the window and zero with lag ≥ 2 h (n = 3,005); the other RU ASNs have 32 outside (0.16 %) and 104 with lag ≥ 2 h (0.52 %). By start hour on 18 Aug, no hour has more than 0.32 % outside the window, and 17h has one.

**Reading.** Late submission is not a mechanism that could hide the 18 Aug event: measurements that are submitted at all are submitted within the hour, on the event day as on the control day, and nothing from the affected networks trickled in later. The D+1 05:00 window can stay. The 2026 raw rows carry no submission timestamp (no `measurement_uid`), so hourly is the finest lag resolution available from the bucket.

## 4. Non-submission: what the sessions did at the onset

The other half of the concern is probes that never submit because their uplink is dead. OONI submits each measurement as it completes, so a dead uplink produces absence (and, where the helper is unreachable but the probe is up, `control_failure`). This can only be seen as a change in volume or as sessions that stop. Two looks (`derived/session_continuity.txt`, `derived/straddling_reports_atlas_asns.csv`):

- Sessions (reports with ≥ 5 measurements in 16:10–17:10) still measuring within 10 min of the onset: **Atlas-affected ASNs: 1 on 18 Aug, and it stopped; 3 on 17 Aug and 2 on 19 Aug, all continued.** All-RU: 21 at risk on 18 Aug, 10 continued into 17:10–17:50, 11 stopped; 17 Aug 27 / 18 / 9; 19 Aug 17 / 8 / 9. No stopped session resumed under the same report ID after 17:50 on any day. The affected-ASN numbers are too small to carry a verdict; the all-RU stop rate on 18 Aug is within the range of the two neighbouring days.
- Most reports in the affected ASNs are Android unattended runs with one measurement per report (e.g. 40 single-measurement AS42610 reports in 17:00–17:10), so "did the session continue" cannot be asked of them; only volume can.
- 10-min volume in the Atlas-affected ASNs, 18 Aug against 17 Aug: 17:10 bin 53 against 204 (0.26), then 17:20–18:10 above 17 Aug (52/16, 101/15, 131/60, 181/52, 170/88, 151/60). The 17 Aug comparison bins for this group are 15–200 measurements, so a single day is no baseline; T2 needs all three baseline days and the pooled group. All-RU hourly starts: 17h 5,643 (17 Aug 5,990, 19 Aug 6,371), 18h 5,747 (8,985, 6,894): the 18h bin is 0.72 of the two-day mean, above T0's p1 of 0.594.
- A peek at the coarse outcome in 17:10–18:10, all inputs (not the T0 stage, not set F): TCP all-endpoints-failed share AS42610 0.10 (n = 100) against 0.02 before; AS12714 0.38 (n = 29, 10 % control failures); AS8402 0.04, flat; all-RU 0.06 against 0.05. Recorded here only so that T2's pre-registration is written knowing it exists; it is not a verdict.

## 5. Consequences for T2

1. **Window.** Event 17:10–18:10 UTC (core 17:10–17:50), analysis 16:10–19:10, bins 60/15/5 min as T1. Baseline days 17 Aug (D−1), 19 Aug (D+1), 11 Aug (D−7). 17 and 19 Aug are pulled in full in `T2/raw/` (with 20 Aug covering 19 Aug's D+1 hours); **11 Aug and 12 Aug 00–05 still need pulling.**
2. **Units.** All-RU; pooled Atlas-affected group (55 ASNs, `T2/coverage-check-T2-asns.csv`); AS8402 and AS42610 per ASN at 60 min; controls AS39028, AS35807, AS31200, plus US/DE/BR upload volume from `T2/s3_volume.csv` (17–20 Aug listed, 384 rows). Mark AS8369 and AS25490 as "Atlas outage, not Moscow" and report them separately.
3. **Volume as a signal.** Lag is ruled out as a confound (§3). Absence by non-submission cannot be separated from T1's throughput effect at the session level in these ASNs (§4), so T2 should predict volume per unit against three baseline days and read it together with `control_fail` and the TCP stage: a dead uplink gives absence plus helper failures; a blackholed route with the uplink up gives TCP connect timeouts and the throughput drop T1 described. Both are M2; what distinguishes M2 from a filter is that domestic and foreign inputs fail alike and recovery is fast.
4. **Prediction to write before the pull of 11 Aug**: in the pooled group, 15-min volume ratio < 0.594 in at least one bin of 17:10–17:50 or `tcp_fail`/`control_fail` share above the tier threshold, same for domestic and foreign inputs; nothing in the control ASNs; US/DE/BR steady; back to baseline by 18:30.

Files: `T2/pull_lag.sh`, `T2/pull_17.sh`, `T2/extract_lag.py`, `T2/analyse_lag.py`, `T2/s3_volume.sh`; `T2/raw/` (11 GB, 600 files, `manifest.sha256`); `T2/raw_api/daily_17_19.json`, `daily_asn_17_19.json` (API per-day and per-ASN counts, `manifest.sha256`); `T2/atlas_18aug_probes.csv`, `T2/coverage-check-T2-asns.csv`; `T2/derived/` (`lag_summary.txt`, `lag_by_start_day.csv`, `lag_18aug_by_start_hour.csv`, `usable_asns_18aug_hourly.csv`, `usable_asns_hourly_17_18_19.csv`, `straddling_reports_atlas_asns.csv`, `session_continuity.txt`, `lag_<uploadday>.csv.gz`).

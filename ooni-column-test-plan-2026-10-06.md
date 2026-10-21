# OONI column of the mechanism table — test plan (6 Oct 2026)

Purpose: fill the OONI column of `mechanism-instrument-table-fixed-line-2026-09-29.md` with observations, so we can decide whether OONI (subscriber-side, outbound) carries the attribution question (RQ2.2). Run in a separate session. The OONI API may not be reachable from the cloud workspace; if not, run from the Mac or the browser pane (as for the 5 Oct pulls).

Context docs referenced below are in `context/` next to this file.

## Already done (do not repeat, reuse as calibration)

- **14 Jan 2025, M6 (DPI failing closed)** — `jan14-2025-dissection-2026-10-05.md`: OONI shows it. Volume drops to ~¼ of flanking days; https non-.ru anomaly share 0.80 vs 0.40 baseline; raw HTTPS = TCP ok then TLS `generic_timeout_error`. Plain-HTTP measurements with `http_experiment_failure = timed_out` are labelled `anomaly=false, blocking=null`, so **OONI's anomaly flag under-counts this class** — use raw failure stages, not the flag.
- **4 May 2026, M4 (МГТС whitelist report)** — `may4-2026-mgts-builtins-ooni-2026-10-05.md`: OONI (≥4 sessions on AS25513) and Atlas (8 probes) both show no whitelist behaviour at the reported time. The report is uncorroborated, so 4 May cannot serve as an M4 anchor. M4 needs a different anchor event.

## Method common to every test

1. **Write the predicted OONI signature before pulling** (from the table, §2), dated, in the result doc.
2. **Unit:** OONI's vantage point is `(probe_cc, probe_asn)`; there is no persistent probe ID. Work per ASN for the affected ASNs, plus all-RU, plus a set of RU ASNs outside the event's reported scope as within-country control. (A DE control measures German conditions and is not informative for OONI.)
3. **Hygiene filters:** drop `annotations.network_type = mobile` (fixed-line scope); flag VPN-tainted measurements (geolocation mismatch between claimed ASN and egress — OONI's own analysis puts mismatch at ~7 % globally, Canada/Russia a common pair); keep the last measurement per report and input.
4. **Inputs:** restrict to "normally reachable" inputs, defined by raw stage, not by OONI's anomaly flag *(changed 6 Oct 2026 after T0 §3: the anomaly-based set used on 5 Oct keeps dead domains, broken certificates and sites that answer RU clients differently, and 13 % of its measurements fail on a quiet day)*. An input qualifies for day D if, on the baseline days (D−1, D+1, D−7), after the hygiene filters of step 3, it has ≥ 20 RU measurements and raw stage `ok` (step 5) in ≥ 90 % of the measurements whose control request succeeded. This needs the baseline days' raw `test_keys`; the aggregation API cannot supply it. Where the baseline days are not pulled raw, use the split-half rule from T0 (reports of day D halved by hash of `report_id`; an input qualifies for one half if it meets ≥ 10 measurements and the 90 % rule in the other half) and label the result provisional. Split inputs by: domestic (.ru/.su/.рф, RU-hosted) vs foreign; https vs http; and, where relevant, hosting ASN of the resolved IP.
5. **Outcome per measurement = failure stage from raw `test_keys`:** DNS failure / DNS inconsistent with control, TCP connect failure, TLS handshake failure (timeout vs reset vs alert), HTTP failure after handshake (timeout, reset, short body), ok. Do not rely on `anomaly`/`blocking` alone.
6. **Baseline and window:** event window ± a fixed timing margin (same margin for all tests); baseline = same clock hours on the day before, the day after, and the same weekday one week earlier. Report measurement **volume per bin** alongside shares — the volume drop was itself a signal on 14 Jan.
7. **Thresholds from quiet periods, not from the event:** set the "change" threshold so that ~1 % of quiet bins for that ASN exceed it; report n per bin so small bins are visible.
8. **Cell verdict:** observed / null / ambiguous / no coverage (too few measurements in the unit), with n.
9. **Data handling:** parallelize pulls across independent days/ASNs (state the concurrency setting); keep raw pulls with hashes, do not pull-and-delete.

## Tests, in priority order

**T0 — Instrument calibration (prerequisite).** On ~10 quiet days spread over 2022–2026: per-ASN variability of volume and per-stage failure shares by hour; how often the anomaly flag and the raw stage disagree; RU volume by month and by ASN (coverage over time — monthly RU cells fell from ~683k in March to ~405k in August 2026). Output: thresholds per ASN group and a coverage table. Every later test depends on this.

**T1 — Re-run 14 Jan 2025 (M6) with the stage-based method.** Method validation: it must reproduce the TLS-timeout signature and the volume drop. If it does not, fix the method before going on.

**T2 — Restriction vs failure: 18 Aug 2026 ММТС-9 power failure (M2).** Prediction: volume drop and failures at TCP connect for domestic and foreign inputs alike (no domestic/foreign split), in the affected ASNs only, then fast recovery. This is the negative control that separates an accident from a filter.

**T3 — 6–7 Dec 2024 Dagestan/Ingushetia drill (M3).** Prediction: in Dagestan/Ingushetia ASNs, foreign inputs fail (stage to be observed — TCP connect expected), domestic inputs ok, DNS ok. First check coverage: OONI geography is country-level, so identify the regional ISPs' ASNs first; expect few measurements. A clean M3 cell is what separates M3 from M4.

**T4 — Destination-range blocks (M8).** Anchors: Hetzner Nov 2024; Cloudflare/OVH/Hetzner/DigitalOcean June 2025. Prediction: TCP connect or TLS failures concentrated on inputs whose resolved IP sits in the listed ranges, with a step at onset; other foreign inputs unaffected.

**T5 — 16 KB cap (M5).** A standing condition, not an event: compare, within the same RU measurements, inputs served from affected ranges (e.g. Cloudflare) against others. Prediction: TLS handshake ok, then HTTP body read stalls/times out or is truncated (~16 KB). Feasibility question first: does web_connectivity record body length and the point of failure precisely enough to see this? This is the M5-vs-M8 pair.

**T6 — DNS intervention (M7).** Compare OONI DNS consistency failures per ASN with the Atlas finding (~5 % of RU probes see UDP/53 substitution, flat since Jan 2022) — a cross-instrument consistency check. Then the single report of `.ru` NXDOMAIN for ~3 min on 10 Sep 2026.

**T7 — Whitelist with a usable anchor (M4).** Candidate: 10 Sep 2026 Dom.ru Поволжье (forum 4625 #1658, disputed #1660). Identify the ER-Telecom ASNs serving the region from the registry. Prediction: foreign non-allowlisted inputs fail at TCP/TLS, allowlisted domestic services (Yandex, VK, Gosuslugi …) ok. Open: which allowlist to test against — find a published or reported list before pulling. If OONI shows nothing here too, record it alongside 4 May: two uncorroborated whitelist reports is itself a finding about the reports or the instruments.

## Output

One result doc per test (`ooni-T<n>-<event>-<date>.md`), and an updated OONI column in the mechanism table with each cell marked obs. / null / no coverage, n, and a link. At the end: which mechanism pairs OONI separates (M3/M4, M4/M6, M5/M8, M2 vs restriction), which it cannot, and why.

## Amendments, 6 Oct 2026 evening (Hannah, after reading T0, T1, T4 and T5)

These override method steps 2, 7 and 8 where they conflict. They apply to T2, T6, T7 and any re-run.

- **A1. Verdicts are per probe ASN only.** All-Russia and pooled groups are reported as description, without a verdict. Reason: an all-Russia share averages networks with and without the mechanism, weighted by probe volume, so its size measures the probe mix rather than the mechanism (T4 E1, T5).
- **A2. Every per-ASN cell states the number of setups it rests on.** A setup is `software_name`, `software_version` and `test_version`, plus `platform`, `engine_version` and `origin` where present. Give the number of distinct setups and of reports, both overall and among the failures. Setups are a lower bound on devices; reports are an upper bound. The counts for the existing T1/T4/T5 cells are in `setup-counts/setup_counts.csv`.
- **A3. Percentile thresholds are dropped** (step 7). A p99 over a few hundred hourly bins is the second- or third-largest value, and hours within a day are correlated. Judge a change by a contrast (event against baseline, affected group against control group) with an interval estimate that names its resampling unit, and report n and setups beside it.
- **A4. AS39028 is removed from all-Russia aggregates** and reported as its own unit, being one scripted deployment on one line (`AS39028/as39028-characterisation-2026-10-06.md`).
- **A5. 2026 events are judged against 2026 quiet days, and more of these will be pulled.** Check candidate days against the ntc.party fixed-line and DNS catalogues first. That check, with candidates, is in `ntc-party-check-test-days-2026-10-06.md`.

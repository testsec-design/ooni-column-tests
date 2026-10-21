# OONI T4: destination-range blocks (M8) — Hetzner, Nov 2024, and Cloudflare/OVH/Hetzner/DigitalOcean, June 2025

6 Oct 2026. Test T4 from `ooni-column-test-plan-2026-10-06.md`. Code and data are in `T4/`. T5 (`ooni-T5-16kb-cap-2026-10-06.md`) uses the same June 2025 pull and shares the hosting classification; the two were pre-registered together.

Terms used throughout: **stage** = where a measurement first failed (T0 §0.1, unchanged logic); **control-ok** = the test helper's own request succeeded; **blocked family** = failures at TCP connect or TLS handshake; **stall family** = TLS handshake succeeded and the HTTP exchange then failed; **strict set** = inputs that reached stage `ok` in ≥ 90 % of control-ok measurements on the baseline days; **balanced panel** = inputs with at least one measurement both before and after onset; **DiD** = difference-in-differences.

## Summary

- **November 2024, Hetzner: OONI sees the block, but as a selective one.** On Hetzner-hosted inputs that were reachable in late October, failures before the HTTP exchange (TCP connect or TLS handshake) rise from 0.2 % to 4.8 % of control-ok measurements across Russia, with a difference-in-differences of +4.4 points [2.9, 6.1] against other foreign inputs; nothing moves for Cloudflare, DigitalOcean, other foreign or domestic inputs. The rise is concentrated in a handful of networks: Telecom.ru AS50716 goes from 0 to 12 % [7.6, 17.9], smaller ISPs reach 14–47 %, while Rostelecom, MGTS and Beeline stay at zero. OVH-hosted inputs rise too (+6.9 points). The all-RU figure is below the pre-registered 10-point threshold, so by the rule the all-RU cell is *null* and the AS50716 cell is *observed*. The onset is at 18–19 UTC on 6 Nov 2024 and the block persists through 10 Nov.
- **The failure stage is not the one the forum described.** Within the blocked family, 71 % of the Hetzner failures are a completed TCP connect followed by a TLS-handshake timeout, and 28 % are TCP failures; plain-http Hetzner inputs fail at TCP. So the mechanism table's "M8 fails at connect/handshake" holds, but "connect" alone would have missed most of it.
- **June 2025: no connect-stage block for any of the four providers.** The blocked family's DiD is at most +0.6 points for Cloudflare, Hetzner, DigitalOcean, OVH and their pool. What rises is the stall family: TLS handshake ok, headers received, then HTTP timeout: Hetzner +13.9 points [10.2, 17.0], Cloudflare +7.8 [6.8, 9.0], OVH +7.7, DigitalOcean no significant change (11 inputs). On Rostelecom the stalls reach 28–38 %; on MGTS, MTS and SkyNet nothing happens in 10–12 June. For the M8 cell this event is *null*; it is the M5 event, analysed in T5. The step appears on 10 June at 04–05 UTC, not on 9 June.
- **Both control groups hold** in both events (other foreign and domestic within ±3 points in every family), control failures stay below 0.7 %, and Russian volume shows no outage shape.

## 0. Pre-registration

Written 6 Oct 2026 at **15:35 UTC**, before any OONI data for the event days was pulled.

**What I had seen before writing this.** The plan; the T0 result doc and its derived tables; the T1 result doc (§0 only, the rest is not yet written); the T3/T7 coverage check; the four context docs; the T0 and T1 code. From OONI data: only T0's already-downloaded quiet-day files, of which I read two `jsonl.gz` objects from upload hour 12 on each of 2024-09-18, 2025-02-19, 2025-09-21 and 2026-06-10 (about 3,000 measurements each) to find out which `test_keys` fields exist (needed for T5 step 1). No measurement from any event day or baseline day. From S3: a listing of object names and sizes for the candidate days (`T4/s3_size.csv`, 28.4 GB of jsonl in total). From outside OONI: the Cloudflare blog post of 26 Jun 2025, the ntc.party threads 12845 (Hetzner, Nov 2024, pages 1–2) and 17013 (June 2025, page 1), the Tor Project forum thread 16134, press summaries (heise, The Record, BleepingComputer, Zona), PeeringDB's `net` listing for the four providers, the CAIDA RouteViews prefix-to-AS files and the NRO delegated-stats file, all downloaded into `T4/reference/`. The ntc.party catalogue referenced by the mechanism table (`ntc-party-fixed-line-outages-catalogue-2026-09-23.md`) is not on this machine, as T0 already noted.

### 0.1 Anchor events and their dating

**E1 — Hetzner, November 2024.** The ntc.party thread "Недоступность Hetzner" (topic 12845) opens on 7 Nov 2024 at 15:25 (forum time) with sites on Hetzner unreachable "since yesterday"; a reply in the same hour says "since 17–18 MSK", and the first posts describe SYN packets with no answer while ping passes, on Yota, Beeline, MGTS and parts of Rostelecom, with MTS reportedly unaffected at first. A Tor Project forum post of 2 Dec 2024 (topic 16134) refers to "recent (from early November) problems" with AS24940, TCP on all ports failing, UDP failing and ICMP working, and notes that the block looked targeted and could be cleared for a while by stopping all outgoing traffic. One reply in 12845 says OVH addresses were blocked on some providers too. **Onset: 6 Nov 2024, afternoon UTC, uncertain by about one day.** Nothing read says when the block was lifted, so the after window may contain a lifted block; that is reported, not assumed. The mechanism table lists this as an M8 anchor; the first-hand reports say a connect-stage block (SYN dropped).

**E2 — Cloudflare / OVH / Hetzner / DigitalOcean, June 2025.** Cloudflare's own post ("Russian Internet users are unable to access the open Internet", 26 Jun 2025) says: "Since June 9, 2025, Internet users located in Russia and connecting to the open Internet have been throttled by Russian Internet Service Providers (ISPs)", that "the throttling allows Internet users to load only the first 16 KB of any web asset", that it affects HTTP/1.1 and HTTP/2 over TCP/TLS and HTTP/3 over QUIC, and names Rostelecom, Megafon, Vimpelcom, MTS and MGTS. The ntc.party thread "Блокировка Cloudflare, OVH, Hetzner, DigitalOcean… 09.06.2025" (topic 17013, opened by ValdikSS on 18 Jun 2025) describes, for Cloudflare, Hetzner and DigitalOcean, connections that freeze after about 16 KB of received data, and for OVH a different, earlier (28 May 2025) block triggered by UDP packets to other hosters' ranges, lasting about 10 minutes per trigger. Press (heise, The Record, BleepingComputer) repeats the 9 June date. **Onset: 9 Jun 2025 (Monday), dated to the day.** The exact hour is not given by any source; it is read from the onset-day hourly series (descriptive, P7).

A point to state plainly before seeing data: the mechanism table files E2 under M8 (connect/handshake failures), but the first-hand sources describe a transfer stall for three of the four providers, which is the table's M5 signature. T4 therefore pre-registers the table's prediction as primary (P5) and the source-based alternative (P5-alt) next to it, and scores both. OVH in E2 is reported separately because its block started twelve days before the baseline window.

### 0.2 Design, fixed in advance

**Days (UTC).** For each event, three groups of days: *baseline* (input selection only), *before* and *after* (comparison), plus the onset day (hourly series only, excluded from all shares).

| Event | Baseline (selection) | Before | Onset (excluded) | After |
|---|---|---|---|---|
| E1 Hetzner | 30 Oct, 31 Oct, 1 Nov 2024 | 3, 4, 5 Nov | 6 **and 7** Nov (one-day uncertainty) | 8, 9, 10 Nov |
| E2 June 2025 | 2, 3, 4 Jun 2025 | 6, 7, 8 Jun | 9 Jun | 10, 11, 12 Jun |

Baseline days are separate from the before days so that the before share is not biased downward by selecting on it. For each day D, upload-day D (00–23) plus upload hours 00–05 of D+1 are pulled, exactly as in T0/T1; measurements are assigned to days by `measurement_start_time`.

**Source and handling.** Public bucket `ooni-data-eu-fra`, `raw/<YYYYMMDD>/<HH>/RU/webconnectivity/*.jsonl.gz`, `--no-sign-request`. No call to `api.ooni.io`. One pull for both tests (`T4/pull_s3.sh`): 21 days + 4 next-morning stubs, 28.4 GB by listing, 8 hour-prefixes in parallel (`xargs -P 8`, aws-cli default 10 threads each; every object is an independent read, so concurrency cannot change the data). Files kept under `T4/raw/`, SHA-256 manifest `T4/manifest.sha256`; `T5/raw` is a symlink to `T4/raw`. Disk at pull time: 75 GB free; T1's pull (5 GB, running) shares the link.

**Hygiene (T0 §0.1, unchanged).** Drop `annotations.network_type = mobile`; keep the last measurement per `(report_id, input)`; drop measurements without `test_keys`; `control_fail` (the test helper's request failed) is its own class and every other share is computed among control-ok measurements. The canary-taint share per report is reported but **not** used as a filter (T0 §2 showed it marks networks, not VPNs).

**Stage.** T0's `extract_stages.py` logic, copied unchanged into `T4/extract_stages.py` (day set changed; byte-identical stage function, checked by diff), with two additions written into extra columns, not into the stage: (i) `http_code`: the status code of the first request's response (0 if no headers arrived), which tells "headers received, body stalled" from "nothing received"; (ii) `ctl_body_len`: `control.http_request.body_length`; (iii) the control's resolved IPs (`control.dns.addrs`).

**Hosting classification (constraint 5).** Per input, from the **control's** resolved addresses on the baseline days (union over its baseline measurements). Each address is mapped to an origin ASN by longest-prefix match in the CAIDA RouteViews prefix-to-AS file nearest the onset (`routeviews-rv2-20241106-1400` and `-rv6-20241106-0600` for E1; `-rv2-20250609-1200` and `-rv6-20250609-0600` for E2). The control's DNS answers carry no ASN field (checked on the T0 samples: `control.dns` has only `failure` and `addrs`), so prefix-to-AS is the method for every input; the method column therefore reads `pfx2as` throughout, and inputs whose control never resolved are `unresolved` and excluded. Provider ASN sets, verified against PeeringDB organisation records on 6 Oct 2026:

| Provider | PeeringDB org | ASNs counted | Also seen in the local AS-name table, kept as secondary |
|---|---|---|---|
| Hetzner | 12507 | 24940, 212317, 213230, 215859 | — (AS37153 "HETZNER" is xneelo, formerly Hetzner South Africa: excluded) |
| OVH | 1433 | 16276, 35540 | — |
| DigitalOcean | 8840 | 14061, 62567, 133165, 135340, 393406, 394362 | 200130, 201229, 202018, 202109 |
| Cloudflare | 4715 | 13335, 209242 | 132892, 203898, 394536 |

An input belongs to a provider if any control address maps to that provider's ASNs; an input mapping to two providers is `mixed` and excluded from the provider groups (count reported). **Domestic** = hostname TLD `.ru`, `.su` or `.рф`, or every control address in an ASN registered to RU in the NRO delegated-stats file (`T4/reference/nro-delegated-stats`, 5,764 RU ASNs). Everything else is **other foreign**. Groups are fixed on the baseline days and never re-assigned from event-day data.

**Inputs (constraint 3).** Strict set per event: inputs with ≥ 20 RU measurements after hygiene on the three baseline days and stage `ok` in ≥ 90 % of their control-ok measurements there. Then the balanced panel: of those, inputs measured at least once in the before window and at least once in the after window. The number of inputs at each step, per group, is reported. Primary analysis on **https** inputs; http inputs reported separately (plain http cannot show a handshake stage).

**Outcome families.** *Blocked* (M8): `tcp_fail`, `tls_timeout`, `tls_reset`, `tls_other`, `tls_or_http_unsplit`. *Stall* (M5): `http_timeout`, `http_reset`, `http_other` (by construction after a successful handshake when `tls_handshakes` is recorded), split by `http_code > 0` (headers received). *Other*: `dns_fail`, `tls_alert`, `http_diff`. Shares are among control-ok measurements of the group and period; `control_fail` is reported as a share of all measurements.

**Primary quantity.** For each event and family, all-RU, https, balanced panel:
DiD = (affected after − affected before) − (other foreign after − other foreign before), in share points. The affected group is Hetzner for E1 (OVH as a secondary affected group); for E2 each provider separately and the pool Hetzner + DigitalOcean + Cloudflare. Domestic is the second control group, reported alongside.

**Inference.** Measurements of one input are not independent, so the 95 % interval for every DiD and every within-group change is a cluster bootstrap over inputs (inputs resampled with replacement within each group, 2,000 replicates, percentile interval). "Statistically significant" means this interval excludes 0. For every share with n < 200, a Clopper–Pearson 95 % interval is given. Per-ASN results for the seven ASNs T0 found usable (AS12389, 25513, 8402, 35807, 50716, 8359, 31200) use the same estimator; a cell with fewer than 20 control-ok measurements in either period is *no coverage*. Hourly series on the onset day: blocked and stall share per hour for the affected group, with n, for reading the onset hour; no test is attached to it.

**"No change" rule** for the control groups (other foreign, domestic): the 95 % interval of (after − before) lies inside [−0.03, +0.03].

**Verdict rule for the M8 × OONI cell, per event.** *Observed* if, for the affected group, DiD(blocked) ≥ 0.10 with the interval excluding 0, and both control groups satisfy the no-change rule. *Observed with the M5 signature* (reported in the M8 cell as "ambiguous: stall, not connect") if DiD(stall) ≥ 0.10 with the interval excluding 0 while DiD(blocked) < 0.05. *Ambiguous* if the affected group rises in either family but a control group also moves, or if both families rise. *Null* if neither family's DiD reaches 0.05 with the interval excluding 0. *No coverage* if the affected balanced panel has fewer than 10 inputs or fewer than 200 control-ok measurements in either period. Per-ASN cells use the same thresholds.

**Volume.** All-RU hourly volume on the before/after days versus the baseline days (hygiene set), as a check that the event is not an outage (M2) in disguise; the per-ASN volume ratio is not used (T0 §4).

### 0.3 Predictions

| # | Quantity | Prediction |
|---|---|---|
| P1 | Strict set, https, balanced panel, per event | 800–2,500 inputs in total. Hetzner 10–60; Cloudflare 150–500; OVH 5–30; DigitalOcean 5–40; other foreign 300–1,200; domestic 200–800. In E2, OVH keeps fewer than half the inputs it keeps in E1 (its block began 28 May) |
| P2 | E1, Hetzner, all-RU | Blocked share before < 0.03; after 0.30–0.90; DiD(blocked) ≥ 0.30, interval excluding 0. Within the blocked family after onset, `tcp_fail` is ≥ 70 % (SYN dropped). DiD(stall) < 0.05 |
| P3 | E1, other groups | Cloudflare, DigitalOcean, other foreign and domestic satisfy the no-change rule in both families. OVH: a rise of 0–0.30 in the blocked family (one forum report), not predicted either way |
| P4 | E1, per ASN | Of the seven usable ASNs, at least four have coverage in both periods; among those, AS25513 (MGTS) and AS12389 (Rostelecom) show DiD(blocked) ≥ 0.20; AS8359 (MTS) shows a smaller DiD than AS25513 |
| P5 | E2, the table's prediction (M8) | Hetzner, DigitalOcean, Cloudflare and the pool: DiD(blocked) ≥ 0.20 with the interval excluding 0; DiD(stall) < 0.05; other foreign and domestic no change |
| P5-alt | E2, the sources' description (M5) | Hetzner, DigitalOcean, Cloudflare and the pool: DiD(stall) ≥ 0.20 with the interval excluding 0, DiD(blocked) < 0.05; among stalls after onset, headers were received (`http_code > 0`) in ≥ 50 %; other foreign and domestic no change. I expect P5-alt rather than P5 to hold, and say so now |
| P6 | E2, OVH | Already failing in the baseline: fewer than 10 inputs survive the strict set, so the OVH cell is *no coverage* |
| P7 | Onset hour | E1: the hourly blocked share of the Hetzner group first exceeds 0.20 between 12:00 and 18:00 UTC on 6 Nov and stays above it for the rest of 6 and 7 Nov. E2: the Cloudflare group's stall share first exceeds 0.20 in some hour of 9 Jun and stays above it |
| P8 | Volume | All-RU hourly volume on the before and after days stays within 0.58–1.7 × the baseline days' same-hour mean (T0's all-RU p1): no outage |
| P9 | `control_fail` | Below 0.05 of all measurements in every group and period. If OONI's test helpers themselves sit at one of the four providers, this fails and `control_fail` rises after onset in E2; that would be a finding about the instrument and is reported as such |
| P10 | E1 after window | The block persists through 10 Nov: the after share on 10 Nov is at least half of the 8 Nov share (no lift within the window) |

---

## 1. What was run, and how it differs from the pre-registration

**Run on 6 Oct 2026, 15:34–16:10 UTC. Complete.** Pull: 528 upload-hour prefixes, 1,689 `jsonl.gz` objects, 27 GB, no failed prefix, manifest `T4/manifest.sha256` (its own SHA-256 `a4dd3a1b61f1c681…`). Extraction: 2,150,956 lines, none unparseable, 2,150,642 kept (RU, on the 21 days or the next mornings). Concurrency as stated in §0.2 (8 prefixes in parallel; T1's pull ran on the same link at the same time). Classification: `T4/classify_hosting.py`; analysis: `T4/analyse.py` (summary in `T4/derived/summary.txt`).

| # | Planned | What was done | Consequence |
|---|---|---|---|
| D1 | Verdict rule: *observed* at DiD ≥ 0.10, *null* below 0.05 | The rule says nothing about 0.05–0.10 (T5's rule has the same gap between 0.05 and 0.20). Outcomes in that band are reported as **sub-threshold**: statistically significant by the stated test, below the observed threshold. Decided after seeing the data | Affects E1 OVH (0.069) and E2 Cloudflare/pool (0.078/0.082); the all-RU Hetzner result (0.044) falls on the null side of the rule as written |
| D2 | Domestic = TLD or RU-hosted, source unspecified | RU-registered ASNs taken from the NRO delegated-stats file (`T4/reference/`, 5,764 ASNs), a public non-OONI source not named in the brief | None expected; 309/312 domestic inputs per event, nearly all by TLD |
| D3 | — | Learned after §0 was written and before data were pulled: OONI's web-connectivity test helpers run on DigitalOcean (docs.ooni.org/devops); ntc.party 12845 pages 5 and 10 describe the Nov 2024 block as intermittent and selective by ISP, and "started working" on 12 Nov; ntc.party 17013 #886 (27 Apr 2026) reports mass 16 KB deployments in Moscow on 27 Dec 2025 and 14 Jan 2026 | P9 gains a second meaning (§4); the "selective" reading is consistent with the per-ASN results but was not used to change any prediction |
| D4 | Per-ASN results for the seven usable ASNs only | An exploratory breakdown over every probe ASN with ≥ 50 control-ok measurements of the affected group in the after window was added after seeing that the usable ASNs carry almost none of the signal (`T4/asn_breakdown.py`, `derived/asn_breakdown_<ev>.csv`) | Reported as exploratory in §3.4; no verdict rests on it |
| D5 | Hygiene step "drop measurements without `test_keys`" | No such measurement on any of the 21 days | None |

Everything else ran as pre-registered: days, hygiene, stage logic (byte-identical to T0, checked by diff), strict set from baseline days only, balanced panel, hosting from the control's addresses by prefix-to-AS, families, estimator, per-ASN rule.

## 2. Data and hygiene

| Event | Day | Role | Raw n | Mobile dropped | Dup dropped | After hygiene | In reports flagged by the canary proxy | Canary unknown |
|---|---|---|---|---|---|---|---|---|
| E1 | 2024-10-30 | baseline | 130,850 | 1,127 | 98 | 129,625 | 3.4 % | 2.9 % |
| E1 | 2024-10-31 | baseline | 132,537 | 1,044 | 32 | 131,461 | 3.9 % | 2.4 % |
| E1 | 2024-11-01 | baseline | 125,762 | 971 | 32 | 124,759 | 3.4 % | 2.0 % |
| E1 | 2024-11-03 | before | 120,091 | 796 | 16 | 119,279 | 2.9 % | 1.7 % |
| E1 | 2024-11-04 | before | 124,659 | 765 | 0 | 123,894 | 4.5 % | 0.6 % |
| E1 | 2024-11-05 | before | 128,856 | 1,069 | 8 | 127,779 | 2.9 % | 2.1 % |
| E1 | 2024-11-06 | onset (excluded) | 132,318 | 969 | 16 | 131,333 | 2.2 % | 1.2 % |
| E1 | 2024-11-07 | onset (excluded) | 116,570 | 366 | 0 | 116,204 | 4.1 % | 1.9 % |
| E1 | 2024-11-08 | after | 122,451 | 1,035 | 0 | 121,416 | 2.9 % | 0.6 % |
| E1 | 2024-11-09 | after | 116,976 | 445 | 8 | 116,523 | 3.4 % | 0.8 % |
| E1 | 2024-11-10 | after | 121,730 | 945 | 0 | 120,785 | 3.6 % | 1.3 % |
| E2 | 2025-06-02 | baseline | 76,412 | 81 | 0 | 76,331 | 11.1 % | 1.4 % |
| E2 | 2025-06-03 | baseline | 73,336 | 397 | 0 | 72,939 | 7.7 % | 4.0 % |
| E2 | 2025-06-04 | baseline | 73,354 | 164 | 0 | 73,190 | 6.1 % | 1.8 % |
| E2 | 2025-06-06 | before | 67,119 | 300 | 0 | 66,819 | 8.1 % | 2.6 % |
| E2 | 2025-06-07 | before | 65,226 | 402 | 0 | 64,824 | 6.7 % | 1.4 % |
| E2 | 2025-06-08 | before | 69,303 | 1,238 | 0 | 68,065 | 4.8 % | 1.8 % |
| E2 | 2025-06-09 | onset (excluded) | 63,569 | 1,260 | 0 | 62,309 | 4.0 % | 1.4 % |
| E2 | 2025-06-10 | after | 63,531 | 4,882 | 0 | 58,649 | 5.8 % | 7.7 % |
| E2 | 2025-06-11 | after | 63,840 | 3,140 | 0 | 60,700 | 3.0 % | 8.5 % |
| E2 | 2025-06-12 | after | 59,483 | 3,135 | 0 | 56,348 | 1.8 % | 6.4 % |

The canary share is reported, not filtered (T0 §2). In E2 it falls after onset (from 5–8 % to 2–6 %) while the "unknown" share rises; a likely reason is that canary sites fronted by Cloudflare now stall instead of answering, so fewer reports qualify as "canaries reachable". Mobile-labelled measurements jump on 10–12 June (3–5k per day against 80–1,200 before), a change in the probe population that the mobile filter removes.

**Input funnel** (hosting from the control's resolved addresses on the baseline days; method `pfx2as` for every resolved input, since the control's DNS answers carry no ASN field; 5 of 23,738 (E1) and 42 of 20,577 (E2) control addresses had no matching prefix).

| Group | E1: on baseline days → strict → https balanced panel | E2: same |
|---|---|---|
| Hetzner | 92 → 52 → **40** | 99 → 49 → **40** |
| OVH | 34 → 26 → **14** | 41 → 29 → **16** |
| DigitalOcean | 22 → 13 → **11** | 21 → 13 → **11** |
| Cloudflare | 812 → 419 → **346** | 801 → 413 → **351** |
| Other foreign | 1,379 → 905 → **687** | 1,301 → 881 → **701** |
| Domestic | 383 → 308 → **262** | 384 → 312 → **273** |
| Mixed (two providers) / unresolved | 12 / 73 → 5 / 7 → 3 / 7 (excluded) | 15 / 68 → 3 / 8 → 2 / 8 (excluded) |
| **Total https panel** | **1,370** | **1,402** |

Provider ASNs actually seen among the control addresses of strict inputs: Hetzner AS24940 (plus two addresses in AS213230 in E2), OVH AS16276, DigitalOcean AS14061, Cloudflare AS13335 and AS209242. None of the other secondary ASNs occurred. Every input is measured both before and after onset by construction; the panel loses no strict https input in either event.

## 3. Results

All shares below are among control-ok measurements of https inputs in the balanced panel, all-RU unless stated; intervals are the cluster bootstrap over inputs (DiD, changes) or Clopper–Pearson (shares with n < 200). Full tables: `derived/did_<ev>.csv`, `did_asn_<ev>.csv`, `did_http_<ev>.csv`, `composition_<ev>.csv`, `daily_<ev>.csv`, `hourly_<ev>.csv`, `volume_<ev>.csv`, `controlfail_<ev>.csv`.

### 3.1 E1, Hetzner, November 2024

| Group (inputs) | Blocked family: before | after | Δ [95 %] | DiD vs other foreign [95 %] | DiD vs domestic | Stall family DiD |
|---|---|---|---|---|---|---|
| **Hetzner (40)** | 0.002 (n 5,135) | **0.048** (n 5,036) | +0.046 [0.030, 0.063] | **+0.044 [0.029, 0.061]** | +0.042 [0.026, 0.062] | −0.001 [−0.002, 0.001] |
| OVH (14) | 0.004 (n 2,146) | **0.075** (n 2,049) | +0.071 [0.057, 0.089] | **+0.069 [0.055, 0.088]** | +0.067 | +0.003 [−0.003, 0.013] |
| DigitalOcean (11) | 0.006 (n 1,373) | 0.002 (n 1,306) | −0.004 [−0.007, 0.000] | −0.005 [−0.009, −0.001] | −0.007 | −0.001 |
| Cloudflare (346) | 0.002 (n 45,844) | 0.003 (n 43,926) | +0.001 [−0.001, 0.002] | −0.001 [−0.003, 0.001] | −0.003 | −0.000 |
| Other foreign (687) | 0.004 (n 84,209) | 0.005 (n 81,942) | +0.002 [0.000, 0.003] | — | −0.002 | — |
| Domestic (262) | 0.002 (n 29,672) | 0.006 (n 30,415) | +0.004 [−0.001, 0.011] | +0.002 [−0.003, 0.010] | — | −0.001 |

The Hetzner rise is entirely in the blocked family: `tcp_fail` 0.001 → 0.014 (DiD +0.011 [0.008, 0.015]) and `tls_timeout` 0.001 → 0.034 (DiD +0.033 [0.019, 0.048]); `tls_reset`, `http_timeout`, `http_reset` and the "other" family do not move. Of the 242 Hetzner failures in the after window, 171 (71 %) are TCP connected and then a TLS handshake timeout, 68 (28 %) are TCP failures, 3 are TLS resets or other. OVH looks the same (137 of 154 are TLS timeouts). The 12 plain-http Hetzner inputs fail at TCP: `tcp_fail` 0.001 → 0.186 (n 1,255 / 1,388; DiD +0.182 [0.004, 0.417], wide because 12 inputs).

**Time course** (Hetzner, blocked share per day, n 1,470–1,910 per day): 3–5 Nov 0.002–0.003; 6 Nov 0.024; 7 Nov 0.145; 8 Nov 0.063; 9 Nov 0.028; 10 Nov 0.051. Hourly on 6 Nov (n 35–126 per hour): 0.000 in every hour up to 17 UTC, 0.016 at 18, 0.085 at 19, 0.077 at 20, 0.129 at 21, 0.148 at 22, 0.123 at 23; on 7 Nov 0.07–0.25 in every hour. The onset in OONI is **18–19 UTC on 6 Nov 2024** (21–22 Moscow time); the forum's "since 17–18 MSK" is about four hours earlier and could not be checked more finely at this volume. The block does not lift within the window (P10).

**Per ASN, seven usable** (blocked family, Hetzner vs other foreign within the ASN):

| ASN | Before | After | DiD [95 %] | Cell |
|---|---|---|---|---|
| AS50716 Telecom.ru | 0.000 (n 246) | **0.121 [0.076, 0.179]** (n 174) | **+0.118 [0.063, 0.177]** | **observed** |
| AS12389 Rostelecom | 0.002 (n 439) | 0.002 (n 477) | +0.002 [−0.005, 0.008] | null |
| AS25513 MGTS | 0.000 (n 383) | 0.000 (n 434) | −0.002 [−0.005, −0.000] | null |
| AS8402 Beeline | 0.000 (n 233) | 0.004 (n 263) | +0.000 [−0.005, 0.010] | null |
| AS35807 SkyNet | 0.000 [0, 0.050] (n 72) | 0.009 [0, 0.048] (n 113) | +0.010 [0.000, 0.029] | null |
| AS31200 Novotelecom | 0.000 [0, 0.046] (n 79) | 0.000 [0, 0.051] (n 70) | +0.002 [0.000, 0.006] | null |
| AS8359 MTS | n 5 / 4 | | | no coverage |

OVH on the same ASNs: MGTS 0.000 → 0.022 [0.006, 0.054] (n 167/185, DiD +0.019 [−0.001, 0.044]); Telecom.ru 0 → 0.033 [0.004, 0.115] (n 82/60); the others at zero.

**Exploratory (D4): where the Hetzner failures sit.** Among probe ASNs with ≥ 50 Hetzner measurements after onset: NALTEL AS15868 0.469 [0.366, 0.573] (n 96), CityLink AS47236 0.232 [0.130, 0.364] (n 56), M-Line AS48558 0.139 (n 618; 0.000 before, n 654), ER-Telecom Krasnoyarsk AS50544 0.136 [0.070, 0.230] (n 81), Telecom.ru 0.121, Miralogic AS12668 0.118 [0.061, 0.202] (n 93), Timeweb AS9123 0.056, Ufanet AS24955 0.039, Rostelecom NCNET AS42610 0.024; and zero (upper CP bound ≤ 0.05) on Rostelecom, MGTS, Beeline, ER-Telecom Tula and RINET, Lanta, Novotelecom. OVH on M-Line: 0.373 (n 217). The block is selective by network, as the forum said; the large national ISPs' probes did not see it in 8–10 Nov.

**Checks.** `control_fail` ≤ 0.006 in every group and period. All-RU hourly volume on the before and after days is 0.67–1.42 of the baseline same-hour mean, no hour below 0.58: not an outage.

### 3.2 E2, Cloudflare / OVH / Hetzner / DigitalOcean, June 2025

| Group (inputs) | Blocked: before → after | Blocked DiD [95 %] | Stall: before → after | **Stall DiD [95 %]** | Stall DiD vs domestic |
|---|---|---|---|---|---|
| **Hetzner (40)** | 0.001 → 0.004 (n 2,905 / 2,551) | +0.002 [−0.001, 0.005] | 0.001 → **0.153** | **+0.139 [0.102, 0.170]** | +0.152 |
| DigitalOcean (11) | 0.005 → 0.002 (n 757 / 622) | −0.004 [−0.010, 0.002] | 0.001 → 0.019 | +0.005 [−0.017, 0.046] | +0.018 |
| **Cloudflare (351)** | 0.005 → 0.011 (n 25,475 / 22,066) | +0.006 [0.004, 0.008] | 0.002 → **0.093** | **+0.078 [0.068, 0.090]** | +0.091 |
| Pool H+DO+CF (402) | 0.004 → 0.010 (n 29,137 / 25,239) | +0.005 [0.003, 0.007] | 0.002 → **0.097** | **+0.082 [0.072, 0.093]** | +0.096 |
| OVH (16) | 0.004 → 0.006 (n 1,153 / 1,000) | +0.001 [−0.004, 0.005] | 0.008 → **0.098** | **+0.077 [0.027, 0.136]** | +0.091 |
| Other foreign (701) | 0.004 → 0.004 (n 45,926 / 39,431) | — | 0.002 → 0.015 (Δ +0.013 [0.009, 0.017]) | — | +0.013 |
| Domestic (273) | 0.002 → 0.003 (n 20,295 / 17,726) | +0.000 [−0.001, 0.002] | 0.002 → 0.002 | −0.013 [−0.018, −0.009] | — |

The stall family is almost entirely `http_timeout` (Hetzner 389 of 390 stalls; Cloudflare 1,994 of 2,047, plus 47 resets). Headers had been received before the timeout in 83 % (Hetzner), 92 % (DigitalOcean), 96 % (Cloudflare) and 76 % (OVH) of stalls, against 64 % for other foreign stalls and 24 % for domestic. The blocked family's only movement is Cloudflare's `tls_timeout` 0.004 → 0.010. Plain-http inputs: Cloudflare non-ok 0.040 → 0.106 (62 inputs); OVH 0.009 → 0.139; Hetzner's 9 http inputs fall (0.235 → 0.059) and are too few to read.

**Time course.** Cloudflare stall share per hour (n 220–460): on 9 June ≤ 0.01 until 13 UTC and 0.00–0.03 from 14 to 23 UTC; on 10 June 0.01–0.02 at 00–03 UTC, 0.045 at 04, **0.149 at 05 UTC**, then 0.05–0.13 for the rest of the day; Hetzner 0.20 at 05 UTC and 0.09–0.31 thereafter. Daily pool stall: 6–8 June 0.001–0.002, 9 June 0.009, 10 June 0.098, 11 June 0.172, 12 June 0.143. OONI dates the step to **10 June 2025, 04–05 UTC** (07–08 Moscow time), with at most a faint trace on the afternoon of 9 June.

**Per ASN, seven usable** (stall family; blocked family in brackets):

| ASN | Hetzner: before → after, DiD | Cloudflare: before → after, DiD | Cell |
|---|---|---|---|
| AS12389 Rostelecom | 0.002 → **0.375** (n 553/365), **+0.342 [0.254, 0.425]** [blocked −0.002] | 0.001 → **0.276** (n 5,532/3,396), **+0.243 [0.213, 0.275]** [blocked +0.034 [0.026, 0.041]] | **observed, stall** |
| AS25513 MGTS | 0.003 → 0.000 (n 287/205), −0.006 | 0.003 → 0.003 (n 2,568/1,876), −0.003 [−0.007, 0.002] | null |
| AS8402 Beeline | 0.000 → 0.022 (n 148/226), +0.019 [0.001, 0.043] | 0.000 → 0.018 (n 1,280/2,082), +0.016 [0.009, 0.022] | null (sub-threshold) |
| AS35807 SkyNet | 0 → 0 (n 84/51) | 0.003 → 0.004 (n 661/458), +0.002 | null |
| AS8359 MTS | n 15/37, no coverage | 0.000 → 0.008 (n 133/393), +0.002 [−0.011, 0.016] | null |
| AS31200 Novotelecom | n 142/2 | n 1,294/44 | no coverage after onset |
| AS50716 Telecom.ru | no measurements in June 2025 | | no coverage |

OVH on Rostelecom: 0.000 → 0.220 [0.160, 0.291] (n 239/168), DiD +0.189 [0.080, 0.313]. DigitalOcean on Rostelecom: 0.000 → 0.065 [0.024, 0.137] (n 174/92).

**Exploratory (D4): pool stall share after onset by probe ASN** (≥ 50 measurements): ER-Telecom Kazan AS41668 0.620 [0.543, 0.693] (n 171), Beeline AS16345 0.558 [0.413, 0.695] (n 52), Ufanet AS24955 0.434 (n 1,640), AS48524 0.386 (n 376), MTS AS35728 0.330 [0.264, 0.401] (n 191), Rostelecom 0.280 (n 3,853), AS207235 0.276, SIBMEDVED AS210616 0.170, ER-Telecom Samara AS34533 0.124 (n 459), Kamensk AS39812 0.067; and at or near zero: M-Line AS48558 (0.001, n 3,230), MGTS, ER-Telecom Tula AS52207 (n 1,201), RINET AS8331, PORTTEL, BIGTELECOM, SkyNet, MegaFon AS12714 (0.000, n 148), MTS AS8359 (0.007, n 439), Beeline Corbina AS8402 (0.018). Of the five ISPs Cloudflare named, only Rostelecom shows the cap in OONI's 10–12 June data through its main ASN; Beeline and MTS show it through other ASNs of theirs (AS16345, AS35728) and not through AS8402/AS8359; MegaFon's AS12714 and MGTS show nothing.

**Checks.** `control_fail` ≤ 0.003 after onset in every group: the probe's exchange with the DigitalOcean-hosted test helper (a few KB) is unaffected, which is itself evidence that DigitalOcean was capped, not blocked at connect. All-RU volume declines through the period (76k on 2 June to 56k on 12 June, a holiday); 7 of 144 before/after hours fall below 0.58 of the baseline same-hour mean, all night hours of 11–12 June (minimum 0.39 at 21 UTC on 11 June). This is a trend plus holiday, not an outage step.

## 4. Predictions scored

| # | Prediction | Outcome |
|---|---|---|
| P1 | Panel sizes within the stated ranges; OVH keeps < ½ as many inputs in E2 as in E1 | **Met** for every group (total 1,370 / 1,402; Hetzner 40; Cloudflare 346/351; OVH 14/16; DO 11; other foreign 687/701; domestic 262/273). **Not met** for OVH: 16 inputs in E2 against 14 in E1 |
| P2 | E1 Hetzner: before < 0.03; after 0.30–0.90; DiD ≥ 0.30; `tcp_fail` ≥ 70 % of the blocked family; stall DiD < 0.05 | Before **met**; after **not met** (0.048); DiD **not met** (0.044, though [0.029, 0.061] excludes 0); composition **not met** (TLS timeout 71 %, TCP fail 28 %); stall **met** |
| P3 | E1: Cloudflare, DO, other foreign, domestic no change; OVH 0–0.30 | **Met** (all four within ±0.03 in both families); OVH +0.069, inside the stated range but not a prediction |
| P4 | E1 per ASN: ≥ 4 with coverage; MGTS and Rostelecom DiD ≥ 0.20; MTS < MGTS | Coverage **met** (6); MGTS and Rostelecom **not met** (both ≈ 0); MTS no coverage |
| P5 | E2 (table, M8): blocked DiD ≥ 0.20 for Hetzner, DO, Cloudflare, pool; stall < 0.05 | **Not met** on every count: blocked DiD ≤ +0.006 |
| P5-alt | E2 (sources, M5): stall DiD ≥ 0.20, blocked < 0.05, headers ≥ 50 %, controls unchanged | Direction **met** for Hetzner (+0.139), Cloudflare (+0.078), pool (+0.082), OVH (+0.077), all with intervals excluding 0; magnitude ≥ 0.20 **not met** all-RU (met on Rostelecom: +0.342 / +0.243); blocked < 0.05 **met**; headers **met** (83–96 %); controls **met**. DO **not met** (+0.005, 11 inputs) |
| P6 | E2 OVH: < 10 inputs survive | **Not met**: 16 survive, and they stall after onset (0.098) |
| P7 | Onset hour: E1 crosses 0.20 between 12 and 18 UTC on 6 Nov; E2 crosses 0.20 in some hour of 9 June | E1 **not met** as stated: the rise begins at 18–19 UTC, reaches 0.15 on 6 Nov and 0.25 only in single hours of 7 Nov. E2 **not met**: nothing crosses 0.05 on 9 June; the step is at 04–05 UTC on 10 June |
| P8 | Volume ratio 0.58–1.7 in every before/after hour | E1 **met** (0.67–1.42). E2 **not met** formally (7 night hours of 11–12 June at 0.39–0.57, a downward trend and a holiday, not an outage) |
| P9 | `control_fail` < 0.05 everywhere | **Met** (≤ 0.006). The test helpers sit on DigitalOcean (D3), so the June result also says the helper exchange survived the cap |
| P10 | E1 block persists: 10 Nov ≥ ½ of 8 Nov | **Met** (0.051 vs 0.063) |

Tally: of the quantitative predictions, the ones about direction, specificity and the control groups were met; every prediction about magnitude was not. The mechanism table's prediction for June 2025 (P5) failed outright; the source-based alternative (P5-alt) held in direction and composition.

## 5. Verdict for the M8 × OONI cell

- **E1, Hetzner, Nov 2024. All-RU: null by the pre-registered rule** (DiD +0.044 < 0.05), with a statistically significant, stage-specific, provider-specific signal just under the line (cluster-bootstrap 95 % interval [0.029, 0.061]; other foreign and domestic flat). **AS50716 Telecom.ru: observed** (+0.118 [0.063, 0.177], n 174 after). Rostelecom, MGTS, Beeline, SkyNet, Novotelecom: null (n 70–477 per period). MTS: no coverage. Exploratory: observed-sized rises on five smaller ISPs (NALTEL, CityLink, M-Line, ER-Telecom Krasnoyarsk, Miralogic), consistent with the forum's account of a selective block.
- **E2, June 2025. Null for M8** in every group and every usable ASN (blocked-family DiD ≤ +0.034, the largest being Rostelecom's Cloudflare TLS timeouts 0.007 → 0.042). The event is present in OONI as the stall signature: Hetzner **ambiguous: stall, not connect** by the rule (+0.139 ≥ 0.10, blocked +0.002), Cloudflare and the pool sub-threshold for the same signature (+0.078 / +0.082), Rostelecom observed for the stall signature (+0.342 / +0.243). T5 carries this event.

## 6. Proposed wording for the M8 cell of the OONI column

> **obs. (selective)** — Nov 2024 Hetzner block: failures before the HTTP exchange (TCP ok then TLS timeout 71 %, TCP fail 28 %) on Hetzner-hosted inputs only; all-RU +4.4 pts [2.9, 6.1] (n 5.0k, below the 10-pt rule), AS50716 +11.8 [6.3, 17.7] (n 174), smaller ISPs 14–47 %, Rostelecom/MGTS/Beeline null. Onset 6 Nov 18–19 UTC, persists to 10 Nov. OVH +6.9. June 2025: **null for M8** — no connect/handshake rise for Cloudflare, Hetzner, OVH or DO (blocked DiD ≤ +0.6 pt); that event is M5 (see T5). `ooni-T4-range-blocks-2026-10-06.md`

## 7. Open questions

1. **Why TLS timeout rather than SYN drop in Nov 2024?** The forum reported unanswered SYNs; OONI's Hetzner failures are mostly a completed TCP connect followed by a handshake timeout, and plain-http inputs fail at TCP. One reading: the TSPU let the SYN through on some paths and dropped the ClientHello (or everything after the connect) on others; another: OONI's `tcp_connect` success reflects a middlebox completing the handshake. A look at the raw `tcp_connect` timings of the 171 TLS-timeout cases would tell them apart.
2. **Selectivity.** The usable national ASNs carried none of the Nov 2024 signal; smaller ISPs carried a lot. Whether that is the TSPU deployment, regional ordering, or probe placement (e.g. probes on hosting networks) cannot be told from OONI alone. The same pattern recurs in June 2025 (Rostelecom, Ufanet and ER-Telecom Kazan yes; MGTS, MegaFon AS12714 and MTS AS8359 no, at least in 10–12 June). The T0 thresholds, which are per ASN, were built for exactly this reason; the per-ASN cells are the ones to trust.
3. **Onset dating.** OONI puts the Nov 2024 onset about four hours after the forum's first time and the June 2025 step a day after Cloudflare's "since June 9". Either the first day was partial (Cloudflare's own data are global and not per hour) or probes only ran into the cap once daytime traffic began. Hourly per-ASN series for 9 June on Rostelecom would settle it but need more volume than one ASN has.
4. **The rule's magnitude thresholds** (10 and 20 points) were set for a nationwide block and turned out too high for selective ones; the pre-registered per-ASN cells gave the clean answer. For T6/T7, set the all-RU threshold from the per-ASN coverage expected, or state the verdict per ASN only.
5. The OVH rise in Nov 2024 (one forum mention) is real in OONI (+6.9 points, M-Line 37 %) and deserves its own anchor entry if the catalogue has one.


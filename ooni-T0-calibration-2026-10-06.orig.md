# OONI T0 — instrument calibration on quiet days

6 Oct 2026. Test T0 of `ooni-column-test-plan-2026-10-06.md`. Code and data in `T0/`.

## 0. Pre-registration (written 2026-10-06 13:11 UTC, before any data pull)

What had been seen before this section was written: the plan, the four context docs, and one connectivity check against the aggregation API (RU web_connectivity, 1 Jun 2026: 184,618 measurements, 57,530 anomaly, 17,198 failure) plus a 5-key S3 listing. Nothing else.

### 0.1 Design decisions fixed in advance

**Quiet days (10).** 2022-06-15 (Wed), 2022-11-16 (Wed), 2023-04-19 (Wed), 2023-09-16 (Sat), 2024-04-10 (Wed), 2024-09-18 (Wed), 2025-02-19 (Wed), 2025-09-21 (Sun), 2026-03-11 (Wed), 2026-06-10 (Wed). "Quiet" means: not within 7 days of any event named in the plan or the context docs (12 Mar 2022, Nov 2024 Hetzner, 6–7 Dec 2024, 14 and 24 Jan 2025, 20 Mar and 30 Mar–2 Apr 2025, Jun 2025 range blocks, 2–4 May 2026, 18 Aug 2026, 10 Sep 2026), and no nationwide fixed-line incident known to me on that date. The ntc.party catalogue (`ntc-party-fixed-line-outages-catalogue-2026-09-23.md`) is not on this machine, so the days have **not** been checked against it. Quietness is deliberately not judged from the OONI data itself.

**Source.** Raw measurements from the public S3 bucket `ooni-data-eu-fra`, `raw/<YYYYMMDD>/<HH>/RU/webconnectivity/*.jsonl.gz` (needed for `test_keys`). The bucket is partitioned by upload hour, so for quiet day D I pull upload-day D and upload-hours 00–05 of D+1 and keep measurements whose `measurement_start_time` falls on D (UTC). Anomaly/failure flags and the per-input baseline counts come from the OONI API (`api.ooni.io`), which is the only place the pipeline's `anomaly` flag exists.

**Unit (step 2).** `(probe_cc=RU, probe_asn)`. T0 has no event, so there is no affected/control split. Units reported: all-RU; each ASN singly where it has coverage; and ASN groups by volume tier, tiers fixed here: A ≥ 2,000 filtered measurements per quiet day (median over the days the ASN appears), B 500–1,999, C 100–499, D < 100.

**Hygiene (step 3).** (a) Drop `annotations.network_type = mobile`; measurements with no annotation are kept and counted separately. (b) VPN taint: OONI's own mismatch analysis uses the submission IP, which I do not expect to find in the public raw data. Proxy used instead, per report (`report_id`): a report is flagged if it measured ≥ 3 of the canary inputs and ≥ 50 % of them reached an HTTP response. Canaries = sites blocked on Russian networks for the whole period: `facebook.com`, `www.facebook.com`, `twitter.com`, `www.instagram.com`, `instagram.com`, `www.linkedin.com`, `www.bbc.com`, `meduza.io`, `www.svoboda.org`, `rutracker.org` (any scheme). Reports with < 3 canaries are "taint unknown". Flagged reports are excluded from the calibration statistics and their share reported. (c) Last measurement per `(report_id, input)`.

**Inputs (step 4).** For quiet day D the "normally reachable" set is chosen from D's baseline days (D−1, D+1, D−7), not from D: inputs with ≥ 20 RU measurements and anomaly share < 0.05 summed over those three days (aggregation API). Splits: domestic (`.ru/.su/.рф`) vs foreign by TLD; https vs http. "RU-hosted" and hosting-ASN splits are not needed for calibration and are left to the tests that use them.

**Outcome (step 5).** One stage per measurement from raw `test_keys`, first failing stage in this order: `dns_fail` (`dns_experiment_failure` set) → `tcp_fail` (TCP attempted, no endpoint connected) → `tls_timeout` / `tls_reset` / `tls_alert` / `tls_other` (https, no handshake succeeded) → `http_timeout` / `http_reset` / `http_other` (`http_experiment_failure` set after connect/handshake) → `http_diff` (response received; status mismatch, or body-length, headers and title all mismatch vs control) → `ok`. `dns_inconsistent` (`dns_consistency = inconsistent`) is a separate flag, not a stage, because a CDN answer can differ from the control and still work. If TLS vs HTTP cannot be told apart (no `tls_handshakes` recorded) the stage is `tls_or_http_unsplit`. Control status (`control_failure`, control HTTP failure) is recorded alongside.

**Window, margin, bins (step 6).** Timing margin fixed for all tests: **±60 min** around the reported event window. Bins: 60 min (primary) and 15 min, on `measurement_start_time` UTC. Baseline = same clock hours on D−1, D+1, D−7. In T0 raw stages are pulled for the quiet day only; the baseline days enter through the API (input selection, hourly volume per ASN). Consequence stated up front: T0 calibrates thresholds on the **absolute** per-bin stage share and on the **volume ratio** (bin volume ÷ mean of the three baseline same-hour volumes); a threshold on the *difference* in stage share against baseline would need raw pulls for 30 more days and is not calibrated here.

**Thresholds (step 7).** Per unit and bin size, threshold = 99th percentile over quiet bins of (i) non-ok stage share, (ii) each stage share, (iii) volume ratio (1st percentile, since the signal is a drop). Computed in bands of n per bin (20–49, 50–99, 100–199, ≥ 200); bins with n < 20 are "no coverage". n reported everywhere.

**Verdicts (step 8).** T0 fills no mechanism cell. The verdict here is per unit: *usable* (threshold estimable: ≥ 100 quiet bins with n ≥ 20) / *no coverage*.

**Data handling (step 9).** S3 downloads with 8 parallel workers (independent objects); API with 4 workers (independent day×slice reads). Concurrency cannot change the data. Raw files kept under `T0/raw/` with a SHA-256 manifest.

### 0.2 Predictions

| # | Quantity | Prediction |
|---|---|---|
| P1 | All-RU web_connectivity volume on the quiet days | 60k–200k per day; lower in 2022–23 than 2025; 2026-06-10 below 2026-03-11 |
| P2 | Hourly volume, all-RU | diurnal, max/min hour ratio 2–4; a quiet hour falls below 0.5 × baseline in fewer than 1 % of hours |
| P3 | Hourly volume, single ASN | bursty (depends on which probes run): outside the top ~5 ASNs the 1st-percentile volume ratio is ≈ 0, so a volume drop is not readable per ASN |
| P4 | Stage shares, normally-reachable inputs, all-RU | ok ≥ 0.92; non-ok 0.02–0.08; TLS/HTTP timeouts the largest failure class; `dns_fail` < 0.01; `tcp_fail` < 0.02 |
| P5 | 99th-percentile non-ok share per hour | all-RU ≤ 0.15; tier-A ASNs 0.15–0.35; small-n bins (20–49) can reach 1.0 by chance |
| P6 | Anomaly flag vs raw stage | of measurements with a raw failure stage, > 30 % carry `anomaly=false` (the 14 Jan plain-HTTP timeout class); of `anomaly=true` on normally-reachable inputs, most are `dns_inconsistent` with stage ok |
| P7 | Coverage by ASN | top 10 ASNs hold > 50 % of volume; ≤ 15 ASNs reach n ≥ 20 normally-reachable measurements in at least half of the hours; monthly volume falls through 2026 |
| P8 | Mobile | `network_type` present on a minority of measurements (mobile app only); of annotated ones 10–40 % mobile |
| P9 | VPN taint (canary proxy) | 3–12 % of measurements sit in flagged reports (OONI's global mismatch figure is ~7 %) |
| P10 | TLS/HTTP split | `tls_handshakes` present for https inputs on all ten days; unsplit share < 5 % |

---

## 1. Status and deviations from §0

**Run 6 Oct 2026, 13:40–15:00 UTC. Result: partial.** The raw-data half of T0 is complete. The API half was cut off by the OONI API's per-IP quota (HTTP 429, `x-ratelimit-remaining: 0`) after 31 responses; I stopped the pull at that point. Everything marked *provisional* below needs `python T0/pull_api.py` (resumable, skips what exists) and `python T0/analyse.py` to be re-run once the quota is back.

| # | Pre-registered | What was done | Effect |
|---|---|---|---|
| D1 | Normally-reachable inputs from API per-input counts on D−1, D+1, D−7 | API delivered none of these. *Provisional substitute:* split the reports of day D in two halves (hash of `report_id`); an input qualifies for one half if in the other half it has ≥ 10 measurements and probe-side anomaly share < 0.05. No measurement takes part in its own selection | Same-day rather than baseline-day selection. A circular same-day selection gives nearly the same thresholds (§3), so the bias is small, but this is not the plan's definition |
| D2 | `anomaly` flag from the API measurement list | Not delivered. *Proxy:* `test_keys.blocking` set (not `false`/`null`), the field the pipeline's flag is derived from. Equivalence not verified here | §5 compares stage against the probe-side verdict, not the published flag |
| D3 | Stage order without a control class | Added `control_fail` (test-helper request failed) as its own class ahead of the others; other stage shares are computed among control-ok measurements. Found from the data: see §2 | The pre-registered `nonok` is still reported (`nonok_prereg`) |
| D4 | One input set | Added a *strict* set (D1 plus: raw stage ok in ≥ 90 % of the other half's control-ok measurements), post hoc, because the anomaly-based set is not "reachable" (§3) | Reported next to the primary set, labelled |
| D5 | Volume ratio on 10 days | Hourly API counts exist for 6 days only (2022-06 → 2024-09); the four 2025–26 days are missing | Volume thresholds do not cover the current era |
| D6 | Canary "reached an HTTP response" | Implemented as raw stage `ok` (a blockpage also is an HTTP response) | Stricter, intended reading |

Not done: quiet days were not checked against the ntc.party catalogue (not on this machine); DNS-inconsistency and hosting-ASN splits; VPN taint by OONI's own method (submission IP is not in the public data).

## 2. Data and hygiene

Raw: 1,605 `jsonl.gz` files, 19 GB, 1,446,791 lines, 0 unparseable; 1,126,525 measurements started on the ten quiet days (the rest started on the following mornings). `T0/manifest.sha256` (SHA-256 of the manifest: `a1f77b603eb3fc28…`), `T0/manifest_api.sha256` (31 API responses). Concurrency as stated in §0.

| Day | raw n | no `network_type` | mobile dropped | in tainted reports | taint unknown | after hygiene | on normally-reachable inputs (F) |
|---|---|---|---|---|---|---|---|
| 2022-06-15 | 97,361 | 65 % | 220 | 8.4 % | 0.5 % | 89,004 | 61,059 |
| 2022-11-16 | 76,616 | 58 % | 2,536 | 15.6 % | 1.0 % | 62,559 | 34,005 |
| 2023-04-19 | 60,746 | 75 % | 88 | 6.6 % | 1.5 % | 56,681 | 24,199 |
| 2023-09-16 | 123,821 | 64 % | 949 | 21.7 % | 0.5 % | 96,212 | 61,619 |
| 2024-04-10 | 78,935 | 51 % | 1,620 | 7.9 % | 2.9 % | 71,211 | 30,584 |
| 2024-09-18 | 177,192 | 71 % | 2,083 | 5.9 % | 0.8 % | 164,817 | 105,756 |
| 2025-02-19 | 84,200 | 85 % | 646 | 8.0 % | 1.9 % | 76,904 | 38,041 |
| 2025-09-21 | 118,301 | 67 % | 706 | 2.5 % | 2.8 % | 114,532 | 63,755 |
| 2026-03-11 | 134,244 | 89 % | 3,540 | 16.2 % | 39.7 % | 109,507 | 44,448 |
| 2026-06-10 | 175,109 | 70 % | 11,522 | 18.1 % | 53.2 % | 133,960 | 42,708 |

- **Mobile filter is weak.** 51–89 % of measurements carry no `network_type`, so "drop mobile" removes only what the mobile app labels. Mobile is 0.6–8 % of annotated measurements until 2025 and 22–23 % in 2026.
- **The canary flag does not isolate VPNs.** Canaries are blocked as expected (ok share 8–20 % per canary), but flagged reports concentrate in particular networks: AS34665 100 % of 19,924 measurements, AS9009 52 %, AS9123 Timeweb 46 %, AS12668 43 %, AS12714 MegaFon 33 %, AS51645 ER-Telecom Irkutsk 33 %; AS25513 1.4 %, AS50716 2.7 %. It flags any vantage point where blocked sites work — VPN, hosting, or an ISP segment without filtering. In 2026, 40–53 % of measurements sit in reports with fewer than 3 canaries, so the flag is mostly undefined there. `derived/taint_per_asn.csv`.
- Duplicates per `(report_id, input)`: 193 in total. Upload lag is negligible: ≤ 222 of a day's measurements arrive in the next day's first six upload hours.
- **Three of the ten days are not quiet for the instrument.** Two have control-failure episodes, one a submission gap. `control_failure` share per hour is ≤ 0.05 on eight days. On 2023-04-19 it is 0.03–0.24 (06–20 UTC). On **2024-04-10 it is 0.17–0.52 from 00 to 13 UTC**, in 46 ASNs, error `httpapi: all endpoints failed` (test helpers unreachable), and 11,050 of those 13,547 measurements also show a probe-side TCP timeout at 60 s. Whether this was an OONI backend problem or reachability of the helpers from Russia is not established. Without the control class this day alone puts all-RU `tcp_fail` at 18 %.
- **2026-03-11, ~13:30–22:00 UTC: OONI-wide submission gap.** RU web_connectivity falls from ~10,000–12,000 measurements per hour to 55–165 (15, 16, 17 and 21 UTC), with partial recovery at 18–20 UTC, and is back at 7,500 at 22 UTC. The same hours are near-empty in the bucket for US (125 MB → 0 MB per upload hour), DE and BR, so the cause is on OONI's side, not in Russia. Seen from RU alone it is a volume drop to ~1 % of normal lasting eight hours.

## 3. Stage shares on quiet days

All-RU, set F, pooled over the ten days (n = 506,174): ok 0.869, control_fail 0.025, http_diff 0.043, dns_fail 0.020, tls_alert 0.017, http_timeout 0.011, tls_timeout 0.005, tcp_fail 0.003, tls_reset 0.002. Per day: `derived/stage_shares_per_day.csv`.

**The anomaly-based "normally reachable" set is not a reachable set.** An input whose domain is dead (NXDOMAIN for probe and control alike), whose certificate is broken, or which answers Russian clients with a different status passes "anomaly share < 0.05" because OONI does not call those anomalies. 13 % of F is non-ok on a quiet day. The strict set (D4) removes them:

| All-RU, 60-min bins (240) | n | netfail median | netfail p99 | http_diff p99 |
|---|---|---|---|---|
| F (provisional primary) | 506,174 | 0.048 | 0.194 | 0.077 |
| strict set | 444,289 | 0.010 | 0.066 | 0.010 |
| circular same-day selection | 523,374 | 0.048 | 0.172 | 0.072 |
| no input restriction | 975,387 | 0.317 | 0.506 | 0.065 |

`netfail` = DNS, TCP, TLS or HTTP failure among control-ok measurements (excludes http_diff).

**The baseline moves with the era.** Median hourly all-RU netfail on the strict set: 0.004–0.008 for the six days up to Sept 2024 except 0.017 on 2024-04-10; 0.010 in Sept 2025; **0.028 on 2026-03-11 and 0.051 on 2026-06-10** (F: 0.03–0.07, then 0.13 and 0.17). The 2026 rise is HTTP timeouts (4.5–5.7 % of F, 0.1–0.3 % before), DNS failures and TLS failures. The 2026-03-11 maximum of 0.207 (strict set) falls inside that day's submission gap, where an hour holds a few dozen measurements. `derived/allru_hourly_per_day.csv`.

Splits (F, among control-ok): netfail https-foreign 0.062, https-domestic 0.074, http-foreign 0.063, http-domestic 0.105 (dns_fail 0.080). Domestic inputs are not cleaner than foreign ones on quiet days.

## 4. Thresholds (provisional: D1, D3, D5)

99th percentile over quiet bins with n ≥ 20; a later test calls a "change" when the bin exceeds it. Full table by n band, both bin sizes, all stage families: `derived/thresholds_stage_share.csv`.

| Unit, 60-min bins, set F | quiet bins | median n | control_fail p99 | netfail p50 / p99 | tls_any p99 | tls_timeout p99 | tcp_fail p99 | dns_fail p99 | nonok_prereg p99 |
|---|---|---|---|---|---|---|---|---|---|
| all-RU | 240 | 1,965 | 0.51 | 0.048 / 0.19 | 0.070 | 0.020 | 0.017 | 0.068 | 0.40 |
| tier A, per-ASN bins, n ≥ 200 | 318 | 372 | 0.19 | 0.044 / 0.23 | 0.071 | 0.031 | 0.018 | 0.10 | 0.32 |
| tier A, 100–199 | 176 | 142 | 0.65 | 0.046 / 0.32 | 0.15 | 0.046 | 0.028 | 0.18 | 0.45 |
| tier B, n ≥ 200 | 143 | 306 | 0.02 | 0.030 / 0.12 | 0.054 | 0.018 | 0.044 | 0.047 | 0.17 |
| tier B, 100–199 | 282 | 132 | 0.17 | 0.039 / 0.21 | 0.11 | 0.038 | 0.028 | 0.085 | 0.28 |
| tier B, 50–99 | 989 | 67 | 1.0 | 0.036 / 0.28 | 0.11 | 0.049 | 0.041 | 0.099 | 1.0 |
| tier B, 20–49 | 669 | 36 | 1.0 | 0.078 / 0.39 | 0.23 | 0.093 | 0.050 | 0.19 | 1.0 |
| tier C, 100–199 | 158 | 129 | 0.50 | 0.036 / 0.19 | 0.081 | 0.042 | 0.024 | 0.079 | 0.37 |
| tier C, 50–99 | 854 | 66 | 1.0 | 0.041 / 0.22 | 0.14 | 0.052 | 0.038 | 0.13 | 1.0 |
| tier C, 20–49 | 734 | 35 | 1.0 | 0.083 / 0.62 | 0.31 | 0.17 | 0.13 | 0.26 | 1.0 |
| tier D, n ≥ 20 | 407 | 48 | 0.82 | 0.057 / 0.45 | 0.26 | 0.15 | 0.10 | 0.22 | 0.52 |
| AS12389 Rostelecom | 230 | 216 | 0.72 | 0.045 / 0.32 | 0.096 | 0.039 | 0.030 | 0.16 | 0.43 |
| AS25513 МГТС | 209 | 133 | 0.38 | 0.047 / 0.37 | 0.20 | 0.059 | 0.031 | 0.14 | 0.61 |
| AS8402 Beeline (Corbina) | 176 | 83 | 1.0 | 0.042 / 0.37 | 0.13 | 0.084 | 0.032 | 0.12 | 1.0 |
| AS35807 SkyNet | 163 | 73 | 1.0 | 0.035 / 0.20 | 0.13 | 0.036 | 0.016 | 0.086 | 0.39 |
| AS50716 Telecom.ru | 126 | 130 | 0.02 | 0.035 / 0.19 | 0.12 | 0.033 | 0.007 | 0.094 | 0.30 |
| AS8359 МТС | 114 | 83 | 0.88 | 0.066 / 0.31 | 0.16 | 0.056 | 0.044 | 0.14 | 0.93 |
| AS31200 Novotelecom | 113 | 66 | 1.0 | 0.042 / 0.25 | 0.14 | 0.045 | 0.020 | 0.14 | 1.0 |

Strict set, per-ASN 60-min bins with n ≥ 100: netfail p99 0.12 (tier A), 0.085 (B), 0.064 (C); tls_any p99 0.042 / 0.032 / 0.046; tcp_fail p99 0.026 / 0.033 / 0.019.

How to read this:
- The 14 Jan 2025 signature (failure share 0.8–0.9 at the TLS stage) clears every stage-specific threshold by a wide margin, in any unit with n ≥ 50. An effect of the size seen on 4 May 2026 (anomaly share ~0.03) is below every threshold.
- Stage-specific thresholds are far tighter than the aggregate: all-RU `tls_timeout` p99 is 0.02 and `tcp_fail` 0.017, against 0.40 for the pre-registered non-ok share.
- A p99 of 1.0 means a single probe session can fill a bin with one failure class. `control_fail` does this in every tier.
- These pool 2022–2026. Given §3, a 2026 event should be judged against 2026 quiet bins; ten days cannot give a per-era 99th percentile (24 bins per day).

**Volume ratio** (hour ÷ mean of the same hour on D−1, D+1, D−7; API counts, no hygiene filter; 6 days, `derived/thresholds_volume_ratio.csv`):

| Unit | quiet bins | p1 | p5 | p50 | share of quiet bins < 0.5 | < 0.25 |
|---|---|---|---|---|---|---|
| all-RU | 144 | 0.58 | 0.70 | 1.02 | 0 | 0 |
| AS12389 | 144 | 0.00 | 0.23 | 0.99 | 13 % | 5.6 % |
| AS25513 | 144 | 0.00 | 0.01 | 1.04 | 22 % | 9.7 % |
| tier A / B / C / D pooled | 424 / 1,796 / 1,818 / 1,115 | 0 | 0 | 1.0 / 1.0 / 0 / 0 | 24 / 31 / 56 / 80 % | 15 / 28 / 54 / 79 % |

All-RU: a drop below ~0.58 of baseline is beyond the 1 % level on these six days, so the −75 % of 14 Jan 2025 is far outside their variation. But 2026-03-11 (§2, not among the six) shows a drop to ~1 % caused by OONI itself, so **an all-RU volume drop is only evidence about Russia if other countries' volume holds at the same time.** Plan step 2 rules out a non-RU control; for volume it is needed. Per ASN, volume drop is not a usable signal: even Rostelecom falls to zero in more than 1 % of quiet hours.

## 5. Probe-side verdict versus raw stage (proxy for the anomaly flag, D2)

| | hygiene set, all inputs (n = 975,387) | F (n = 506,174) |
|---|---|---|
| Raw stage not ok (incl. control_fail) | 376,911 | 66,351 |
| … of these not flagged | 116,207 (**31 %**) | 60,760 (**92 %**) |
| Flagged | 261,051 | 5,598 |
| … of these raw stage ok | 347 (0.1 %) | 7 |

Unflagged share by stage, all inputs: control_fail 100 %, http_diff 74 %, tls_alert 57 %, dns_fail 54 %, **http_timeout 46 %**, tls_other 37 %, http_reset 11 %, tls_reset 6 %, tls_timeout 4 %, tcp_fail 2 %. The flag follows TLS timeouts and resets and TCP failures closely; it misses about half of HTTP timeouts (the 14 Jan plain-HTTP class) and all control failures. `dns_inconsistent` is set on 91,398 measurements, of which 27,105 have stage ok and 48,024 are flagged. `derived/flag_vs_stage_*.csv`.

## 6. Coverage

Monthly RU web_connectivity (API, complete, `derived/coverage_monthly.csv`, per ASN in `coverage_asn_by_month.csv`):

| Year | measurements | Note |
|---|---|---|
| 2022 | 36.9 M | 4.2 M in Jan, 2.0 M in Oct |
| 2023 | 32.4 M | 1.8 M (Jun) – 4.1 M (Aug) |
| 2024 | 39.5 M | 2.4–4.6 M per month |
| 2025 | 29.3 M | falls to 1.8 M in Dec |
| 2026 (to Sep) | 46.1 M | 1.3 M in Jan; **7.4 M in Mar**; 5.0–6.4 M Apr–Sep |

ASNs seen per month: 200–400 until Jan 2026, then 966 in Feb and 575–885 since. ASNs averaging ≥ 20 measurements per hour over a month: 25–62 until 2025, 16 in Jan 2026, 59–86 since March. Top-10 share 0.40–0.65. The largest contributors change: AS34665 holds 11–21 % of volume Aug–Dec 2023 and nothing in 2025; AS48558 leads Sep 2024–Feb 2025 and is nearly gone in 2026; AS39028 (ER-Telecom Ulyanovsk) goes from 33 measurements in 2024 to 4.0 M in 2026.

Coverage on the quiet days, set F, hours (of 240) with n ≥ 20 (`derived/coverage_quiet_days_per_asn.csv`, 467 ASNs):

| Unit | hours with n ≥ 20 | hourly volume median (p5–p95) | Verdict |
|---|---|---|---|
| all-RU | 240 | 3,760 (1,405–7,574) | usable |
| AS12389 Rostelecom | 230 | 432 (70–1,283) | usable |
| AS25513 МГТС | 209 | 226 (5–798) | usable |
| AS8402 Beeline (Corbina) | 176 | 119 (0–435) | usable |
| AS35807 SkyNet SPb | 163 | 100 (0–295) | usable |
| AS50716 Telecom.ru | 126 | 57 (0–732) | usable |
| AS8359 МТС | 114 | 6 (0–341) | usable |
| AS31200 Novotelecom | 113 | 34 (0–331) | usable |
| other 460 ASNs | < 100 each | median 0 | no coverage |

"Usable" = at least 100 quiet bins with n ≥ 20, the minimum for a 99th percentile. For the other ASNs a threshold can only be borrowed from their tier and n band (§4).

## 7. Predictions scored

| # | Result |
|---|---|
| P1 | Range right (61k–177k per day). Ordering wrong: 2022-06 exceeds 2025-02; 2026-06-10 exceeds 2026-03-11 |
| P2 | Right on nine days (max/min hour 1.8–4.9; no hour below 0.5 × baseline on the 6 days with API counts). Wrong on 2026-03-11: max/min 189 because of the OONI-wide gap |
| P3 | Right, and stronger: p1 of the volume ratio is 0 for every single ASN including Rostelecom |
| P4 | **Wrong.** ok is 0.87 on F, not ≥ 0.92; dns_fail 0.02; the largest classes are http_diff, control_fail, dns_fail and tls_alert, not timeouts. Cause: the anomaly-based input set (§3) |
| P5 | **Wrong** for the pre-registered share (all-RU p99 0.40); netfail p99 is 0.19 on F and 0.066 on the strict set |
| P6 | First half right (31 % unflagged; 92 % on F). Second half wrong: flagged measurements almost never have stage ok |
| P7 | Mostly right: 5 ASNs reach n ≥ 20 in half the hours. Wrong on 2026: volume tripled in Feb–Mar 2026 and has declined only ~22 % since |
| P8 | Annotation is a minority (right). Mobile share of annotated was 0.6–8 % before 2026 (predicted 10–40 %) |
| P9 | 2.5–21.7 % per day, five days inside 3–12 %; the flag is network-specific, not a VPN measure |
| P10 | Right: unsplit ≤ 2.3 % of https failures in 2022–Apr 2023, zero afterwards |

## 8. Consequences for T1–T7

1. Use stage-specific shares among control-ok measurements, with `control_fail` as its own series. T1 should expect `control_fail` to rise on 14 Jan 2025 (the helpers are foreign TLS endpoints).
2. Define the input set by stage (strict set), not by anomaly share. This changes plan step 4 and is a decision for you.
3. Per-ASN tests are feasible for seven ASNs at hourly bins. T3 (Dagestan/Ingushetia) and T7 (regional ER-Telecom ASNs) will most likely return "no coverage"; check `coverage_asn_by_month.csv` for the target ASNs before pulling.
4. Volume drop is an all-RU signal only, and needs a non-RU volume control (e.g. DE, US upload volume for the same hours) to exclude OONI-side gaps. T1 should check this for 14 Jan 2025 before reading the −75 % as an effect of the outage.
5. 2026 events (T2, T7, the 10 Sep items in T6) need 2026 quiet days as reference; the pooled thresholds are too low for them at the all-RU level.

## 9. Open

- Re-run the API pulls when the quota resets (D1, D2, D5), then `analyse.py`; replace the provisional tables.
- Check the ten days against the ntc.party catalogue. Decide whether 2023-04-19, 2024-04-10 and 2026-03-11 stay in the quiet set; they are in every table above.
- What happened to the OONI test helpers on 10 Apr 2024, 00–13 UTC.
- The 2026 rise in quiet-day HTTP timeouts.
- More 2025–26 quiet days for an era-specific threshold.

Files: `T0/pull_s3.sh`, `T0/pull_api.py`, `T0/extract_stages.py`, `T0/analyse.py`; `T0/raw/` (19 GB), `T0/raw_api/`, `T0/derived/` (per-measurement stage tables `stages_<day>.csv.gz`, `summary.txt`, and the CSVs cited above).

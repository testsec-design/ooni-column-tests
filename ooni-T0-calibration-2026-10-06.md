# OONI T0: calibrating the instrument on quiet days

6 Oct 2026. This is test T0 from `ooni-column-test-plan-2026-10-06.md`. Code and data are in `T0/`.

## Summary

T0 asks how OONI web_connectivity behaves in Russia on days when nothing is known to have happened, so that later tests (T1–T7) have thresholds for calling a change. The run is complete: the raw pull (19 GB) finished at 15:00 UTC, and the API pull, cut off by the rate limit on the first attempt, was completed on a second, sequential attempt at 17:30 UTC. One provisional element remains: inputs are selected from the quiet day itself (split-half), not from the baseline days, because the baseline days are not pulled raw (D1).

The main findings:

- **The pre-registered input set does not contain only reachable sites.** Selecting inputs by OONI's anomaly share lets through dead domains, broken certificates and sites that answer Russian clients differently, because OONI does not flag those. On a quiet day 13 % of measurements on these inputs fail. Plan step 4 was therefore amended during the run (§0.3): inputs are now selected by whether the connection actually succeeded, which brings the median hourly failure share from 0.048 to 0.011. All tables below use the amended set.
- **Thresholds for individual failure stages are tight.** For all of Russia, the 99th-percentile share of TLS timeouts per hour is 0.017 and of TCP failures 0.017, and of all network failures together 0.071. The 14 Jan 2025 signature (failure shares of 0.8–0.9 at the TLS stage) clears every stage threshold easily. An effect the size of 4 May 2026 (anomaly share around 0.03) sits at or below the all-Russia threshold and well below any per-ASN one.
- **The quiet-day baseline has risen in 2026**, mostly through HTTP timeouts. Events in 2026 need 2026 quiet days as their reference.
- **Volume drops are only readable for Russia as a whole, and only with a non-Russian control.** On 11 Mar 2026 Russian volume fell to about 1 % for eight hours because of a gap on OONI's side that hit the US, Germany and Brazil too. For a single ASN, volume drops to zero too often on quiet days to mean anything, even for Rostelecom.
- **OONI's `anomaly` flag misses a quarter to a half of HTTP timeouts and nearly all test-helper failures**, which confirms the 14 Jan finding on a sample of 80,619 measurements with the published flag. Its separate `failure` flag catches most of the HTTP timeouts, but a quarter of the test-helper failures and three quarters of the response-mismatch cases carry neither flag.
- **Only seven ASNs have enough coverage for per-ASN thresholds.** The regional networks that T3 and T7 need will most likely have none.
- **Three of the ten "quiet" days were not quiet for the instrument.** Two had test-helper failure episodes and one the OONI-wide submission gap.

## Terms used in this document

- **Stage:** where a measurement first failed: DNS, TCP, TLS or HTTP, or `ok`. Defined exactly in §0.1.
- **control_fail:** OONI's test helper (the comparison measurement from outside Russia) failed. Added during the run (deviation D3). The other stage shares are computed only over measurements whose control succeeded (**control-ok**).
- **netfail:** the share of control-ok measurements that failed at DNS, TCP, TLS or HTTP. It excludes `http_diff` (a response arrived but differed from the control).
- **Set F:** the "normally reachable" inputs, selected by raw stage as amended in §0.3 (with the provisional split-half substitute D1).
- **Anomaly-based set:** the pre-registered definition (anomaly share below 0.05), kept as a sensitivity row.
- **p99 threshold:** the 99th percentile of a quantity over quiet bins. A later test calls a change when a bin exceeds it.
- **Volume ratio:** an hour's measurement count divided by the mean count for the same hour on D−1, D+1 and D−7.
- **Tiers A–D:** ASNs grouped by daily measurement volume (§0.1).

## 0. Pre-registration

Written 6 Oct 2026 at 13:11 UTC, before any data was pulled. At that point I had seen the plan, the four context docs, one connectivity check against the aggregation API (RU web_connectivity on 1 Jun 2026: 184,618 measurements, 57,530 anomalies, 17,198 failures) and a listing of 5 keys in the S3 bucket. Nothing else.

### 0.1 Design decisions fixed in advance

**Quiet days.** Ten days: 2022-06-15 (Wed), 2022-11-16 (Wed), 2023-04-19 (Wed), 2023-09-16 (Sat), 2024-04-10 (Wed), 2024-09-18 (Wed), 2025-02-19 (Wed), 2025-09-21 (Sun), 2026-03-11 (Wed), 2026-06-10 (Wed). A day counts as quiet if it is more than 7 days from every event named in the plan or the context docs (12 Mar 2022, Nov 2024 Hetzner, 6–7 Dec 2024, 14 and 24 Jan 2025, 20 Mar and 30 Mar–2 Apr 2025, the June 2025 range blocks, 2–4 May 2026, 18 Aug 2026, 10 Sep 2026), and I know of no nationwide fixed-line incident on it. The ntc.party catalogue (`ntc-party-fixed-line-outages-catalogue-2026-09-23.md`) is not on this machine, so the days have **not** been checked against it. I deliberately did not use the OONI data itself to judge whether a day was quiet.

**Source.** Raw measurements come from the public S3 bucket `ooni-data-eu-fra`, under `raw/<YYYYMMDD>/<HH>/RU/webconnectivity/*.jsonl.gz`, because only the raw data contains `test_keys`. The bucket is organised by upload hour, so for quiet day D I pull all of upload day D plus upload hours 00–05 of D+1, and keep the measurements whose `measurement_start_time` falls on D (UTC). The anomaly and failure flags and the per-input counts for the baseline come from the OONI API (`api.ooni.io`), the only place the pipeline's `anomaly` flag exists.

**Unit (plan step 2).** A unit is `(probe_cc=RU, probe_asn)`. T0 has no event, so there is no split into affected and control networks. I report three kinds of unit: all of Russia; each ASN with enough coverage; and ASNs grouped into tiers by volume. The tiers are fixed here, using the median daily count of filtered measurements over the days on which the ASN appears: A ≥ 2,000, B 500–1,999, C 100–499, D < 100.

**Hygiene (plan step 3).**

- *Mobile:* drop measurements with `annotations.network_type = mobile`. Measurements with no annotation are kept and counted separately.
- *VPN taint:* OONI's own mismatch analysis uses the submission IP, which I do not expect to find in the public raw data. I use a proxy instead, per report (`report_id`). A report is flagged if it measured at least 3 canary inputs and at least half of them reached an HTTP response. The canaries are sites blocked on Russian networks throughout the period, in any scheme: `facebook.com`, `www.facebook.com`, `twitter.com`, `www.instagram.com`, `instagram.com`, `www.linkedin.com`, `www.bbc.com`, `meduza.io`, `www.svoboda.org`, `rutracker.org`. Reports with fewer than 3 canaries are "taint unknown". Flagged reports are excluded from the calibration statistics, and their share is reported.
- *Duplicates:* keep the last measurement per `(report_id, input)`.

**Inputs (plan step 4).** For quiet day D, the "normally reachable" set is chosen from D's baseline days (D−1, D+1 and D−7), not from D itself: inputs with at least 20 RU measurements and an anomaly share below 0.05, summed over those three days, from the aggregation API. Inputs are split into domestic (`.ru`, `.su`, `.рф`) and foreign by top-level domain, and into https and http. Splits by Russian hosting or by hosting ASN are not needed for calibration and are left to the tests that use them.

**Outcome (plan step 5).** Each measurement gets one stage from its raw `test_keys`: the first stage that failed, checked in this order:

1. `dns_fail`: `dns_experiment_failure` is set.
2. `tcp_fail`: TCP was attempted and no endpoint connected.
3. `tls_timeout`, `tls_reset`, `tls_alert`, `tls_other`: an https input where no TLS handshake succeeded.
4. `http_timeout`, `http_reset`, `http_other`: `http_experiment_failure` is set after the connection or handshake.
5. `http_diff`: a response arrived, but its status differs from the control's, or its body length, headers and title all differ.
6. `ok`.

`dns_inconsistent` (`dns_consistency = inconsistent`) is recorded as a separate flag rather than a stage, because a CDN can return a different answer from the control's and still work. If TLS and HTTP failures cannot be told apart (no `tls_handshakes` recorded), the stage is `tls_or_http_unsplit`. The control's status (`control_failure`, control HTTP failure) is recorded alongside.

**Window, margin and bins (plan step 6).** The timing margin for all tests is **±60 minutes** around the reported event window. Bins are 60 minutes (primary) and 15 minutes, on `measurement_start_time` in UTC. The baseline is the same clock hours on D−1, D+1 and D−7.

In T0, raw stages are pulled only for the quiet day itself. The baseline days enter only through the API, for input selection and hourly volume per ASN. As a result, T0 calibrates thresholds on two quantities: the **absolute** stage share per bin, and the **volume ratio**. A threshold on the *change* in stage share relative to the baseline would need raw pulls for 30 more days, so it is not calibrated here.

**Thresholds (plan step 7).** For each unit and bin size, the threshold is the 99th percentile over quiet bins of (i) the non-ok stage share and (ii) each individual stage share, and the 1st percentile of (iii) the volume ratio, since that signal is a drop. Thresholds are computed separately for bands of measurements per bin (20–49, 50–99, 100–199, ≥ 200). Bins with fewer than 20 measurements count as "no coverage". The number of measurements is reported everywhere.

**Verdicts (plan step 8).** T0 fills no cell of the mechanism table. Its verdict is per unit: *usable* if a threshold can be estimated (at least 100 quiet bins with at least 20 measurements each), otherwise *no coverage*.

**Data handling (plan step 9).** S3 downloads run with 8 parallel workers (the objects are independent) and API reads with 4 (the day-and-slice reads are independent). Concurrency cannot change the data. Raw files are kept under `T0/raw/` with a SHA-256 manifest.

### 0.2 Predictions

| # | Quantity | Prediction |
|---|---|---|
| P1 | All-RU web_connectivity volume on the quiet days | 60k–200k per day; lower in 2022–23 than in 2025; 2026-06-10 below 2026-03-11 |
| P2 | Hourly volume, all-RU | Follows a daily cycle, with a max/min hour ratio of 2–4. A quiet hour falls below 0.5 × baseline in fewer than 1 % of hours |
| P3 | Hourly volume, single ASN | Bursty, because it depends on which probes run. Outside the top ~5 ASNs the 1st-percentile volume ratio is about 0, so a volume drop cannot be read per ASN |
| P4 | Stage shares, normally-reachable inputs, all-RU | ok ≥ 0.92; non-ok 0.02–0.08; TLS and HTTP timeouts the largest failure class; `dns_fail` < 0.01; `tcp_fail` < 0.02 |
| P5 | 99th-percentile non-ok share per hour | All-RU ≤ 0.15; tier-A ASNs 0.15–0.35; small bins (20–49 measurements) can reach 1.0 by chance |
| P6 | Anomaly flag vs raw stage | Of measurements with a raw failure stage, more than 30 % carry `anomaly=false` (the 14 Jan plain-HTTP timeout class). Of `anomaly=true` measurements on normally-reachable inputs, most are `dns_inconsistent` with stage ok |
| P7 | Coverage by ASN | The top 10 ASNs hold more than 50 % of volume; at most 15 ASNs reach 20 normally-reachable measurements in at least half of the hours; monthly volume falls through 2026 |
| P8 | Mobile | `network_type` is present on a minority of measurements (the mobile app only); 10–40 % of annotated ones are mobile |
| P9 | VPN taint (canary proxy) | 3–12 % of measurements sit in flagged reports (OONI's global mismatch figure is about 7 %) |
| P10 | TLS/HTTP split | `tls_handshakes` present for https inputs on all ten days; the unsplit share is below 5 % |

### 0.3 Amendment to plan step 4 (6 Oct 2026, ~15:40 UTC, after the first run)

After the first run showed that the anomaly-based set is not a set of reachable inputs (§3), plan step 4 was changed by decision: an input is "normally reachable" on day D if, on the baseline days after the hygiene filters, it has at least 20 RU measurements and raw stage `ok` in at least 90 % of the measurements whose control succeeded. OONI's anomaly share is no longer used. The plan file carries the same wording. §0.1 and §0.2 are left as written; the predictions were made against the old definition and are scored against both in §7. Every table below was recomputed on the amended set; the anomaly-based set appears as a sensitivity row. The split-half fallback (D1) still applies, since the baseline days' raw data are not pulled.

---

## 1. What was run, and how it differs from the pre-registration

**Run on 6 Oct 2026, 13:40–17:35 UTC. Result: complete, with D1 provisional.** The raw pull finished at 15:00 UTC. The first API attempt (4 parallel workers) stopped after 31 responses when the per-IP quota ran out (HTTP 429, `x-ratelimit-remaining: 0`); a rewritten sequential `pull_api.py` (one request every 3 s, resumable) completed the remaining 104 responses between 15:17 and 17:30 UTC without a single 429. The quota showed about 4,000 units at the start and fell by 3–15 per request.

| # | Planned | What was done | Consequence |
|---|---|---|---|
| D1 | Select normally-reachable inputs from API per-input counts on D−1, D+1 and D−7 | The API returned none of these. *Provisional substitute:* split day D's reports into two halves by a hash of `report_id`. An input qualifies for one half if, in the other half, it has at least 10 measurements and stage `ok` in at least 90 % of control-ok ones. No measurement takes part in its own selection | Inputs are selected from the same day rather than from baseline days. For the anomaly-based rule, the pre-registered baseline-day selection, the split-half and a circular same-day selection give nearly the same thresholds (§3: netfail p99 0.188, 0.194, 0.172), so the bias is probably small; this cannot be checked for the stage rule without raw baseline days |
| D2 | Take the `anomaly` flag from the API's measurement list for every measurement | Delivered for a fixed sample: four half-hour slices per quiet day (02:00, 08:00, 14:00, 20:00 UTC), 80,619 measurements. The probe-side field `test_keys.blocking` agrees with the published flag on 99.6 % of them (313 flag-only cases, none proxy-only) | §5 is computed on the sample. The proxy is validated and can be used where the API list is not pulled |
| D3 | Stage order with no class for control failures | Added `control_fail` (the test-helper request failed) as its own class, checked before the others. The other stage shares are computed among control-ok measurements. This came from the data (§2) | The pre-registered non-ok share is still reported, as `nonok_prereg` |
| D4 | Anomaly-based input set (§0.1, step 4) | Replaced by the stage-based set (§0.3) after the first run showed the anomaly-based set is not reachable (§3) | The primary set was changed after seeing data. The old set is kept as a sensitivity row |
| D5 | Volume ratio on all 10 days | Done on the second attempt | None |
| D6 | Canary counts as clean if it "reached an HTTP response" | Implemented as raw stage `ok`, since a blockpage is also an HTTP response | Stricter, and the intended reading |

Not done: the quiet days were not checked against the ntc.party catalogue (not on this machine). The DNS-inconsistency and hosting-ASN splits were not computed. VPN taint by OONI's own method was not possible, since the submission IP is not in the public data.

## 2. Data and hygiene

The raw pull is 1,605 `jsonl.gz` files: 19 GB, 1,446,791 lines, none unparseable. Of these, 1,126,525 measurements started on the ten quiet days; the rest started on the following mornings. Manifests: `T0/manifest.sha256` (the manifest's own SHA-256 is `a1f77b603eb3fc28…`) and `T0/manifest_api.sha256` (135 API responses; its SHA-256 is `cfff7a07db30dd04…`). Concurrency was as stated in §0.

| Day | Raw n | No `network_type` | Mobile dropped | In tainted reports | Taint unknown | After hygiene | On normally-reachable inputs (set F, stage-based) |
|---|---|---|---|---|---|---|---|
| 2022-06-15 | 97,361 | 65 % | 220 | 8.4 % | 0.5 % | 89,004 | 59,417 |
| 2022-11-16 | 76,616 | 58 % | 2,536 | 15.6 % | 1.0 % | 62,559 | 33,269 |
| 2023-04-19 | 60,746 | 75 % | 88 | 6.6 % | 1.5 % | 56,681 | 22,937 |
| 2023-09-16 | 123,821 | 64 % | 949 | 21.7 % | 0.5 % | 96,212 | 57,916 |
| 2024-04-10 | 78,935 | 51 % | 1,620 | 7.9 % | 2.9 % | 71,211 | 31,084 |
| 2024-09-18 | 177,192 | 71 % | 2,083 | 5.9 % | 0.8 % | 164,817 | 98,018 |
| 2025-02-19 | 84,200 | 85 % | 646 | 8.0 % | 1.9 % | 76,904 | 35,736 |
| 2025-09-21 | 118,301 | 67 % | 706 | 2.5 % | 2.8 % | 114,532 | 62,104 |
| 2026-03-11 | 134,244 | 89 % | 3,540 | 16.2 % | 39.7 % | 109,507 | 40,173 |
| 2026-06-10 | 175,109 | 70 % | 11,522 | 18.1 % | 53.2 % | 133,960 | 39,408 |

**The mobile filter removes little.** Between 51 % and 89 % of measurements carry no `network_type`, so "drop mobile" only removes what the mobile app labels. Mobile is 0.6–8 % of annotated measurements until 2025, and 22–23 % in 2026.

**The canary flag does not isolate VPNs.** The canaries are blocked as expected (each reaches ok in 8–20 % of measurements). But flagged reports cluster in particular networks: AS34665 (100 % of 19,924 measurements), AS9009 (52 %), AS9123 Timeweb (46 %), AS12668 (43 %), AS12714 MegaFon (33 %) and AS51645 ER-Telecom Irkutsk (33 %), against 1.4 % on AS25513 and 2.7 % on AS50716. The flag picks up any vantage point where blocked sites work: a VPN, a hosting network, or an ISP segment without filtering. In 2026, 40–53 % of measurements sit in reports with fewer than 3 canaries, so the flag is mostly undefined there. Per-ASN figures: `derived/taint_per_asn.csv`.

**Duplicates and upload lag are negligible.** There are 193 duplicates per `(report_id, input)` in total. At most 222 of a day's measurements arrive in the next day's first six upload hours.

**Three of the ten days are not quiet for the instrument.** Two have episodes of control failures, and one has a gap in submissions.

- *Control failures.* The hourly `control_failure` share is at most 0.05 on eight days. On 2023-04-19 it is 0.03–0.24 (06–20 UTC). On **2024-04-10 it is 0.17–0.52 from 00 to 13 UTC**, across 46 ASNs, with the error `httpapi: all endpoints failed` (the test helpers were unreachable). 11,050 of those 13,547 measurements also show a probe-side TCP timeout at 60 s. Whether this was a problem in OONI's backend or in reaching the helpers from Russia is not established. Without the control class, this day alone would put the all-RU `tcp_fail` share at 18 %.
- *Submission gap on 2026-03-11, about 13:30–22:00 UTC.* Russian web_connectivity falls from about 10,000–12,000 measurements per hour to 55–165 (at 15, 16, 17 and 21 UTC), partly recovers at 18–20 UTC, and is back at 7,500 by 22 UTC. The same hours are nearly empty in the bucket for the US (125 MB → 0 MB per upload hour), Germany and Brazil, so the cause is on OONI's side, not in Russia. Seen from Russian data alone, it looks like an eight-hour drop to about 1 % of normal volume.

## 3. Stage shares on quiet days

Pooled over the ten days, all-RU, set F (stage-based; 883–1,792 inputs per day; n = 480,062): ok 0.957, control_fail 0.025, http_timeout 0.0038, dns_fail 0.0037, http_diff 0.0028, tcp_fail 0.0027, tls_timeout 0.0022, tls_alert 0.0008, tls_reset 0.0008. Per-day figures: `derived/stage_shares_per_day.csv`.

**Selecting inputs by anomaly share does not give a set of reachable inputs.** Some inputs pass the test of "anomaly share below 0.05" because OONI does not count their failures as anomalies: domains that are dead (NXDOMAIN for both probe and control), sites with broken certificates, and sites that answer Russian clients with a different status. As a result, 13 % of the measurements on the anomaly-based set are non-ok on a quiet day. This is why step 4 was amended (§0.3). The stage rule keeps about as many inputs (883–1,792 per day, against 965–1,915 for the anomaly rule computed as pre-registered from the API counts on D−1, D+1 and D−7), and the two rules overlap heavily: 444k of the 480k measurements in F are also in the split-half anomaly-based set.

| All-RU, 60-min bins (240 bins) | n | netfail median | netfail p99 | http_diff p99 |
|---|---|---|---|---|
| **Set F: stage-based (primary, §0.3)** | 480,062 | 0.011 | 0.071 | 0.018 |
| Anomaly-based set, as pre-registered (API counts on the baseline days) | 569,672 | 0.044 | 0.188 | 0.076 |
| Anomaly-based, split-half on day D | 506,174 | 0.048 | 0.194 | 0.077 |
| Anomaly-based split-half and stage-based | 444,289 | 0.010 | 0.066 | 0.010 |
| Anomaly-based, circular same-day selection | 523,374 | 0.048 | 0.172 | 0.072 |
| No input restriction | 975,387 | 0.317 | 0.506 | 0.065 |

**The baseline changes over time.** On set F, the median hourly all-RU netfail is 0.005–0.009 on the six days up to September 2024 (except 0.024 on 2024-04-10), 0.012 in September 2025, and then **0.032 on 2026-03-11 and 0.053 on 2026-06-10**. The 2026 rise comes from HTTP timeouts (1.1–1.4 % of set F, against 0.1–0.4 % before), TCP and DNS failures, and TLS failures (median hourly tls_any 0.011–0.020 in 2026, at most 0.003 before). The highest value on 2026-03-11 (0.162) falls inside that day's submission gap, when an hour holds only a few dozen measurements. Per-hour figures: `derived/allru_hourly_per_day.csv`.

**Domestic inputs are not cleaner than foreign ones on quiet days.** Netfail among control-ok measurements on set F: https-foreign 0.016, https-domestic 0.014, http-foreign 0.016, http-domestic 0.012.

## 4. Thresholds (provisional only through D1: same-day input selection)

Each threshold is the 99th percentile over quiet bins with at least 20 measurements. A later test calls a change when a bin exceeds it. The full table, by band of measurements per bin, for both bin sizes and every stage family, is in `derived/thresholds_stage_share.csv`.

| Unit, 60-min bins, set F | Quiet bins | Median n | control_fail p99 | netfail p50 / p99 | tls_any p99 | tls_timeout p99 | tcp_fail p99 | dns_fail p99 | nonok_prereg p99 |
|---|---|---|---|---|---|---|---|---|---|
| All-RU | 240 | 1,870 | 0.50 | 0.011 / 0.071 | 0.033 | 0.017 | 0.017 | 0.037 | 0.38 |
| Tier A, per-ASN bins, n ≥ 200 | 310 | 359 | 0.20 | 0.005 / 0.15 | 0.027 | 0.015 | 0.023 | 0.12 | 0.30 |
| Tier A, 100–199 | 170 | 144 | 0.56 | 0.006 / 0.11 | 0.078 | 0.031 | 0.028 | 0.041 | 0.37 |
| Tier B, n ≥ 200 | 133 | 323 | 0.01 | 0.004 / 0.082 | 0.031 | 0.022 | 0.065 | 0.014 | 0.089 |
| Tier B, 100–199 | 245 | 129 | 0.22 | 0.000 / 0.12 | 0.036 | 0.019 | 0.026 | 0.026 | 0.22 |
| Tier B, 50–99 | 876 | 66 | 1.0 | 0.000 / 0.14 | 0.039 | 0.036 | 0.048 | 0.033 | 1.0 |
| Tier B, 20–49 | 679 | 35 | 1.0 | 0.000 / 0.29 | 0.24 | 0.086 | 0.049 | 0.18 | 1.0 |
| Tier C, 100–199 | 162 | 129 | 0.45 | 0.000 / 0.072 | 0.047 | 0.027 | 0.024 | 0.025 | 0.30 |
| Tier C, 50–99 | 814 | 66 | 1.0 | 0.000 / 0.13 | 0.066 | 0.040 | 0.032 | 0.035 | 1.0 |
| Tier C, 20–49 | 854 | 35 | 1.0 | 0.000 / 0.41 | 0.16 | 0.093 | 0.13 | 0.076 | 1.0 |
| Tier D, n ≥ 20 | 420 | 47 | 0.84 | 0.000 / 0.43 | 0.24 | 0.075 | 0.10 | 0.12 | 0.52 |
| AS12389 Rostelecom | 230 | 206 | 0.72 | 0.006 / 0.13 | 0.037 | 0.028 | 0.027 | 0.074 | 0.38 |
| AS25513 МГТС | 209 | 127 | 0.41 | 0.004 / 0.20 | 0.14 | 0.037 | 0.034 | 0.12 | 0.41 |
| AS8402 Beeline (Corbina) | 176 | 76 | 1.0 | 0.000 / 0.16 | 0.083 | 0.070 | 0.048 | 0.029 | 1.0 |
| AS35807 SkyNet | 163 | 68 | 1.0 | 0.000 / 0.081 | 0.038 | 0.026 | 0.025 | 0.023 | 0.37 |
| AS50716 Telecom.ru | 125 | 127 | 0.005 | 0.000 / 0.032 | 0.008 | 0.008 | 0.017 | 0.009 | 0.25 |
| AS8359 МТС | 112 | 78 | 0.90 | 0.004 / 0.17 | 0.15 | 0.10 | 0.043 | 0.042 | 0.92 |
| AS31200 Novotelecom | 109 | 67 | 1.0 | 0.000 / 0.024 | 0.007 | 0.006 | 0.022 | 0.010 | 1.0 |

For comparison, on the anomaly-based set the same per-ASN 60-minute bins with at least 100 measurements give netfail p99 of 0.28 (tier A), 0.20 (B) and 0.16 (C), two to three times the values above.

How to read the table:

- **Large events stand out; small ones don't.** The 14 Jan 2025 signature (a failure share of 0.8–0.9 at the TLS stage) clears every stage-specific threshold by a wide margin, in any unit with at least 50 measurements per bin. An effect the size of 4 May 2026 (anomaly share around 0.03) sits at or below the all-RU netfail threshold of 0.07 and well below every per-ASN one.
- **Stage-specific thresholds are much tighter than the aggregate.** For all of Russia, `tls_timeout` p99 is 0.017 and `tcp_fail` p99 is 0.017, against 0.38 for the pre-registered non-ok share, which still counts control failures.
- **A p99 of 1.0 means one probe session can fill a bin** with a single failure class. `control_fail` does this in every tier, and so does the pre-registered non-ok share, because it contains control failures.
- **Per-ASN medians of 0 mean most quiet hours have no network failure at all** on these inputs. The 99th percentile is then set by a handful of hours, which is why the per-ASN tls_any and dns_fail thresholds vary so much between networks of similar size.
- **These thresholds pool 2022–2026.** Given §3, a 2026 event should be judged against 2026 quiet bins. Ten days cannot give a 99th percentile per period, since each day has only 24 hourly bins.

**Volume ratio.** Each hour's count divided by the mean of the same hour on D−1, D+1 and D−7, from API counts with no hygiene filter, over all 10 days (`derived/thresholds_volume_ratio.csv`):

| Unit | Quiet bins | p1 | p5 | p50 | Share of quiet bins < 0.5 | < 0.25 |
|---|---|---|---|---|---|---|
| All-RU | 240 | 0.06 | 0.60 | 1.02 | 3.8 % | 3.3 % |
| All-RU without 2026-03-11 | 216 | 0.59 | 0.75 | 1.03 | 0 | 0 |
| AS12389 | 240 | 0.00 | 0.12 | 1.01 | 12 % | 6.7 % |
| AS25513 | 240 | 0.00 | 0.06 | 0.93 | 22 % | 9.6 % |
| Tier A / B / C / D pooled | 827 / 2,841 / 4,245 / 2,682 | 0 | 0 | 0.96 / 0.99 / 0.08 / 0 | 25 / 33 / 57 / 80 % | 18 / 29 / 54 / 77 % |

For all of Russia, a drop below about 0.59 of the baseline lies beyond the 1 % level on the nine undisturbed days, so the −75 % of 14 Jan 2025 is far outside their normal variation. But 2026-03-11 (§2) shows a drop to about 1 % that OONI itself caused, and with that day included the all-RU 1st percentile is 0.06: the ninth hour of 240 is the gap. **An all-RU volume drop is therefore evidence about Russia only if other countries' volume holds steady at the same time.** Plan step 2 rules out a non-Russian control, but for volume one is needed. Per ASN, a volume drop is not a usable signal: even Rostelecom falls to zero in more than 1 % of quiet hours.

## 5. Probe-side verdict versus raw stage

This compares the raw failure stage with OONI's published flags on the sampled slices (four half-hours per quiet day; D2). The API carries two flags: `anomaly` (the one the 14 Jan analysis used) and `failure`. The probe-side field `test_keys.blocking` reproduces `anomaly` on 99.6 % of the sample, so the proxy can stand in for it elsewhere.

| | Hygiene set, all inputs (sample n = 80,619) | Set F (sample n = 39,443) |
|---|---|---|
| Raw stage not ok (including control_fail) | 31,134 | 1,725 |
| … of which `anomaly = false` | 9,482 (**30 %**) | 1,319 (**76 %**; 36 % once control failures are excluded) |
| … of which neither `anomaly` nor `failure` | 4,260 (14 %) | 517 (30 %; 16 % excluding control failures) |
| `anomaly = true` | 21,867 | 441 |
| … of which raw stage ok | 215 (1 %) | 35 (8 %) |

The share of failures with `anomaly = false`, by stage, over all inputs: control_fail 98 %, http_diff 75 %, http_other 58 %, dns_fail 52 %, tls_alert 51 %, **http_timeout 45 %**, tls_other 35 %, http_reset 13 %, tls_reset 5 %, tls_timeout 4 %, tcp_fail 1 %. On set F: dns_fail 42 %, tcp_fail 30 %, http_timeout 25 %, tls_timeout 21 %, tls_reset 5 %. The `anomaly` flag tracks TLS timeouts, TLS resets and TCP failures closely and misses a quarter to a half of HTTP timeouts (the 14 Jan plain-HTTP class) and nearly all control failures. The `failure` flag picks up most of what `anomaly` misses: of 2,741 HTTP timeouts, 1,142 carry `failure` only and 100 carry neither. What carries neither flag is concentrated in two classes: response mismatches (2,361 of 3,160 http_diff) and control failures (633 of 2,328). `dns_inconsistent` is set on 7,737 sampled measurements, of which 2,291 have stage ok and 4,203 carry `anomaly`. Tables: `derived/flag_vs_stage_*.csv`.

## 6. Coverage

Monthly Russian web_connectivity volume, from the API (complete; `derived/coverage_monthly.csv`, and per ASN in `coverage_asn_by_month.csv`):

| Year | Measurements | Note |
|---|---|---|
| 2022 | 36.9 M | 4.2 M in Jan, 2.0 M in Oct |
| 2023 | 32.4 M | 1.8 M (Jun) to 4.1 M (Aug) |
| 2024 | 39.5 M | 2.4–4.6 M per month |
| 2025 | 29.3 M | Falls to 1.8 M in Dec |
| 2026 (to Sep) | 46.1 M | 1.3 M in Jan; **7.4 M in Mar**; 5.0–6.4 M Apr–Sep |

The number of ASNs seen per month is 200–400 until January 2026, then 966 in February and 575–885 since. The number averaging at least 20 measurements per hour over a month is 25–62 until 2025, 16 in January 2026, and 59–86 since March. The top 10 ASNs hold 40–65 % of volume. The largest contributors change over time: AS34665 holds 11–21 % of volume in Aug–Dec 2023 and nothing in 2025; AS48558 leads from September 2024 to February 2025 and has nearly disappeared in 2026; AS39028 (ER-Telecom Ulyanovsk) grows from 33 measurements in 2024 to 4.0 M in 2026.

Coverage on the quiet days, set F, counting hours (out of 240) with at least 20 measurements (`derived/coverage_quiet_days_per_asn.csv`, 464 ASNs):

| Unit | Hours with n ≥ 20 | Hourly volume, median (p5–p95) | Verdict |
|---|---|---|---|
| All-RU | 240 | 3,760 (1,405–7,574) | usable |
| AS12389 Rostelecom | 230 | 432 (70–1,283) | usable |
| AS25513 МГТС | 209 | 226 (5–798) | usable |
| AS8402 Beeline (Corbina) | 176 | 119 (0–435) | usable |
| AS35807 SkyNet SPb | 163 | 100 (0–295) | usable |
| AS50716 Telecom.ru | 125 | 57 (0–732) | usable |
| AS8359 МТС | 112 | 6 (0–341) | usable |
| AS31200 Novotelecom | 109 | 34 (0–331) | usable |
| Other 457 ASNs | fewer than 100 each | median 0 | no coverage |

"Usable" means at least 100 quiet bins with at least 20 measurements, the minimum for a 99th percentile. The other ASNs can only borrow a threshold from their tier and band (§4).

## 7. Predictions scored

| # | Result |
|---|---|
| P1 | Range right (61k–177k per day). Ordering wrong: 2022-06 exceeds 2025-02, and 2026-06-10 exceeds 2026-03-11 |
| P2 | Right on nine days (max/min hour ratio 1.8–4.9; no hour below 0.5 × baseline). Wrong on 2026-03-11, where the ratio is 189 and nine hours fall below 0.5 because of the OONI-wide gap |
| P3 | Right, and more so than predicted: the 1st-percentile volume ratio is 0 for every single ASN, including Rostelecom |
| P4 | **Wrong** on the set it was made for (anomaly-based): ok 0.87, not ≥ 0.92; the largest failure classes are http_diff, control_fail, dns_fail and tls_alert. On the amended set, ok is 0.957 and the largest class after control_fail is http_timeout, closer to the prediction, but that set was chosen after seeing the data |
| P5 | **Wrong** for the pre-registered share (all-RU p99 is 0.38, driven by control failures). netfail p99 is 0.071 all-RU and 0.08–0.15 for tier-A ASN bins with at least 100 measurements; small bins do reach 1.0 as predicted |
| P6 | First half right: 30 % of failures have `anomaly = false` (36 % on set F, excluding control failures). Second half wrong: `anomaly = true` measurements almost never have stage ok (1 %; 8 % on set F) |
| P7 | Mostly right: 5 ASNs reach 20 measurements in half the hours. Wrong for 2026: volume tripled in Feb–Mar 2026 and has fallen only about 22 % since |
| P8 | Right that annotation is a minority. The mobile share of annotated measurements was 0.6–8 % before 2026, not 10–40 % |
| P9 | 2.5–21.7 % per day, with five days inside 3–12 %. The flag is specific to networks, not a measure of VPN use |
| P10 | Right: unsplit failures are at most 2.3 % of https failures in 2022 to April 2023, and zero afterwards |

## 8. Consequences for T1–T7

1. **Use stage-specific shares among control-ok measurements, with `control_fail` as its own series.** T1 should expect `control_fail` to rise on 14 Jan 2025, because the test helpers are foreign TLS endpoints.
2. **Plan step 4 is amended (§0.3): select inputs by stage.** For T1–T7 this means either pulling the baseline days raw (about 5 GB per day in 2026, less earlier) or using the split-half fallback and labelling it provisional.
3. **Per-ASN tests are feasible for seven ASNs at hourly bins.** T3 (Dagestan/Ingushetia) and T7 (regional ER-Telecom ASNs) will most likely return "no coverage". Check `coverage_asn_by_month.csv` for the target ASNs before pulling.
4. **A volume drop is a signal only for Russia as a whole, and it needs a non-Russian volume control** (e.g. German or US upload volume for the same hours) to rule out gaps on OONI's side. T1 should check this for 14 Jan 2025 before reading the −75 % as an effect of the outage.
5. **2026 events (T2, T7 and the 10 Sep items in T6) need 2026 quiet days as their reference.** The pooled thresholds are too low for them at the all-RU level.

## 9. Open

- Pull the baseline days raw (30 days, roughly 50 GB) to replace the split-half input selection (D1) with the plan's definition.
- Check the ten days against the ntc.party catalogue. Decide whether 2023-04-19, 2024-04-10 and 2026-03-11 stay in the quiet set; they are included in every table above.
- Find out what happened to the OONI test helpers on 10 Apr 2024, 00–13 UTC.
- Explain the 2026 rise in quiet-day HTTP timeouts.
- Add more 2025–26 quiet days, for a threshold specific to the current period.

Files: `T0/pull_s3.sh`, `T0/pull_api.py`, `T0/extract_stages.py`, `T0/analyse.py`; `T0/raw/` (19 GB), `T0/raw_api/`, and `T0/derived/` (per-measurement stage tables `stages_<day>.csv.gz`, `summary.txt`, and the CSVs cited above).

# Prompt for Claude Code: T5b — is the 2026 quiet-day baseline rise the 16 KB cap?

Work in `~/shutdown-measurement/ooni-column-tests/`. Put everything for this task in a new folder `T5b/` and write the result to `T5b/ooni-T5b-2026-baseline-cap-<date>.md`. Do not edit any existing document, and do not write anywhere under `T0/`, `T1/`, `T2/`, `T4/`, `T5/` or `AS39028/`. T2 is being run in another session in the same folder.

## Read first

- `ooni-column-test-plan-2026-10-06.md`
- `ooni-T0-calibration-2026-10-06.md`: §0.1 stage logic, §3 "the baseline changes over time", §8
- `AS39028/as39028-characterisation-2026-10-06.md`: §3 and §5
- `ooni-T5-16kb-cap-2026-10-06.md`: §0.2 feasibility, §3, §6, and §8 item 4, which is the question here
- `ooni-T4-range-blocks-2026-10-06.md`: §0.2, the hosting classification and inference rules
- `setup-counts/setup_counts.csv` and `setup-counts/README.md`

## Question

T0 found that the quiet-day hourly netfail share on set F rose from at most 0.012 (up to September 2025) to 0.032–0.061 on the 2026 quiet days. The rise is mostly HTTP timeouts. The AS39028 analysis showed that this one deployment does not explain the rise. T5 showed that in June 2025 the 16 KB cap appears in OONI as a size-dependent post-handshake stall: the TLS handshake succeeds, headers arrive, and the HTTP exchange then times out, only on pages whose control body exceeds 16 KiB. Forum reports (ntc.party 17013 #886, 4625 #1526) describe the cap as widespread on wired networks by 2026.

Does that signature account for the 2026 rise? If so, on which hosting networks and on which probe ASNs?

## Decisions already made (Hannah, 6 Oct 2026). Apply them; do not revisit them.

1. **Verdicts are per probe ASN only.** Report all-Russia figures as description, with no verdict attached.
2. **Count setups for every per-ASN cell.** Report distinct setups and reports, both overall and among the failures. A setup is `software_name`, `software_version`, `test_version`, plus the annotations `platform`, `engine_version` and `origin` where present. State that setups are a lower bound on devices and reports an upper bound.
3. **No percentile thresholds.** Use contrasts with interval estimates instead. Remove AS39028 from all-Russia aggregates and report it as its own unit.

## Data

Do not pull any new OONI data. Use only what is already on disk:

- **2026 quiet days:** 2026-03-11 and 2026-06-10 (in `T0/raw/`), and 2026-09-23 (in `AS39028/raw/`). On 2026-03-11, exclude 13:30–22:00 UTC, which is OONI's submission gap.
- **Reference days before the cap:** 2024-09-18 and 2025-02-19 (in `T0/raw/`).
- **2025-09-21 is not clean.** The ntc.party check found a reported restriction on AWS address ranges that day (4625 #1118–#1119: ClientHello stalls, only allowlisted SNIs pass). Use 2025-09-21 only as a secondary comparison, with AWS-hosted inputs reported separately.

Read the raw files in place; do not copy them. You may download the CAIDA RouteViews prefix-to-AS files (IPv4 and IPv6) nearest each day into `T5b/reference/`, with SHA-256 hashes.

Parallelize extraction across days and files wherever that cannot change the result. State the concurrency setting and how to raise it.

## Method

1. **Stages.** Re-extract stages with the stage function from `T4/extract_stages.py`, unchanged (check this by diff). It records `http_code`, `ctl_body_len` and the control's resolved addresses, which T0's stage tables lack. Apply hygiene as in T4 §0.2. Analyse https inputs only.

2. **Input selection.**
   - **Do not use T0's split-half set F as the primary set.** It selects inputs that reached `ok` on the same day. An input that is capped all day stalls in both halves, so it drops out of set F. A standing cap is therefore partly invisible in T0's 2026 baseline by construction.
   - **Primary set:** select inputs on the reference days (2024-09-18 and 2025-02-19). Keep inputs with at least 20 measurements and stage `ok` in at least 90 % of control-ok measurements. Report how many 2026 inputs this set lacks.
   - **Sensitivity rows:** (a) no reachability filter, excluding only the T0 canary sites; (b) T0's set F. For (b), report how many inputs set F excluded on each 2026 day, and how many of those are larger than 16 KiB and hosted on a network that shows a size step.

3. **Size.** An input's size is the median `control.http_request.body_length` over the day's control-ok measurements. Use the bins < 8, 8–16, 16–32, 32–64 and ≥ 64 KiB.

4. **Hosting.** Map each control address to its origin ASN by longest-prefix match. Group inputs as Cloudflare, Hetzner, DigitalOcean, OVH, and every other foreign origin ASN with at least 10 inputs on its own. Pool the remaining foreign inputs as "other foreign", and keep domestic inputs separate. Do not restrict the analysis to the four June 2025 providers; the question is where the size step is now.

5. **Primary quantity: the size contrast.** For each day and hosting group, compute the stall share of inputs above 16 KiB minus the stall share of inputs at or below 16 KiB. A stall is `http_timeout`, `http_reset` or `http_other` after a recorded successful handshake, among control-ok measurements. Also report the share of stalls with headers received (`http_code > 0`). For intervals, use a cluster bootstrap over inputs, as in T4, and report the number of setups alongside.

6. **Decomposition.** For each 2026 day, take all-Russia without AS39028 and compute the excess HTTP-timeout share over 2025-02-19. Estimate how much of that excess the size step accounts for. As the counterfactual, replace the stall share of every group's inputs above 16 KiB by that group's stall share for inputs at or below 16 KiB on the same day. Report what remains of T0's netfail rise after the counterfactual. Report this as description, not as a verdict.

7. **Per probe ASN.** Compute the same size contrast for every probe ASN with at least 200 control-ok measurements above 16 KiB on a day. Report setup counts for each cell.

8. **Secondary.** AS39028's blocked inputs shifted from TLS timeouts to TLS resets between June and September 2026. Report TLS timeout and reset shares by day, probe ASN and hosting group, without a verdict.

## Pre-registration

Before you read any stage output from this extraction, write the following into the result doc, with a timestamp:
- Your predictions.
- The per-ASN verdict rule. Propose its thresholds and justify them; do not use percentiles.
- The decision rule for "the size step accounts for most, part, or none of the 2026 rise".
- What you had seen before writing.

Record every later deviation in a table: planned, done, consequence.

## Write-up

Follow the structure of the T4 and T5 docs: summary, terms, pre-registration, deviations, data and hygiene, results, predictions scored, proposed text for the M5 cell and for T0 §3, and open questions.

State claim strength as conjunctions and search scope, never as universal negatives. Use statistical terms only where they are exactly correct. Keep raw-derived tables in `T5b/derived/` with a manifest.

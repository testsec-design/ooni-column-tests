# OONI volume for Russia and for a full replica (1 Oct 2026)

Measured by Hannah from her Mac. Follow-up to `data-inventory-2026-10-01.md` (item O2) and the supervisors' question about an OONI replica in Kassel.

## Counts (OONI aggregation API, probe_cc=RU, 2022-01-01 → 2026-10-01)

~250 million measurements in total: web_connectivity 184.2 M (~106,000/day), dnscheck 36.1 M, stunreachability 12.8 M, all other tests together 17.4 M. web_connectivity: 43.9 M anomaly, 3.66 M confirmed (blockpage match), 9.1 M failure, 127.5 M ok. dnscheck, echcheck and wireguard report every measurement as failure and none as ok — likely an aggregation artefact for tests without anomaly logic; check before using.

## Bytes (S3 bucket `ooni-data-eu-fra`, prefix `raw/20260601/`, one day)

- All countries: 57,246 objects, 63.5 GB compressed.
- Russia: 4.49 GB compressed = 2.23 GB `.jsonl.gz` + 2.27 GB postcans (`.tar.gz`). The two formats hold the same measurements, so only the jsonl part counts: ~2.2 GB/day for RU, ~15 KB compressed per measurement.

## Extrapolation (assumes June 2026 volume is typical — not yet checked against 2022 and 2024 days)

- RU jsonl since 2022: ~2.2 GB × ~1,735 days ≈ **~3.9 TB compressed**.
- Full replica, all countries, jsonl only, since 2022: if the jsonl/postcan split is similar globally, ~32 GB/day ≈ **~55 TB compressed**; ~110 TB including postcans. Earlier years extra.

## Consequences

- Thesis: no full raw RU pull. Use the aggregation API for the whole period (per day × ASN × test, and per domain for web_connectivity), plus raw jsonl only around events and for affected ASNs (~15 GB compressed per week of all-RU data, less when filtered).
- Replica: tens of TB, fits Kassel's 1.3 PB S3 cold storage; a raw mirror is `aws s3 sync --no-sign-request` plus a scheduled incremental sync; making it queryable means running OONI's pipeline (ClickHouse). Suggested split: the Kassel PhD student who spoke to OONI leads the replica; Hannah contributes the RU-slice sync and her converter.
- Licence: CC BY-NC-SA 4.0.

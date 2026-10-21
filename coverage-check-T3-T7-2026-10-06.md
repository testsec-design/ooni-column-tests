# Coverage check for T3 and T7 — 6 Oct 2026

Prerequisite from the plan (T3: "first check coverage"; T0 §8 item 3: check `coverage_asn_by_month.csv` for the target ASNs before pulling).

**Data.** `T0/raw_api/monthly/*.json` (OONI API, RU web_connectivity, per ASN per month, 2022-01 to 2026-09, 1,989 ASNs). `T0/derived/coverage_asn_by_month.csv` holds only the top 200 ASNs, so the lookup was done against the raw JSON. ASNs were identified by name in `reference/asn-holders.json` (743 RU holders) and `disco/data/asNames.json` (54k global names). The monthly criterion is the one T0 uses in `coverage_monthly.csv`: at least 14,400 measurements in the month, i.e. 20 per hour on average. The quiet-day columns come from `T0/derived/coverage_quiet_days_per_asn.csv`. Table: `coverage-check-T3-T7-2026-10-06.csv`.

## T3 — Dagestan/Ingushetia, Dec 2024: no coverage

Every Dagestan- or Ingushetia-named ASN has zero measurements in December 2024, and zero from October 2024 to February 2025. Four of them (Dagestantelekom AS39434, former Ingushelectrosvyaz AS44412, DAG-AS AS41796, DAGINCOM AS196657) never appear in the Russian OONI data in any of the 57 months. The ones that do appear (DAGSV AS43574, DAGNET AS15428, Kaspiytelekom AS57333, SKANETDAG AS60936, and smaller ones) have a few hundred to a few thousand measurements in their best month and nothing near the drill.

The only candidate with volume in December 2024 is MegaFon Kavkaz AS31163 (mobile), with 229 measurements for the month, about 0.3 per hour. It also covers the whole North Caucasus, not Dagestan alone. Rostelecom's Dagestan branch sits inside the nationwide AS12389 and cannot be separated, because OONI has no region field.

Verdict: T3 cannot be run per ASN on OONI. The M3 cell has to come from another instrument (Atlas probes in the region, if any existed in December 2024, or the sensor/telescope columns), or T3 is recorded as "no coverage" in the table.

Limit of the check: an ASN whose registry name does not mention the region (e.g. a holding-level ASN of a national ISP) would be missed. That is the OONI region problem itself, not a gap in the lookup.

## T7 — ER-Telecom Volga ASNs, Sep 2026: coverage exists for some ASNs, contrary to the T0 expectation

| ASN | ER-Telecom unit | Sep 2026 n | per hour | Aug 2026 n | Quiet hours ≥ 20 (of 240) |
|---|---|---|---|---|---|
| 39028 | Ulyanovsk | 778,361 | 1,081 | 707,310 | 48 |
| 51035 | Ufa (Volga or Urals macro-region?) | 104,887 | 146 | 77,551 | 42 |
| 12768 | Perm, holding-level ASN | 46,923 | 65 | 67,423 | 41 |
| 42682 | Nizhny Novgorod | 37,885 | 53 | 40,187 | 8 |
| 39435 | Volgograd (South macro-region?) | 26,658 | 37 | 23,027 | 21 |
| 42116 | Naberezhnye Chelny | 22,562 | 31 | 33,339 | — |
| 42683 | Orenburg | 15,519 | 22 | 20,369 | — |
| 41754 | Penza | 4,944 | 7 | 976 | 6 |
| 50543 | Saratov | 4,931 | 7 | 935 | — |
| 41668 | Kazan | 2,822 | 4 | 3,110 | 30 |
| 34533 | Samara/Togliatti | 2,131 | 3 | 18,515 | 8 |
| 41786 | Yoshkar-Ola | 2,127 | 3 | 0 | 17 |
| 34590 | Izhevsk (IZHEVSK-AS) | 1,500 | 2 | 39,788 | 0 |
| 57026 | Cheboksary? (CHEB-AS, holder unknown) | 242 | 0.3 | — | 26 |

Seven ER-Telecom ASNs clear the 20-per-hour monthly average in September 2026. Ulyanovsk AS39028 alone averages over 1,000 per hour and is the largest Russian ASN in OONI since June 2026 (12–14 % of all-RU volume). The T0 quiet-day table marks all of them "no coverage" only because they have volume on at most 3 of the 10 quiet days: AS39028 had 33 measurements in all of 2024 and started growing in July 2025 (corrected 6 Oct 2026 after `AS39028/as39028-characterisation-2026-10-06.md`; the first version of this sentence said "did not exist before 2026"). With 2026 quiet days as the reference (T0 §8 item 5), AS39028 is a usable hourly unit and AS51035, AS12768, AS42682 and AS39435 are plausible at 2–3 h bins.

Two things to settle before pulling:

1. **Which ASNs are "Поволжье".** The forum report (4625 #1658) names Dom.ru Поволжье without a city. ER-Telecom's Volga macro-region is taken here as Samara/Togliatti, Saratov, Penza, Ulyanovsk, Kazan, Naberezhnye Chelny, Nizhny Novgorod, Yoshkar-Ola, Cheboksary and Orenburg; Ufa, Izhevsk, Volgograd and the Perm holding ASN are borderline. Read the thread for the city, then pick the ASN. If it is Samara, Saratov, Penza or Kazan, OONI has no coverage for T7 either.
2. **What AS39028's 2026 volume is.** A jump from 33 measurements in 2024 to 4.5 M in 2026 is not organic uptake. The T0 taint table shows 0 % of its reports in the flagged set and 38 % in reports with canaries, so the volume is not the VPN-probe class, but whether it is one automated prober or a real residential population matters for reading a whitelist signal. Check the number of distinct probes (report IDs or probe_cc/asn/software combinations) per day on a 2026 quiet day before using it.

The monthly average also hides within-month variation; the hourly pull for 10 Sep 2026 is still needed to confirm that the event hours have ≥ 20 measurements.

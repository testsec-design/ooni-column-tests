Run test T6 (DNS intervention, mechanism M7) from ooni-column-test-plan-2026-10-06.md.

Read first: the plan, including amendments A1–A5 at the end (they apply to T6);
ooni-T0-calibration-2026-10-06.md; ooni-T1-jan14-2025-2026-10-06.md (§0.1 input rule);
ooni-T2-mmts9-2026-08-18-2026-10-07.md (its August 2026 raw pull may be reusable);
T5b/ooni-T5b-2026-baseline-cap-2026-10-07.md (setup definition; extract.py handles
web_connectivity 0.5.x); AS39028/as39028-characterisation-2026-10-06.md (summary);
ntc-party-check-test-days-2026-10-06.md; context/mechanism-instrument-table-fixed-line-2026-09-29.md
(row M7); context/dns-udp53-substitution-finding-2026-09-22.md (the Atlas finding; its data
folders are ~/shutdown-measurement/dnscheck/{all,live,monthly,onsets}); and
context/ntc-party-dns-russia-catalogue-2026-09-22.md (the forum's dated DNS events). Code and
data go in T6/.
Do not modify other tests' folders.

## Why the plan's T6 needs refining first

The plan says: compare OONI DNS failures per ASN with the Atlas finding, then the 10 Sep 2026
".ru NXDOMAIN for 3 minutes" report. Three things make that too thin, and you should design
around them:

1. The Atlas finding measures something different. Atlas built-ins send UDP/53 queries to
   a-root; about 5 % of Russian probes get an answer from someone else, flat since 2022,
   mostly household routers (Yandex SafeDNS, Quad9 redirection). OONI web_connectivity
   resolves through the probe's system resolver. The two can only be compared on a shared
   quantity, see Part A.
2. The forum catalogue has a far better event: from 20 Aug 2026 a multi-ISP wave in which
   UDP/53 queries to public resolvers (1.1.1.1, 1.0.0.1, 8.8.8.8, 8.8.4.4, even NSDI and
   MSK-IX resolvers) are intercepted after the ТСПУ hop, answered from MSK-IX / RIPN
   infrastructure; TCP/53 and DoH still reach Google; registry-blocked domains come back
   NXDOMAIN, empty, or with a forged authoritative flag, while other domains resolve correctly;
   Yandex UDP is not intercepted; mobile largely unaffected. In parallel, DoH/DoT to
   dns.google, cloudflare-dns.com, AdGuard, Quad9 and AliDNS blocked by SNI on several ISPs.
   Earlier: scattered UDP/53 interception reports in Feb–Mar 2026, and a separate 3 Jul 2026
   IP:port block of 8.8.8.8 on TCP 53/853/443 with UDP intact. Read the catalogue's
   "Mid-Aug" and "20–28 Aug" paragraphs and thread 23007 references before designing Part B.
3. The 10 Sep report is one user with split DNS, three minutes at midnight Moscow time.
   Treat it as a coverage check (Part C), not a main test.

## Hard constraints

1. Pre-register before pulling any event-period data: write §0 of the result doc with a UTC
   timestamp, stating what you had seen. Deviations go in a table, never silently.
2. A1–A4: verdicts per probe ASN only; all-RU and pooled groups are description. Every cell
   states setups and reports (overall and among the failures). No percentile thresholds:
   judge by contrasts (after vs before, affected group vs control) with intervals that name
   their resampling unit (resample reports or days, not measurements, and say why).
   AS39028 is its own unit and excluded from all-RU.
3. A5: 2026 events against 2026 reference days. Choose before/after days by the rules used in
   T0 (more than 7 days from listed events; here also avoid 17–19 Aug, the T2 power failure,
   and 3 Jul) and check them against the fixed-line and DNS catalogues. State the choice.
4. Prefer the S3 bucket (ooni-data-eu-fra, --no-sign-request). Reuse raw files already on disk
   (T0, T2, AS39028) where the days match. The API may be used only serially with pauses
   (T0/pull_api.py's client), and only where S3 cannot answer.
5. Parallelize S3 downloads and state the setting. Keep raw files with a SHA-256 manifest; no
   pull-and-delete. Estimate disk use from S3 listings first; stop and ask me above 60 GB.
6. Identify resolver operators (Google, Cloudflare, Yandex, Quad9, NSDI, MSK-IX, RIPN, the
   ISPs' own) by ASN from registry data (RIPEstat, the repo's asn-holders.json), never from
   memory, and record how each was identified.
7. Enumerate the fields actually present before relying on any (in particular `resolver_ip`,
   `resolver_asn`, `queries[].engine`, `queries[].resolver_address`, `queries[].answers`,
   `dns_consistency`, and in dnscheck the per-lookup transport and failure fields), for both
   web_connectivity 0.4.x and 0.5.x. What `resolver_ip` means in OONI (the address the
   probe's resolver is seen to query from, found by a lookup) must be stated from OONI's own
   specification, cited, before it is used.

## Part A — the standing condition (description, no verdict)

Shared quantity: is the probe's DNS answered by the operator it appears to be configured for?
- OONI, 2026-09-23 (raw already in AS39028/raw): per probe ASN, the distribution of resolver
  operators by `resolver_asn`, and the share of measurements resolved through a router-level
  substitute of the kinds the Atlas finding names (e.g. Yandex SafeDNS), if identifiable.
- Atlas: the 20 Sep 2026 all-probe snapshot (`~/shutdown-measurement/dnscheck/all`, flagged
  lists `dnscheck/dns-flagged.txt` and `dns-cases.txt`):
  per ASN, the share of probes whose a-root queries are answered by a non-root.
- Compare by ASN, report where both instruments have coverage, and say plainly how much
  agreement one should expect given that they measure different paths. A null here is not
  a failure of either instrument.

## Part B — the August 2026 wave (the M7 event)

Pre-register predictions for each instrument path before pulling:
- **web_connectivity, probes whose system resolver is a public resolver** (resolver_asn of
  Google or Cloudflare before the wave): after 20 Aug, on wired ISPs named in the catalogue,
  (i) `resolver_asn` shifts towards MSK-IX / RIPN / NSDI infrastructure, because the
  resolver-identification lookup is itself intercepted; (ii) registry-blocked inputs return
  NXDOMAIN, empty or inconsistent answers more often, while normally reachable inputs do not
  change. Controls: probes using their ISP's own resolver, probes using Yandex, and mobile
  ASNs (reported not affected).
- **dnscheck** (pull it from S3; check first which resolvers and transports the Russian
  measurements actually test): UDP/53 to public resolvers still answers but from a different
  responder or with altered timing; DoH/DoT lookups fail at TLS (SNI block) on the ISPs and
  dates the catalogue names; TCP/53 unchanged.
Primary per-ASN contrast for each prediction: after minus before, with an interval, against the
same contrast in the control groups. Report the onset day per ASN where the data show one,
next to the forum's dates. Report the 3 Jul 8.8.8.8 IP:port block separately if your days
cover it; it is a different mechanism (a block, not a substitution).

## Part C — 10 Sep 2026, ".ru NXDOMAIN for three minutes"

Coverage only: how many measurements, in which ASNs, with which resolvers, in 2026-09-09
20:50–21:15 UTC (midnight MSK ± margin). If there is coverage, show the DNS outcomes for .ru
inputs minute by minute against the same minutes on the reference days. Otherwise record
"no coverage" with n.

## Output

- ooni-T6-dns-<date>.md: findings first; terms defined once; §0 pre-registration; deviations;
  data and hygiene; Parts A–C with tables (n, setups, reports, intervals); predictions scored;
  verdict per ASN for the M7 × OONI cell (observed / null / ambiguous / no coverage); what OONI
  can and cannot see about DNS intervention and why; open questions.
- Proposed wording for the M7 cell of the OONI column. Do not edit the mechanism table.
- Plain, readable prose: short sentences, findings before method detail.

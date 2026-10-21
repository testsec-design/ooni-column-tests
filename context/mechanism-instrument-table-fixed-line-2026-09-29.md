# Mechanism × instrument table — fixed-line disruptions in Russia (draft, 29 Sept 2026)

Purpose: answer the "black box" concern by writing down, before looking at new data, what each instrument should report under each candidate mechanism, and where two mechanisms would produce the same row. Cells marked **obs.** are calibrated on a labelled event already analysed; cells marked *pred.* are predictions not yet tested; **?** means the test is defined but not run. Sources: `memo1-atlas-ioda-2026-09-25.md`, `memo2-ham-radio-2026-09-25.md`, `sensor-fusion-design-2026-09-23.md`, `dns-udp53-substitution-finding-2026-09-22.md`, `ntc-party-fixed-line-outages-catalogue-2026-09-23.md`, `atlas-mgts-whitelist-prediction-2026-09-24.md`.

Scope: fixed-line only. Mobile shutdowns are out of scope for now because the anchoring events with instrument coverage are all fixed-line.

## 1. Candidate mechanisms

| # | Mechanism | Where it acts | Anchor events (labelled from outside the instruments) |
|---|---|---|---|
| M1 | Route withdrawal | BGP; prefixes leave the global table | None clean in RU 2022–26. Closest: 12 Mar 2022 LINX disconnection of Rostelecom/MegaFon — a transit change with partial withdrawal, not a cut |
| M2 | Transit, exchange or power failure, routes held | Physical/transit layer; unintentional | 18 Aug 2026 ММТС-9 power failure (Amnezia); 2 May 2026 Moscow (forum: M9 power on both feeds, MSK-IX outage, Dom.ru DHCP) |
| M2b | Operator access-line cut (single ISP, deliberate) | Access network; DHCP/BNG switched off | Forum lead only: Nizhny Novgorod, МТС/РТК ШПД "DHCP off with drone alerts" (24403 #9, disputed #10) |
| M3 | Border filter, destination-based, 2024 style | National border; foreign destinations unreachable, ICMP echo out of country blocked | 6–7 Dec 2024 Dagestan/Ingushetia drill (Access Now, IODA, forum 13598) |
| M4 | Whitelist (allowlist), 2026 style | TSPU at the ISP; new connections to non-allowlisted destinations refused, established sessions survive, UDP largely cut (forum/Habr) | 4 May 2026 МГТС GPON Moscow (forum 24403 #23 + Atlas); 10 Sep 2026 Dom.ru Поволжье (forum 4625 #1658, disputed #1660) |
| M5 | Throttling / 16 kB cap | TSPU; connectivity present, transfers to particular ranges cut after ~16 kB | Cloudflare's own confirmation of the cap; forum 16 kB scans (17013 #886, 4625 #1526) |
| M6 | DPI failing closed on TLS | TSPU fault; HTTPS dead after ClientHello, ICMP/UDP pass, minutes, nationwide | 14 Jan 2025 (Mintsifry acknowledgement; forum 14571 #26, #68, #141) |
| M7 | DNS intervention | Resolver path; substitution or NXDOMAIN | No event-level anchor. Background: ~5 % of RU probes see UDP/53 substitution, flat since Jan 2022, mostly household; one report of `.ru` NXDOMAIN for 3 min on 10 Sep 2026 |
| M8 | Destination-range block (hoster/CDN) | TSPU; specific foreign IP ranges | Hetzner Nov 2024; Cloudflare tests Mar–Apr 2025; Cloudflare/OVH/Hetzner/DO Jun 2025 |

M8 is a blocking episode rather than an outage, but it produces partial-reachability rows in the same instruments and is the main look-alike for M4 and M5, so it stays in the table.

## 2. Predicted and observed response per instrument

Instruments: **A-sess** = Atlas controller session log (msm 7000: SSH-in-TLS tunnel to RIPE Dublin, persistent flow). **A-built** = Atlas built-ins through the labelling rule (a-root/k-root ICMP, HTTP/TLS to RIPE hosts, own resolver, root DNS checks). **A-443** = the proposed standing measurement (`atlas_443.py`: TLS to controller, to a non-allowlisted foreign host, to yandex.ru). **I-BGP** = IODA routing. **I-ping** = IODA `ping-slash24` at region level. **Ham** = Kassel archive, within-station upload retention (UDP flow to one foreign collector). **OONI** = submission absence and composition of reachable destinations.

| Mech. | A-sess | A-built | A-443 | I-BGP | I-ping | Ham | OONI |
|---|---|---|---|---|---|---|---|
| M1 route withdrawal | *pred.* sessions drop, recovery when routes return | *pred.* `line-cut`/`upstream-cut`: every target fails | *pred.* all three fail | *pred.* withdrawn — defining signal | *pred.* drop | *pred.* uploads stop, RF continues | *pred.* absence |
| M2 transit/power, routes held | **obs.** multi-ASN simultaneous loss, quick line recovery (2 May); 2 of 38 probe-outages with partial-reachability signature (18 Aug) | **obs.** 18 Aug: one lost upstream, one lost MSK-IX k-root + resolver; rest session-only or silent | *pred.* all fail for the interval, then all recover | **obs.** held (IODA `routes_withdrawn` = no on both) | **?** 18 Aug expected null (too few /24s) — not checked | **obs.** null 18 Aug (n≈30 station-bins, low power); flat 2 May | *pred.* absence for the interval |
| M2b operator access cut | *pred.* one ISP's probes drop; no reconnection until restored | *pred.* `silent` (no buffered results) | *pred.* all fail | *pred.* held | *pred.* that ISP's /24s stop replying | *pred.* uploads stop for that ISP's subscribers; region-level only | *pred.* absence for that AS |
| M3 border filter 2024 | **obs. null** (Dagestan): established tunnels survived 26 h | **?** *pred.* foreign targets fail, resolver OK — labelling rule not yet run on Dec 2024 | *pred.* controller and foreign host fail, yandex OK | **obs.** flat | **obs.** −18.7 % region level, ~25 h (Ingushetia harder) | **obs. null**: uploads continued through the drill, ingested in real time | *pred.* foreign-destination failures; not checked |
| M4 whitelist 2026 | **obs.** blocked recovery after a controller restart (МГТС 4 May: median 6.3 h vs 1.8 min, perfect rank separation); otherwise *pred.* null — established sessions survive | **obs. null** (`selective` did not fire): a-root, k-root, HTTP, TLS to RIPE all reachable during the whitelist | *pred.* controller and foreign host fail, yandex OK — the direct signature | *pred.* held | **?** *pred.* null (ICMP passed on 4 May) — not checked | **?** *pred.* drop if UDP is cut as reported — 4 May not yet run with region denominators | *pred.* allowlist share rises; non-allowlisted domestic fails — the control separating M4 from M3 |
| M5 throttling / 16 kB | *pred.* null (keepalives are small) | *pred.* `degraded` on HTTP to RIPE if the range is affected; ICMP fine | *pred.* handshakes succeed, bulk transfer stalls — needs a size-aware probe | *pred.* held | *pred.* null | *pred.* null | *pred.* completed measurements with slow/failed large fetches |
| M6 DPI fail-closed | **obs. null** (14 Jan 2025: 2 probes out, upload lag unremarkable) | **?** *pred.* `selective`-like: ICMP OK, HTTP/TLS fail — the natural first test of that label, not yet run | *pred.* controller and foreign fail; yandex may also fail (forum: RU sites recovered first) | *pred.* held | **?** *pred.* null (ICMP passed) — not checked | *pred.* null (UDP passed) | *pred.* burst of TLS failures, minutes |
| M7 DNS intervention | *pred.* null | **obs.** substitution/NXDOMAIN visible per probe; no event-level step ever seen | *pred.* null (targets by IP) | *pred.* held | *pred.* null | *pred.* null unless the collector is resolved by name | *pred.* DNS-consistency failures |
| M8 destination-range block | *pred.* null unless RIPE ranges are listed | *pred.* null (RIPE hosts not in the blocked ranges) | *pred.* fails only if the foreign host sits in the blocked range | *pred.* held | *pred.* null | **?** depends on where the collector sits — question 1 for Kassel | *pred.* web-connectivity failures for listed domains — OONI's natural strength |

## 3. Which rows collide (identifiability)

Two mechanisms are separable only if some instrument gives different answers. Reading down the table:

M1 against everything else is clean: IODA BGP is the discriminator and no other row withdraws routes.

M2 against M4 was the 2 May confusion. Both drop many Moscow probes at once; the separation is in A-built (M2 fails every target for the interval and recovers; M4 leaves a-root and RIPE HTTP/TLS reachable) and in recovery shape (M2 recovers as fast as German probes; M4 recovers by ASN, hours later). This pair is the worked example that the table method resolves.

M3 against M4 is the pair that matters most and is not yet settled. A-sess is null for both (established sessions survive both). The predicted discriminators are I-ping (M3 blocks ICMP out of the country, observed; M4 does not, observed on 4 May via a-root ping) and Ham (M3 let the UDP flow through, observed; M4 is predicted to cut it, untested). Both halves need the 4 May checks in column I-ping and Ham before the row can be called calibrated.

M4 against M6 collide on every instrument except by scope and duration: nationwide and minutes (M6) against per-ISP and hours (M4). The one instrument-level difference is whether domestic non-allowlisted HTTPS works; on 14 Jan the forum says Russian sites recovered first rather than stayed up. Running the labelling rule on 14 Jan 2025 is the cheapest next test in the whole table, and if `selective` fires there and not on 4 May, the two rows separate.

M5 against M8 collide on partial reachability. The discriminator is transfer size: M8 fails the handshake, M5 passes it and stalls the transfer. Neither Atlas instrument as currently defined is size-aware.

M2b has no instrument calibration at all; it is a forum lead with a single disputed report.

## 4. What the table shows about the instruments

Atlas in 2026 delivers mainly one observable, reachability of a persistent tunnel to Dublin, which is why its row for the two filtering mechanisms (M3, M4) is null except when a controller restart forces reconnection. The built-ins add reachability of a handful of foreign targets that the 2026 whitelist apparently passes. A-443 is the column designed to fill the M4 cell directly, and it is empty because it is prospective; whether to run it, and under whose account, is the standing question from memo 1.

IODA region-level ping is the only instrument with an observed positive for M3. IODA BGP is the only one that separates M1. Ham is the only one with an observed null for M3 that also carries a measured denominator, and its M4 cell is the one prediction that would make it a whitelist detector.

OONI's column is entirely predicted; nothing has been run against it yet.

## 5. Questions for the next meeting

1. Which of the distinctions in §3 matter for the resilience question? If M3 versus M4 is the one that matters, the two unchecked cells on 4 May (I-ping, Ham) come first; if the fault class matters (M2, M6), the 14 Jan labelling run comes first.
2. Is the mechanism list complete for fixed-line as they see it? In particular whether M2b belongs as a class or as a variant of M4, and whether there is a mobile-network-side analogue worth listing for later.
3. Is a standing A-443 measurement worth its credits, given that it is the only instrument in the table predicted to see M4 without a coincidence?
4. Where does the ham collector sit (Kassel question 1)? Its answer fills the M8 cell and decides the M3 reading.

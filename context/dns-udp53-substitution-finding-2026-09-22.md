# UDP/53 substitution on Russian Atlas probes: a flat ~5 % background since 2022, not a 2026 mechanism — 22 Sept 2026

Data: RIPE Atlas built-ins 10309 (hostname.bind CH TXT to a.root-servers.net, UDP), 10009/10109 (SOA "." UDP/TCP), pulled with `dns_interception_check.py` into `dnscheck-live/` (40 RU + 40 DE, 20 Sept 2026), `dnscheck-all/` (all 572 connected RU, 20 Sept), `dnscheck-onsets/` (28 flagged probes, daily Jan–Sept 2026), `dnscheck-monthly/` (all connected RU, one day every 30 days, Jan 2022–Aug 2026). Companion to `dns-interception-check-brief.md` and `ripe-atlas-ru-disconnection-notes.md` (failure point 1).

## Result in one line
Whatever answers or drops UDP/53 queries to a-root from ~5 % of Russian probes has done so at that rate since at least January 2022, and is mostly identifiable household DNS redirection. It cannot account for the 2026 reconnection tails (6–16 % of RU probes, absent in 2025).

## Catalogue (verified from the API)
hostname.bind IPv4: 10301 k, 10304 f, 10305 i, 10306 m, 10308 l, 10309 a, 10310 b, 10311 c, 10312 d, 10313 e, 10314 g, 10315 h, 10316 j. SOA UDP 100xx, SOA TCP 101xx, id.server 104xx, version.bind 102xx, version.server 105xx, same suffixes; IPv6 11xxx. 30001 = random names via probe resolver, 30002 = popular domains. SOA built-ins every 1800 s, hostname.bind every 240 s.

## Prevalence (every 30 days, all connected RU probes)
Probes with non-NOERROR (or non-consensus name) share ≥ 50 % on the sampled day, over probes reporting: 10/228 (4.4 %) on 15 Jan 2022 … 25/481 (5.2 %) on 22 Aug 2026; range 3.7–7.2 % over 57 samples; no step at any 2026 controller event or whitelist date. 105 of 531 probes had an onset at some point while the count in state stayed 10–25, so most recovered: churn, not accumulation.

## What the substitutes are (hostname.bind answers received by < 3 probes)
- Yandex SafeDNS: `safedns-prod-safedns-mcluster-NN.{klg,sas,vla}.yp-c.yandex.net` and `*.yp-c.yandex.net` on 19195, 34048 (partly 10234, 14723, 4232). Consumer-router family-filter feature that redirects all port 53.
- Quad9: `res7NN.ams.rrdns.pch.net`, `res7NN.{ams,qhel1,qsin6,fra}` on 54383, 55797, 1003804. Router/host forcing DNS to 9.9.9.9.
- ISP resolvers: `msk-e3-dns02/03.ti.ru` (25003), `ns2.telekonika.ru` (11479). Operator interception or router redirect to DHCP upstream; indistinguishable here.
- Local boxes: `asgard` (3842), `squid` (53477), `ns1` (19008), `ns3` (10184).
- Resolver pool: `ns-node-1..13` (earlier `NS1-A/NS1-B/NS2-A/NS2-B`) on 11072, AS56330 — the one that still looks like operator infrastructure.
- Nameless failures (NOTIMP on ~9 probes, REFUSED, SERVFAIL, NXDOMAIN, UDP-only timeouts) sit in the same flat share.
- Threshold artefacts: `rootns-*` (older a-root naming), `nnn1-dfw8`, `nnn1-lcy4`, `nnn1-frmrs-3`, `nnn1-defra-6` are real instances seen by < 3 probes; 1000963 (AS13335) "96 % wrong_name" is a Cloudflare-hosted probe reaching a Frankfurt instance nobody else reaches, not a case.

## One-day detail, 20 Sept 2026
- 539/572 connected RU probes reported. All consensus answers name a-root instances outside Russia (ams5, sesto-1, lon8, usnyc, lcy*); when a-root answers, it is a-root.
- 35 probes flagged: 7 partial packet loss; ~18 UDP answered by a non-root (name or rcode) with TCP normal; 5 UDP dropped/TCP fine; ~7 both transports dead to 198.41.0.4 (whitelist-shaped, not interception).
- DE control same day: 0/37 UDP-only substitution; 1012117 REFUSED on both transports (host interceptor), 60404 TCP dead/UDP fine (firewall). Keep as the non-censor look-alikes. DE checked on one day only.
- Onsets of the 28 flagged (daily, 2026): 14 pre-January, 12 on twelve distinct dates; no clustering. 11496 (AS20764, on 5 Apr, phased REFUSED/SERVFAIL/timeout mixture) and 1000346 (AS51092, on 30 Aug, 100 % REFUSED) remain individually unexplained; two onsets a year is the churn the flat line implies.

## Consequences
- Drop this as a candidate for the reconnection problem; it did not change in 2026.
- Keep it in the classifier: "DNS answered" vs "DNS answered by the server asked". RU ≈ 5 % vs DE 0/37 is a real population difference, attributable mostly to consumer router features common in Russia, and a confound for any resolver-based measurement from RU probes.
- The bbs #657 claim concerns public resolvers (8.8.8.8 etc.), which root-targeted built-ins cannot test; that remains untested here.
- Method note for the write-up: name legitimacy by consensus (≥ 3 probes) is a stated threshold that misfires on rare instances; SOA UDP/TCP pairing needs a 900 s window.

# ntc.party check of the OONI test days (6 Oct 2026)

This checks every day used as a quiet day, baseline day or before/after day in T0, T1, T4, T5 and the AS39028 analysis against ntc.party, and screens candidate 2026 quiet days (plan amendment A5).

## Sources and search scope

- **The two project catalogues.** `ntc-party-fixed-line-outages-post-index.csv` holds 449 posts in 36 enumerated threads; `ntc-party-dns-russia-post-index.csv` holds 817 posts in 33 threads. Both index posts dated from 22 Sep 2024 up to their compilation dates (22 and 23 Sep 2026). For each test day D, I listed every indexed post dated D−1 to D+2, because posts usually report an event on the same day or the day after.
- **A forum-wide keyword search.** Using ntc.party's own search API from the browser pane, I searched the same D−1 to D+2 window for сбой, не работает, белые and блокировка. This covered the 2025–26 quiet days, the two T1 baseline days nearest the event, and three 2026 candidate days. Discourse search returns up to 50 matching posts per query, ranked; a day with no match means no post containing those four words in that window, not that nothing happened.
- **Posts read in full.** Where a flagged post bore on the day, I read it through the forum's post API: 4625 #1116–#1119, 12845 #558, 14571 #172–#234 (posts dated 15 Jan 2025), 14603 #1, 17013 #795 and #1035, 19553 #9 and #31.

## Limits on what was checked

- **2022–2024 quiet days.** The six T0 quiet days from 2022-06-15 to 2024-09-18 fall before both catalogues begin. They were not checked.
- **2025-02-19.** The forum's search returns no post at all for common words between about 27 Jan and 12 Mar 2025, and both catalogues have the same hole (no indexed post between 27 Jan and 12 Mar). This is a gap in the forum record. The day cannot be checked this way, which is different from a day the forum describes as quiet.
- **2026-09-23.** The catalogues were compiled on 22–23 Sep 2026, so their coverage stops on this day. The keyword search was not run for it.

## Findings per day

| Day | Role | What the forum has in D−1 … D+2 | Reading |
|---|---|---|---|
| 2025-02-19 | T0 quiet | Nothing; the forum record is empty for the whole period (see above) | Not checkable |
| **2025-09-21** | T0 quiet | 4625 #1118 (21 Sep, 16:17 UTC): a server on AWS addresses stalls after the ClientHello; the poster reports "something like whitelists for AWS subnets", with Amazon's own services working. #1119, from another account: "only SNI gosuslugi.ru and www.vk.com pass". 19553 #36 (20 Sep) discusses the same AWS allowlist. 726 #7228 and 19624 #5 (20–21 Sep): timeouts at the RETN–hosting junction, attributed to transit, not blocking. 4625 #1116 (21 Sep): apkmirror stalls after the first 64 KB on some ISPs. 19553 #9/#31 (19–20 Sep): a Dom.ru Rostov whitelist claim, rebutted as a local fault | **Not quiet for AWS-hosted inputs**, by two first-hand reports. There was also a transit problem on RETN-routed paths. The day can stay in T0 only if AWS-hosted and RETN-transited inputs are reported separately |
| 2026-03-11 | T0 quiet | Discussion of the 16 KB block as a standing condition (22516, 22707, 726 #9430). 17013 #795 is a WARP-vantage observation, not an ISP report. 22740 #2 mentions a "Siberian block" in passing. The Feb–Apr 2026 VPS-drop thread (22222) is ongoing | No episode reported; the cap appears as a background condition |
| 2026-06-10 | T0 quiet | 17013 #1035 (9 Jun): one Fastly IP stops answering TCP. 25077 #1/#3 (11 Jun): pypi.org and openpgpkey.archlinux.org drop at hop 3, "second day". 22506 #104 (9 Jun): a new wave of Telegram ClientHello blocking since 5 Jun | Reports about **Fastly-hosted destinations on 9–11 Jun**; report Fastly-hosted inputs separately |
| 2026-09-23 | AS39028 quiet | Catalogues end here. DNS index 23007 #188/#192 (19–20 Sep): Dom.ru St Petersburg sends no reply on UDP/53 to Google and Cloudflare over IPv4 | Not checkable for the day itself; a DNS condition on Dom.ru reported days before |
| 2025-01-07 | T1 baseline (D−7) | 11985 #50 (6 Jan): Skynet St Petersburg, about 19:00 MSK for 1.5 h, i.e. 16:00–17:30 UTC on 6 Jan, outside T1's window. 14351 (6–7 Jan): Cloudflare DoH failing on МТС/МГТС since about 3 Jan | Clean for T1's 13:00–16:00 UTC window. The DoH issue concerns DoH, which the OONI probe does not use by default |
| 2025-01-13 | T1 baseline (D−1) | 12845 #558: a Hetzner-block user report (МТС/МГТС, triggered when torrenting over a Hetzner VPN). 14555 (13 Jan): DoH.Pub down, and #4 says down outside Russia too. 14511 (11–12 Jan): МТС DNS issues | Clean for the window |
| **2025-01-15** | T1 baseline (D+1) | 14571 #226 (10:50 UTC): "second day after yesterday my internet keeps dropping", with the ISP's autoresponder citing "elimination of the consequences of the accident" (ISP not named). 14571 #172/#227/#228: DNS trouble on 14–15 Jan. 14603 #1: Cloudflare DoH failing after the outage; #2 says it works on МТС Урал. 726 #4212 and 13251 #662: Discord blocking changed on 15 Jan | **One first-hand report of residual instability on an unnamed ISP the day after.** T1 found one dns_fail exceedance at 14:15 on 15 Jan, and residual МГТС timeouts after recovery. Neither changes T1's verdict, but 15 Jan is not a clean baseline day |
| 2024-10-30, 10-31, **11-01** | T4 E1 baseline | 12534 #1/#8/#11 (1 Nov): МГТС and others in Moscow lose all connectivity 18:00–18:28 MSK (15:00–15:28 UTC). A Ростелеком Moscow user reports 10–15-minute total outages on the evening of 31 Oct and the morning of 1 Nov | Short Moscow outages on two of the three days used to **select** inputs; the 90 % rule over three days should absorb them. Worth one sensitivity row in T4 |
| 2024-11-03 … **11-05** | T4 E1 before | DNS index 12732 (from 5 Nov): Cloudflare ECH stops working on МТС, Ростелеком and Yota; DoH to Cloudflare, Google and others fails. 12740 (5 Nov): Quad9 resets | ECH and DoH only; web_connectivity 0.4 uses neither. No effect on the stage families T4 used |
| 2024-11-08 … 11-10 | T4 E1 after | Hetzner thread (12845 #120, 10 Nov: Ростелеком SSH on non-default ports). DNS index 12732 #340 (9 Nov): Google DNS unreachable for an hour on one ISP, UDP answers from 8.8.8.8 substituted. 13017: ТТК Volgograd blocks Google DoH from 8 Nov | Within the event; the DNS items could touch the "other" family, which T4 found flat |
| 2025-06-02 … 06-04 | T4/T5 E2 baseline | No indexed post between 21 May and 9 Jun in either catalogue | No episode in the catalogues; keyword search not run |
| 2025-06-06 … 06-08 | T4/T5 E2 before | Same | Same |
| 2025-06-10 … 06-12 | T4/T5 E2 after | The event itself (4625 #733, #748, #761; 12845 #633; 16697 Cloudflare DoH unstable from 9 Jun). 16818 (13–14 Jun) argues over which part was Cloudflare's own incident on 12 Jun | Cloudflare had a service incident of its own on 12 Jun 2025, inside the after window. T5's daily series is lower on 12 Jun than on 11 Jun, so it does not drive the result, but dropping 12 Jun evening (UTC) is a cheap sensitivity row |

## Candidate 2026 quiet days

The rule follows T0: more than 7 days from every event in the plan or the context docs. To that I add: no catalogue post dated D−3 … D+3, no Atlas event of the cross-reference within ±2 days (`atlas-ioda-crossref-2026-09-25.md`), and outside the 15 Jun–15 Jul 2026 exercise window (17013 #1299) and the Russian New Year holidays.

| Candidate | Catalogues | Keyword search, D−1 … D+2 | Other | Assessment |
|---|---|---|---|---|
| **Wed 2026-07-29** | 27 Jul, DNS index 4625 #1634 (D−2): "for some days" TCP to the addresses behind `*.storage.googleapis.com` is blocked. Next post 2 Aug | 4884 #16 (30 Jul): upload.wikimedia.org unreachable on wired Ростелеком Moscow Oblast, reachable on mobile МТС; the poster cites Wikimedia's status page, so the cause may be on Wikimedia's side. 17013 #1305: one site's daily 15-minute "dynamic block". The rest is cap and circumvention discussion | Atlas event 21 Jul, −11.5 % (8 days before) | **Fails the ±3-day rule** (D−2). Best of the candidates: usable with Google-storage-hosted and Wikimedia-hosted inputs reported separately |
| Thu 2026-08-06 | 5 Aug (DNS 13566 #55–57: periodic drops to dns.google) | 25528 (5–6 Aug): RKN blocked many VPN server IPs on 4 Aug 2026 | 12 days before 18 Aug | **Fails the ±3-day catalogue rule** (a DNS post on D−1). Borderline: the reports are a DNS-resolver issue and a blocking step two days earlier aimed at VPN endpoints, neither about general fixed-line reachability. Your call |
| Wed 2026-05-13 | 7 May and 15 May (DNS) | 17013 #965 (14 May): "in the last 2 days all CF subnets were put under 16 KB" (a Yota user, i.e. mobile). 18333 #299 (12 May): WhatsApp working without a VPN on МГТС since 11 May. 13566 #23 (13 May): Google search shaped on a wired ISP in Sverdlovsk | 15 May IODA cluster (rated a probable artefact); Victory Day mobile shutdowns 5–9 May | **Not quiet for M5**: a reported widening of the Cloudflare cap on 12–13 May. Unsuitable as a reference for T5b; usable for other tests only with Cloudflare-hosted inputs reported separately |
| Wed 2026-05-27 | 22 and 29 May | Not run | Atlas event 28 May 14:00, −14.4 % (the largest in the catalogue) | Excluded |
| Any day after 23 Sep 2026 | Not covered | Not run | — | Needs a fresh forum pass first |

No 2026 weekday checked here passes the ±3-day catalogue rule as written. The ntc.party record for 2026 is dense with destination-specific blocking reports (single providers, single services), so a 2026 "quiet day" in practice means "no reported outage or whitelist episode, with the destinations named in nearby reports split out". With the three existing 2026 quiet days (11 Mar, 10 Jun, 23 Sep), adding 29 Jul gives four, and five if 6 Aug is accepted. Reaching more needs one of two things. One is a rule that says which kinds of nearby post disqualify a day: outages and whitelist episodes do, while reports about a single destination only require that destination to be split out. The other is a forum pass covering late September and October 2026.

## Consequences

1. **2025-09-21 is not a quiet day for AWS-hosted destinations**, which matters to T0's 2025 baseline and to any test that uses it. The forum reports an SNI allowlist on AWS address ranges that day, and the Polaris case is a ClientHello stall. T0 should flag the day or split AWS-hosted inputs out.
2. **15 Jan 2025 carries a residual-instability report.** T1's baseline uses it. This does not change the verdict, but T1 could add a row with 15 Jan dropped.
3. **The forum record has a hole from late January to mid-March 2025**, so 2025-02-19 can only be checked against other sources.
4. **The 16 KB cap is a standing background condition in 2026.** The 2026 posts treat it as a constant, with changes in scope (a widening to all Cloudflare subnets reported on 12–13 May on mobile). This is the question for T5b.

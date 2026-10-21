# ntc.party: posts on DNS censorship, interference and interception in Russia, Sept 2024 – Sept 2026

Compiled 22 Sept 2026 from ntc.party's own Discourse search and topic APIs, read through the desktop browser pane (the cloud workspace cannot resolve ntc.party). Companion file: `ntc-party-dns-russia-post-index.csv` (817 dated post pointers in 33 threads, with URLs).

## What was searched, and what "all posts" means here

Pass 1, thread discovery. 45 search queries restricted to posts dated after 22 Sept 2024: `DNS` split into four half-year windows (so no window hit the 500-result cap), plus `ДНС`, `подмена DNS`, `перехват DNS`, `DNS блокировка`, `резолвер`, `DNS spoofing`, `DNS injection`, `DNS interception`, `DNS hijack`, `DoH`, `DoT`, `DoQ`, `DNS over QUIC`, `dnscrypt`, `DNSSEC`, `NXDOMAIN`, `SERVFAIL`, `8.8.8.8`, `DNS Cloudflare 1.1.1.1`, `ECH DNS`, `SVCB`, `HTTPS record`, `DNS ТСПУ`, `DNS РКН`, `DNS Роскомнадзор`, `DNS Ростелеком`, `DNS провайдер`, `DNS оператор`, `заглушка DNS`, `белый список DNS`, `DNS туннель`, `dnstt #russia`, `DNS #russia`, `udp 53`, `порт 53`, `DNS ответ`, `DNS запрос`, and a few others. Result: 2,659 distinct posts in 983 threads; 613 threads contain at least one post whose title or search snippet matches a DNS pattern; 128 of those sit in the Russia category and 307 carry some Russia signal (category, operator name, ТСПУ/РКН, city).

Pass 2, post enumeration. Discourse search returns a sample of posts per thread, not all of them, so for the 33 threads judged most relevant I fetched every post (7,000 posts in total, the largest threads being 1,343, 1,158 and 963 posts long), stripped quotes, and kept every post dated on or after 22 Sept 2024 whose own text matches a DNS pattern (dns/днс/DoH/DoT/DoQ/DNSCrypt/resolver/NXDOMAIN/SERVFAIL/8.8.8.8/1.1.1.1/port 53). That gives the 817 pointers in the CSV. The `interference_keywords` column flags the 296 posts that additionally mention substitution, interception, blocking, ТСПУ/РКН, НСДИ/MSK-IX, port 853, NXDOMAIN or a whitelist; it is a keyword flag, not a reading of the post.

Scope limits worth stating. Pass 2 covered 33 threads, not all 613, so DNS remarks buried in threads I did not enumerate (for example the 9,430-post Zapret thread or the AntiZapret support threads) are represented only by whatever the search sampled. Pattern matching misses posts that describe interception without any of the listed tokens. Reports are self-reports from one forum's users, mostly on wired ISPs in large cities; they date an observation, they do not measure prevalence.

## Timeline of DNS-interference episodes as reported on the forum

Each entry names the thread and post numbers so the claim can be checked. Dates are post dates (UTC).

Nov 2024, ECH/DoH episode. From 5 Nov 2024 Cloudflare ECH stops working on several ISPs (МТС, Ростелеком, Yota) and users find that browser DoH to Cloudflare, Google and others fails in the same window; several posts recommend switching DoH off and note that the ISP resolver "substitutes answers" (12732 #1, #15, #36, #169, #173; 13299 #1, #3, #8). On 8–9 Nov Google DNS is unreachable for an hour on one ISP over both UDP and DoH, and plain UDP answers from 8.8.8.8 are reported substituted (12732 #340). Same week: TTK Volgograd blocks Google DoH for a dnscrypt-proxy user (13017 #1, first noticed 8 Nov); ControlD/Comss DoH breaks and the operator tells a user it has "problems with РКН" (13314 #1, #26); Quad9 users report resets (12740). Google.com A-records from 8.8.8.8 resolving to blocked IPs (13566 #1, 5 Dec).

Jan 2025, the 14 Jan outage and resolver trouble around it. Cloudflare DoH stops working on МТС/МГТС from about 3 Jan; the resolver "keeps flipping from Moscow to Helsinki" (14351 #1, #6, #18; 14511 #1, #5). On 14 Jan the nationwide outage is discussed in a 224-post thread; several users report browser DoH to 1.1.1.1 failing from the morning and one posts a press claim that DNSSEC was involved; another argues the intent was to restrict foreign resolvers and state services broke first (14571 #1, #3, #21, #108, #228). DoH.Pub reported dead 13 Jan (14555). A Dom.ru user says the ISP "is known for DNS substitution" during AntiZapret tunnel failures (14733 #24, #36).

Mar–Apr 2025, Cloudflare test blocks. During the 20 Mar and 30 Mar–2 Apr Cloudflare blocking tests, 1.1.1.1 UDP, DoT and DoH are reported down on МТС Поволжье, Ростелеком, Dom.ru Урал while ICMP still passes; on 2 Apr Google DoH is down too in Поволжье; a Yota resolver returns 127.0.0.1 for Instagram/Facebook and NXDOMAIN for the www names (4625 #260, #287, #308, #329, #377, #395, #525; 15202 #11, #32, #79).

Jun–Jul 2025. Firefox's default DoH (mozilla.cloudflare-dns.com) stops on Ростелеком Omsk on 9 Jun, the day the Cloudflare/OVH/Hetzner blocks begin (4625 #733; 16697 #1, #3, #8). A user running Unbound with DNSSEC finds answers from root servers being spoofed on the path and validation failing (17604 #1, #9, #14, 7 Jul).

Sep–Oct 2025, mobile whitelists. In the 1,158-post mobile-network thread users test which resolvers survive the "белые списки": Beeline answers 8.8.8.8 UDP while T-Mobile does not (16325 #171); the operator's recursive resolver stays reachable, which is what makes dnstt tunnels work at 0.5–1.5 Mbit/s on Beeline (16325 #284, #625, #728; 19123 #2, #344); a whitelist observer notes 1.1.1.1 UDP answering since September (19553 #134). A Ростелеком Юг user reports DoH-plus-GoodbyeDPI failing since mid-September; the thread concludes ECH, not DNS interception, was the trigger (19771 #1, #2, #7). МГТС has had 1.1.1.1 blocked "for over a year" on one tariff (17013 #333, 27 Oct); port 853 is singled out as hard to bypass because no whitelisted SNI exists for it (17013 #380).

Dec 2025. Cloudflare plaintext, DoT and DoH slow to unusable in the evening on МТС home lines; cloudflare-dns.com SNI and :853 reported blocked on one ISP (21223 #1, #13, #18).

Feb–Mar 2026, UDP/53 interception of public resolvers becomes a running topic. 13 Feb: a user notices 8.8.8.8 over UDP/53 no longer returns "bad" sites; replies describe ISP-side substitution, the NSDI, and how to tell (2 ms answers; `nslookup -vc` over TCP still reaches Google) (22192 #1, #2, #5, #8, #9). 16–18 Feb: a VDS user finds 8.8.8.8 UDP timing out intermittently; others confirm interception with substituted IPs and false NXDOMAIN; one proposes TTL-stepped probing to locate the interceptor (22339 #1, #2, #5, #6). 12 Feb, in the confirmed-blocks thread: `*.whatsapp.com` disappears from the ISP resolver's answers, "new fashion to block at DNS" (4625 #1476). 3 Mar: Монитор рунета launches a DNS monitor comparing global resolution with NSDI (22567 #1). 22 Mar: an ISP resolver stops answering for many already-registered domains; replies say plaintext interception has moved from stub-page answers to NXDOMAIN, and that 8.8.8.8 over UDP is intercepted while TCP still reaches Google (23030 #1, #5, #7, #9). 22 Mar: whitelists switched on again in St Petersburg, Google DNS unreachable (16325 #1149). 21 Mar: the thread later used for the August wave opens with a false alarm (a local Portmaster service) (23007 #1, #13).

Apr–May 2026. AdGuard DoH blocked "again" on wired lines, 7–8 Apr, described as a block of that resolver rather than of foreign DNS in general (4374 #4, #5, #6). Google DoH/DoT connections dropping intermittently from 5 May in Moscow (4625 #1569, #1571).

3 Jul 2026, 8.8.8.8 IP:port block. From about 10:00 MSK, 8.8.8.8 is unreachable on TCP 53, 853 and 443 across ТТК, РТК, МТС, Beeline Moscow (AS8402), T2 and Dom.ru Rostov, while 8.8.4.4, 1.1.1.1 and UDP/53 to 8.8.8.8 keep working; one Dom.ru user reports UDP/53 dead as well; users read it as a ТСПУ ip:port rule and a "stress test" of the NSDI migration (4625 #1617, #1618, #1620, #1624, #1625, #1630; 17013 #1110, #1124, #1126, #1145). 31 Jul: Dom.ru ЦФО, DoH to dns.google and to raw IPs affected (13566 #57).

Mid-Aug 2026. DNS answers for some Cloudflare-hosted sites are rewritten to 8.6.112.0/8.47.69.0, addresses that are themselves blocked on ТСПУ (17013 #1360, 19 Aug; 4625 #1637, 18 Aug). OVH domains fail to resolve through Cloudflare's Moscow DoH at certain hours (17013 #1356).

20–28 Aug 2026, the wave the forum calls a "new wave of blocks". This is the densest cluster in the two years (78 keyword-flagged posts in August, most of them here). What the thread reports, region by region: DoH/DoT to dns.google, cloudflare-dns.com, dns.adguard-dns.com, dns.quad9.net, dns.alidns.com blocked by SNI on Ufanet and Megafon (Orenburg), Ростелеком ПФО and ДВ, Dom.ru СЗ (tested 00:00–02:00 on 24 Aug), Beeline (DoT to 1.1.1.1:853 gets SYN-ACK then nothing) (23007 #14, #17, #22, #39, #63, #92; 4625 #1639, #1640). At the same time UDP/53 to 1.1.1.1, 1.0.0.1, 8.8.8.8, 8.8.4.4 and even NSDI and MSK-IX resolvers is intercepted: `whoami.akamai.net` via 8.8.8.8 answers MSK-IX; the responding resolver identifies as RIPN-NS5-RU-MSK; TCP/53 and DoH still reach Google; answers for youtube.com, rutor.info, flibusta.is, rezka.ag come back NXDOMAIN, empty, or with a forged AA flag, while unregistered domains resolve correctly; Yandex UDP DNS is not intercepted (23007 #24, #59, #64, #66–#70, #75, #90, #113, #116, #120, #121, #132, #133, #136, #144). One user localises the interceptor with TTL-stepped queries: a query with TTL 2 (dying before the ТСПУ hop) gets the original answer, TTL 64 gets the substituted one (23007 #145). Mobile networks (МТС, Yota Siberia) largely unaffected (23007 #21, #94, #126). Ростелеком ПФО unblocks Google and Cloudflare DoH on 25 Aug but keeps AdGuard blocked (23007 #63). Wired ТТК/РТК Moscow blocks dnsleaktest.com by IP on 28 Aug (4625 #1644).

Sep 2026. 10 Sep: a home-broadband analogue of the mobile whitelist rolled out from midnight (Dom.ru Поволжье from 13:00 MSK); one user with split DNS sees all `.ru` names return NXDOMAIN for three minutes at midnight (4625 #1658, #1659). 11 Sep: a Ростелеком user reports UDP DNS "recently started being intercepted" and that 1.1.1.1/8.8.8.8/76.76.2.0 answer from NSDI addresses (25892 #7). 19–20 Sep: Dom.ru St Petersburg, UDP/53 to Google and Cloudflare produces no reply at all over IPv4 while IPv6 and TCP work; a traceroute of the UDP/53 path breaks "after the ТСПУ, even abroad" (23007 #188, #192).

## Thread catalogue

Category "Russia" is ntc.party's country subcategory; "Uncat." is Uncategorized. Post counts are Discourse's current post totals (post numbers in the text can exceed them because deleted posts keep their numbers); the "DNS posts" column is the number enumerated in pass 2 for the 33 fully scanned threads, and for the others the number the search sampled (a lower bound). Post numbers give the first place to read.

### A. Threads whose subject is DNS interference in Russia

| Thread | Category | Opened | Posts | DNS posts | What it holds |
|---|---|---|---|---|---|
| 23007 Блокировка DoH Google, Cloudflare, Quad9, OpenDNS | Russia | 2026-03-21 | 164 | 112 | The Aug 2026 wave: DoH/DoT SNI blocks and UDP/53 interception by ISP and region, measurement methods (`whoami.akamai.net`, `dig +tcp`, TTL stepping), dpi-detector releases. Start at #14. |
| 22339 Периодически недоступен DNS сервер 8.8.8.8 на VDS | Russia | 2026-02-18 | 18 | 11 | Feb 2026 UDP/53 interception of 8.8.8.8 confirmed from several ISPs; TTL-probe idea. |
| 22192 Как понять пров подменяет или гугл сам? | Uncat. | 2026-02-13 | 12 | 10 | How to distinguish ISP substitution from resolver behaviour. |
| 23030 Поредили местные DNS | Uncat. | 2026-03-22 | 11 | 8 | ISP resolvers moving from stub answers to NXDOMAIN; UDP vs TCP asymmetry. |
| 17604 Перехват ответов от корневых DNS серверов | Russia | 2025-07-07 | 14 | 9 | Root-server answers spoofed on path, DNSSEC validation fails in Unbound. |
| 13017 TTK Волгоград заблокировал Google DNS | Russia | 2024-11-12 | 3 | 1 | Google DoH blocked on TTK from 8 Nov 2024. |
| 21223 Замедление dns от cloudflare | Russia | 2025-12-08 | 21 | 13 | Cloudflare plaintext/DoT/DoH throttled on МТС evenings; :853 and SNI blocked on one ISP. |
| 14351 Cloudflare dns МТС/МГТС не работает | Uncat. | 2025-01-06 | 23 | 12 | Jan 2025 Cloudflare DoH failure on МТС/МГТС. |
| 14511 Провайдер МТС и работа dns | Uncat. | 2025-01-11 | 11 | 8 | Same episode from the router side. |
| 16697 Перестал работать DNS over HTTPS (DoH) | Uncat. | 2025-06-11 | 22 | 11 | Cloudflare DoH unstable from 9 Jun 2025. |
| 4374 РКН по всей видимости блокирует adguard.com | Russia | 2023-04-24 | 7 | 3 | Apr 2026 AdGuard DoH block (posts #4–#6). |
| 12740 Quad9 dns | Russia | 2024-11-05 | 4 | 3 | Nov 2024 Quad9 trouble. |
| 14603 DoH Cloudflare заблокирован? (нет) | Russia | 2025-01-15 | 5 | 2 | Post-outage false alarm, 15 Jan 2025. |
| 14555 DoH.Pub Накрылся? | Uncat. | 2025-01-13 | 2 | 1 | DoH.Pub unreachable 13 Jan 2025. |
| 13299 Началось? чебурнетизм? (днс блочат) | Uncat. | 2024-11-22 | 19 | 9 | Nov 2024: 1.1.1.1/8.8.8.8 DoH failing, Google-resolved IPs blocked. |
| 19771 Двухфакторная блокировка … при использовании DoH? | Russia | 2025-09-28 | 8 | 8 | Hypothesis of DoH-conditioned blocking; resolved as ECH. |
| 22567 Монитор DNS | Russia | 2026-03-03 | 17 | 13 | Монитор рунета's NSDI-vs-global DNS comparison tool. |
| 25892 Проблема с realme.com и ControlD | Uncat. | 2026-09-11 | 17 | 11 | Sept 2026 UDP interception on Ростелеком (#7); ECS/geo effects. |
| 25745 DoH на Windows 10 | Russia | 2026-08-30 | 29 | 22 | Aftermath of the Aug wave; how-to, with substitution diagnosis at #14, #18. |
| 12356 Проблемы с DoH от Comss | Uncat. | 2024-10-27 | 39 | 22 | Comss DoH failing on TTK, Oct 2024. |
| 13314 DoH Controld и ресурсы microsoft | Uncat. | 2024-11-23 | 44 | 21 | ControlD DoH breakage; operator cites РКН (#26). |
| 12695 Создание "собственного" comss dns | Russia | 2024-11-04 | 60 | 31 | Building a geo-unblocking DoH; touches РКН SNI blocks (#24). |
| 14733 Новый вид блокировок? | antizapret / help | 2025-01-19 | 45 | 21 | Dom.ru DNS substitution suspected during AntiZapret failures (#24, #36). |
| 19062 Не резолвятся домены ntc.party и adblockplus.org | antizapret | 2025-09-01 | 25 | 7 | AntiZapret resolver vs 8.8.8.8 differences. |

### B. Broader threads that carry dated DNS-interference reports

| Thread | Category | Opened | Posts | DNS posts | Where the DNS material is |
|---|---|---|---|---|---|
| 4625 Сообщения об отдельных подтверждённых блокировках ТСПУ | Russia | 2023-06-01 | 963 | 72 | Confirmed-block log: Cloudflare DNS Mar–Apr 2025 (#260–#409), 3 Jul 2026 8.8.8.8 ip:port block (#1617–#1630), Beeline DoT / Google DoH 21 Aug 2026 (#1639, #1640), 10 Sep 2026 home whitelist and `.ru` NXDOMAIN (#1658, #1659). |
| 17013 Блокировка Cloudflare, OVH, Hetzner, DigitalOcean… | Russia | 2025-06-18 | 1,343 | 103 | МГТС 1.1.1.1 block (#333), port 853 (#380), 3 Jul 2026 8.8.8.8 (#1110–#1146), Aug 2026 Cloudflare answer rewriting to blocked IPs (#1360–#1362). |
| 16325 Мобильная сеть 09.05.2025 | Russia | 2025-05-08 | 1,158 | 111 | Which resolvers survive mobile whitelists (#164–#182, #617, #746), dnstt over operator resolvers (#284, #625, #728), Mar 2026 St Petersburg (#1149). |
| 12732 Обсуждение: Блокировка (замедление) ECH Cloudflare | Russia | 2024-11-05 | 429 | 108 | Nov 2024 DoH failures and substitution (#1, #15, #36, #169, #173, #340). |
| 14571 Массовый сбой … 14 января 2025 | Uncat. | 2025-01-14 | 224 | 22 | Resolver-side symptoms of the 14 Jan outage (#3, #21, #74, #108, #228). |
| 22551 Блокировки на российских серверах Cloudflare (CDN/DNS/WARP) | Russia | 2026-03-01 | 127 | 17 | Proton domains SERVFAIL/not resolving (#1, #38). |
| 13566 Блокировка google.com | Russia | 2024-12-05 | 57 | 11 | Google IPs from 8.8.8.8 blocked (#1); Dom.ru DoH Jul 2026 (#57). |
| 19553 Наблюдения за введением "Белых списков" в РФ | Russia | 2025-09-19 | 40 | 2 | 1.1.1.1 UDP surviving mobile whitelists (#134). |
| 14831 Очередной сбой в работе интернета в РФ | Uncat. | 2025-01-24 | 32 | 2 | dnscrypt latency during 24 Jan 2025 outage (#23). |
| 22237 CLI-инструмент для тестирования DPI-блокировок | Russia | 2026-02-15 | 166 | 19 (sampled) | dpi-detector, includes a UDP DNS substitution test; not enumerated. |
| 22516 16кб блокировка | Russia | 2026-02-26 | 220 | 6 (sampled) | Tool list including DNS checks; not enumerated. |
| 19123 Обход белых списков (Теория) | Uncat. | 2025-09-06 | 295 | 5 (sampled) | Operator resolvers and dnstt under whitelists (#2, #40, #344); not enumerated. |
| 13598 В Дагестане отключили зарубежный интернет | Russia | 2024-12-06 | 203 | 8 (sampled) | Which resolvers worked inside the Dec 2024 regional shutdown (#55–#57). |
| 15202 Cloudflare заблокировали? | Russia | 2025-03-20 | 87 | 5 (sampled) | 20 Mar 2025 test: DoH and root servers over IPv6 down (#11, #32, #79). |
| 22307 Архитектура и принцип работы ТСПУ | Research | 2026-03-25 | 71 | 1 (sampled) | Points to dpi-detector's DNS test (#61). |
| 23589 Тестирование ТСПУ | Tools | 2026-04-05 | 21 | 1 (sampled) | NXDOMAIN observations in a test list (#8). |

### C. Research-category posts touching DNS (Censorship research & publications)

22467 "Towards Automated DNS Censorship Circumvention" (FOCI 2026, posted 2026-02-23); 24843 "DNS-Morph: UDP-Based Bootstrapping Protocol for Tor" (CSCML 2021, posted 2026-05-22); 24924 "DNS-sly: Avoiding Censorship through Network Complexity" (FOCI 2016, posted 2026-05-29); 22584 "Реверс инжиниринг модуля проверки успешности блокировок внутри мессенджера MAX" (2026-03-05, 236 posts, DNS mentioned in passing); 22525, 22696, 22933, 25592, 25714 are paper announcements where DNS appears only in the abstract or a comment.

### D. Excluded as not about interference (for completeness)

The remaining ~560 threads with DNS-matching posts are client configuration (sing-box, xray, nekoray, Mihomo DNS settings, FakeDNS, DNS leaks), router how-tos, AntiZapret/zapret support, resolver choice discussions (14469 "Имеет ли смысл использовать DNSCrypt?", 25711 "Как сравнить и выбрать DNS сервер?", 14129, 25599), and geo-unblocking DoH services (Comss, ControlD, xbox-dns). They contain the occasional dated observation, and the search snippets for all of them are in the browser session's data, but I did not enumerate them.

## Reading for the thesis

The Atlas finding of 22 Sept 2026 (`dns-udp53-substitution-finding-2026-09-22.md`) tests root-targeted built-ins and leaves the public-resolver claim untested. The forum reports above are exactly that claim, dated: UDP/53 to 8.8.8.8 and 1.1.1.1 answered by NSDI/MSK-IX resolvers, first as scattered reports in Feb–Mar 2026 and then as a multi-ISP wave from 20 Aug 2026, with the interceptor located after the ТСПУ hop by TTL stepping, TCP/53 untouched, Yandex UDP untouched, and answers for registered domains replaced by NXDOMAIN, empty sets or forged authoritative answers. The 3 Jul 2026 8.8.8.8 ip:port block (TCP 53/853/443 on many ISPs, UDP intact) and the Aug 2026 SNI blocks on DoH/DoT endpoints are separate mechanisms from the UDP substitution and should be catalogued as such.

For a measurement design: Atlas UDM `DNS` measurements to 8.8.8.8, 1.1.1.1, 9.9.9.9 and a Yandex resolver from RU probes, asking `whoami.akamai.net A` (answer identifies the resolver's egress; forum users got MSK-IX addresses) and a registered domain such as `rutor.info`, over UDP and TCP, with `set_nsid` and a control name, would reproduce the forum's diagnostic directly and date onsets per ASN; the DE control from the Atlas work carries over. The forum gives a prior on which ASNs to look at first: Dom.ru (Эр-Телеком), Ростелеком regional segments, Ufanet, Beeline wired, Таттелеком, and, for the ip:port block, T2/ТТК/МТС. Treat all of it as leads to test, not findings.

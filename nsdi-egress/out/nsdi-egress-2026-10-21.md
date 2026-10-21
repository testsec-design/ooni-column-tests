# NSDI resolver egress, active measurement from this Mac, 2026-10-21

**Caveat.** This measures the egress of 195.208.4.1 / 195.208.5.1 as of 2026-10-21 (October 2026). The comparison in section 4 with the December 2025 window TSVs assumes the egress pool was stable between December 2025 and this run; nothing here checks that. It is also one vantage point: the NSDI addresses are anycast, so the node (and egress pool) reached from this machine in Germany need not be the one Russian probes reached in December; an egress IP in a sibling /24 with the same MSK-IX origin ASN is consistent with another node of the same service, not evidence against it.

Run from public IP 2a00:c380:f002:4:9999::196 (origin AS50629, LWLCOM LWLcom GmbH); system resolver 10.128.0.1. 431 queries sent (cap 500); one attempt each, 5 s timeout; >= 1 s between queries to one target; whoami rounds 15 s apart (20 rounds for NSDI, 10 for the controls), ground-truth rounds 5 s apart (5 rounds). Per-query records: `nsdi-egress-2026-10-21-queries.tsv`. Registry data: RIPEstat via T6/ripestat.py.

## 1. Control table: resolver -> egress IPs -> origin ASN -> holder

Expected: 8.8.8.8 -> AS15169, 1.1.1.1 -> AS13335, system resolver -> this machine's ISP ASN (AS50629 from the public IP above).

### google (8.8.8.8): 40 whoami queries, NOERROR x40, median RTT 68 ms, 8 distinct egress IPs, origin ASNs {AS13335, AS15169, AS50629} -> expected AS15169: **FAIL**

| egress IP | queries | prefix | origin ASN | holder |
|---|---|---|---|---|
| 193.46.232.197 | 10 | 193.46.232.0/23 | AS50629 | LWLCOM LWLcom GmbH |
| 141.101.104.145 | 6 | 141.101.104.0/24 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. |
| 2a00:c380:f002:5:9999::197 | 6 | 2a00:c380::/32 | AS50629 | LWLCOM LWLcom GmbH |
| 193.46.232.196 | 4 | 193.46.232.0/23 | AS50629 | LWLCOM LWLcom GmbH |
| 2a00:1450:4013:c1a::122 | 4 | 2a00:1450:4013::/48 | AS15169 | GOOGLE - Google LLC |
| 104.23.163.67 | 4 | 104.23.163.0/24 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. |
| 2a00:c380:f002:3:9999::195 | 4 | 2a00:c380::/32 | AS50629 | LWLCOM LWLcom GmbH |
| 2a00:c380:f002:4:9999::196 | 2 | 2a00:c380::/32 | AS50629 | LWLCOM LWLcom GmbH |

### cloudflare (1.1.1.1): 40 whoami queries, NOERROR x40, median RTT 77 ms, 8 distinct egress IPs, origin ASNs {AS13335, AS15169, AS50629} -> expected AS13335: **FAIL**

| egress IP | queries | prefix | origin ASN | holder |
|---|---|---|---|---|
| 193.46.232.197 | 10 | 193.46.232.0/23 | AS50629 | LWLCOM LWLcom GmbH |
| 2a00:c380:f002:5:9999::197 | 7 | 2a00:c380::/32 | AS50629 | LWLCOM LWLcom GmbH |
| 141.101.104.145 | 6 | 141.101.104.0/24 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. |
| 193.46.232.196 | 4 | 193.46.232.0/23 | AS50629 | LWLCOM LWLcom GmbH |
| 2a00:1450:4013:c1a::122 | 4 | 2a00:1450:4013::/48 | AS15169 | GOOGLE - Google LLC |
| 104.23.163.67 | 4 | 104.23.163.0/24 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. |
| 2a00:c380:f002:3:9999::195 | 3 | 2a00:c380::/32 | AS50629 | LWLCOM LWLcom GmbH |
| 2a00:c380:f002:4:9999::196 | 2 | 2a00:c380::/32 | AS50629 | LWLCOM LWLcom GmbH |

### system (10.128.0.1): 40 whoami queries, NOERROR x40, median RTT 71 ms, 8 distinct egress IPs, origin ASNs {AS13335, AS15169, AS50629} -> expected AS50629: **FAIL**

| egress IP | queries | prefix | origin ASN | holder |
|---|---|---|---|---|
| 193.46.232.197 | 10 | 193.46.232.0/23 | AS50629 | LWLCOM LWLcom GmbH |
| 2a00:c380:f002:5:9999::197 | 7 | 2a00:c380::/32 | AS50629 | LWLCOM LWLcom GmbH |
| 141.101.104.145 | 6 | 141.101.104.0/24 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. |
| 193.46.232.196 | 4 | 193.46.232.0/23 | AS50629 | LWLCOM LWLcom GmbH |
| 2a00:1450:4013:c1a::122 | 4 | 2a00:1450:4013::/48 | AS15169 | GOOGLE - Google LLC |
| 104.23.163.67 | 4 | 104.23.163.0/24 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. |
| 2a00:c380:f002:3:9999::195 | 3 | 2a00:c380::/32 | AS50629 | LWLCOM LWLcom GmbH |
| 2a00:c380:f002:4:9999::196 | 2 | 2a00:c380::/32 | AS50629 | LWLCOM LWLcom GmbH |

**Controls: FAIL, the method is wrong and the NSDI rows below are not to be trusted.**

## 2. NSDI table: egress per address, UDP and TCP separately

### a.res-nsdi.ru (195.208.4.1) over UDP: 40 whoami queries (20 per qname), NOERROR x40, median RTT 51 ms; **14 distinct egress IPs**; origin ASNs {AS13335, AS15169, AS50629} (0 of 3 in dnslook.MSK_IX_ASNS)

| egress IP | queries | prefix | origin ASN | holder |
|---|---|---|---|---|
| 193.46.232.197 | 11 | 193.46.232.0/23 | AS50629 | LWLCOM LWLcom GmbH |
| 141.101.104.145 | 4 | 141.101.104.0/24 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. |
| 193.46.232.196 | 3 | 193.46.232.0/23 | AS50629 | LWLCOM LWLcom GmbH |
| 2a00:c380:f002:5:9999::197 | 3 | 2a00:c380::/32 | AS50629 | LWLCOM LWLcom GmbH |
| 104.23.163.40 | 3 | 104.23.163.0/24 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. |
| 2a00:1450:4013:c1a::122 | 2 | 2a00:1450:4013::/48 | AS15169 | GOOGLE - Google LLC |
| 104.23.163.67 | 2 | 104.23.163.0/24 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. |
| 2a00:c380:f002:3:9999::195 | 2 | 2a00:c380::/32 | AS50629 | LWLCOM LWLcom GmbH |
| 2a00:c380:f002:4:9999::196 | 2 | 2a00:c380::/32 | AS50629 | LWLCOM LWLcom GmbH |
| 173.194.170.80 | 2 | 173.194.0.0/16 | AS15169 | GOOGLE - Google LLC |
| 2400:cb00:114:1024::ac44:31cd | 2 | 2400:cb00:114::/48 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. |
| 172.68.49.204 | 2 | 172.68.49.0/24 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. |
| 172.217.40.16 | 1 | 172.217.0.0/16 | AS15169 | GOOGLE - Google LLC |
| 74.125.114.218 | 1 | 74.125.0.0/16 | AS15169 | GOOGLE - Google LLC |

### a.res-nsdi.ru (195.208.4.1) over TCP: 40 whoami queries (20 per qname), NOERROR x40, median RTT 109 ms; **14 distinct egress IPs**; origin ASNs {AS13335, AS15169, AS50629} (0 of 3 in dnslook.MSK_IX_ASNS)

| egress IP | queries | prefix | origin ASN | holder |
|---|---|---|---|---|
| 193.46.232.197 | 12 | 193.46.232.0/23 | AS50629 | LWLCOM LWLcom GmbH |
| 193.46.232.196 | 3 | 193.46.232.0/23 | AS50629 | LWLCOM LWLcom GmbH |
| 141.101.104.145 | 3 | 141.101.104.0/24 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. |
| 2a00:c380:f002:5:9999::197 | 3 | 2a00:c380::/32 | AS50629 | LWLCOM LWLcom GmbH |
| 104.23.163.40 | 3 | 104.23.163.0/24 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. |
| 2a00:1450:4013:c1a::122 | 2 | 2a00:1450:4013::/48 | AS15169 | GOOGLE - Google LLC |
| 104.23.163.67 | 2 | 104.23.163.0/24 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. |
| 2a00:c380:f002:3:9999::195 | 2 | 2a00:c380::/32 | AS50629 | LWLCOM LWLcom GmbH |
| 2a00:c380:f002:4:9999::196 | 2 | 2a00:c380::/32 | AS50629 | LWLCOM LWLcom GmbH |
| 173.194.170.80 | 2 | 173.194.0.0/16 | AS15169 | GOOGLE - Google LLC |
| 2400:cb00:114:1024::ac44:31cd | 2 | 2400:cb00:114::/48 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. |
| 172.68.49.204 | 2 | 172.68.49.0/24 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. |
| 172.217.40.16 | 1 | 172.217.0.0/16 | AS15169 | GOOGLE - Google LLC |
| 74.125.114.218 | 1 | 74.125.0.0/16 | AS15169 | GOOGLE - Google LLC |

Egress sets by qname for a.res-nsdi.ru: akamai.net 4 IPs, akahelp.net 11 IPs, 1 in common.

### b.res-nsdi.ru (195.208.5.1) over UDP: 40 whoami queries (20 per qname), NOERROR x40, median RTT 41 ms; **14 distinct egress IPs**; origin ASNs {AS13335, AS15169, AS50629} (0 of 3 in dnslook.MSK_IX_ASNS)

| egress IP | queries | prefix | origin ASN | holder |
|---|---|---|---|---|
| 193.46.232.197 | 12 | 193.46.232.0/23 | AS50629 | LWLCOM LWLcom GmbH |
| 193.46.232.196 | 3 | 193.46.232.0/23 | AS50629 | LWLCOM LWLcom GmbH |
| 141.101.104.145 | 3 | 141.101.104.0/24 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. |
| 2a00:c380:f002:5:9999::197 | 3 | 2a00:c380::/32 | AS50629 | LWLCOM LWLcom GmbH |
| 104.23.163.40 | 3 | 104.23.163.0/24 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. |
| 2a00:1450:4013:c1a::122 | 2 | 2a00:1450:4013::/48 | AS15169 | GOOGLE - Google LLC |
| 104.23.163.67 | 2 | 104.23.163.0/24 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. |
| 2a00:c380:f002:3:9999::195 | 2 | 2a00:c380::/32 | AS50629 | LWLCOM LWLcom GmbH |
| 2a00:c380:f002:4:9999::196 | 2 | 2a00:c380::/32 | AS50629 | LWLCOM LWLcom GmbH |
| 173.194.170.80 | 2 | 173.194.0.0/16 | AS15169 | GOOGLE - Google LLC |
| 2400:cb00:114:1024::ac44:31cd | 2 | 2400:cb00:114::/48 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. |
| 172.68.49.204 | 2 | 172.68.49.0/24 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. |
| 172.217.40.16 | 1 | 172.217.0.0/16 | AS15169 | GOOGLE - Google LLC |
| 74.125.114.218 | 1 | 74.125.0.0/16 | AS15169 | GOOGLE - Google LLC |

### b.res-nsdi.ru (195.208.5.1) over TCP: 40 whoami queries (20 per qname), NOERROR x40, median RTT 98 ms; **14 distinct egress IPs**; origin ASNs {AS13335, AS15169, AS50629} (0 of 3 in dnslook.MSK_IX_ASNS)

| egress IP | queries | prefix | origin ASN | holder |
|---|---|---|---|---|
| 193.46.232.197 | 12 | 193.46.232.0/23 | AS50629 | LWLCOM LWLcom GmbH |
| 193.46.232.196 | 3 | 193.46.232.0/23 | AS50629 | LWLCOM LWLcom GmbH |
| 141.101.104.145 | 3 | 141.101.104.0/24 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. |
| 2a00:c380:f002:5:9999::197 | 3 | 2a00:c380::/32 | AS50629 | LWLCOM LWLcom GmbH |
| 104.23.163.40 | 3 | 104.23.163.0/24 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. |
| 2a00:1450:4013:c1a::122 | 2 | 2a00:1450:4013::/48 | AS15169 | GOOGLE - Google LLC |
| 104.23.163.67 | 2 | 104.23.163.0/24 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. |
| 2a00:c380:f002:3:9999::195 | 2 | 2a00:c380::/32 | AS50629 | LWLCOM LWLcom GmbH |
| 2a00:c380:f002:4:9999::196 | 2 | 2a00:c380::/32 | AS50629 | LWLCOM LWLcom GmbH |
| 173.194.170.80 | 2 | 173.194.0.0/16 | AS15169 | GOOGLE - Google LLC |
| 2400:cb00:114:1024::ac44:31cd | 2 | 2400:cb00:114::/48 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. |
| 172.68.49.204 | 2 | 172.68.49.0/24 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. |
| 172.217.40.16 | 1 | 172.217.0.0/16 | AS15169 | GOOGLE - Google LLC |
| 74.125.114.218 | 1 | 74.125.0.0/16 | AS15169 | GOOGLE - Google LLC |

Egress sets by qname for b.res-nsdi.ru: akamai.net 4 IPs, akahelp.net 11 IPs, 1 in common.

## 3. Ground-truth table: rcode per (resolver, qname, transport)

5 queries per cell. example.com and ya.ru are negative controls and must answer; www.youtube.com is the current ground truth for the DNS stage.

| resolver | qname | transport | rcodes / errors | distinct A answers | median RTT ms |
|---|---|---|---|---|---|
| a.res-nsdi.ru (195.208.4.1) | www.youtube.com | udp | NOERROR x4, timeout x1 | 8: 142.251.150.4, 142.251.151.4, 142.251.152.4, 142.251.153.4, 142.251.154.4, 142.251.155.4 ... | 40 |
| a.res-nsdi.ru (195.208.4.1) | www.youtube.com | tcp | NOERROR x5 | 8: 142.251.150.4, 142.251.151.4, 142.251.152.4, 142.251.153.4, 142.251.154.4, 142.251.155.4 ... | 81 |
| a.res-nsdi.ru (195.208.4.1) | example.com | udp | NOERROR x5 | 2: 104.20.23.154, 172.66.147.243 | 39 |
| a.res-nsdi.ru (195.208.4.1) | example.com | tcp | NOERROR x4, timeout x1 | 2: 104.20.23.154, 172.66.147.243 | 93 |
| a.res-nsdi.ru (195.208.4.1) | ya.ru | udp | NOERROR x5 | 3: 5.255.255.242, 77.88.44.242, 77.88.55.242 | 42 |
| a.res-nsdi.ru (195.208.4.1) | ya.ru | tcp | NOERROR x4, timeout x1 | 3: 5.255.255.242, 77.88.44.242, 77.88.55.242 | 80 |
| b.res-nsdi.ru (195.208.5.1) | www.youtube.com | udp | NOERROR x5 | 8: 142.251.150.4, 142.251.151.4, 142.251.152.4, 142.251.153.4, 142.251.154.4, 142.251.155.4 ... | 41 |
| b.res-nsdi.ru (195.208.5.1) | www.youtube.com | tcp | NOERROR x5 | 8: 142.251.150.4, 142.251.151.4, 142.251.152.4, 142.251.153.4, 142.251.154.4, 142.251.155.4 ... | 65 |
| b.res-nsdi.ru (195.208.5.1) | example.com | udp | NOERROR x5 | 2: 104.20.23.154, 172.66.147.243 | 49 |
| b.res-nsdi.ru (195.208.5.1) | example.com | tcp | NOERROR x4, timeout x1 | 2: 104.20.23.154, 172.66.147.243 | 80 |
| b.res-nsdi.ru (195.208.5.1) | ya.ru | udp | NOERROR x5 | 3: 5.255.255.242, 77.88.44.242, 77.88.55.242 | 37 |
| b.res-nsdi.ru (195.208.5.1) | ya.ru | tcp | NOERROR x5 | 3: 5.255.255.242, 77.88.44.242, 77.88.55.242 | 67 |
| google (8.8.8.8) | www.youtube.com | udp | NOERROR x5 | 8: 142.251.150.4, 142.251.151.4, 142.251.152.4, 142.251.153.4, 142.251.154.4, 142.251.155.4 ... | 73 |
| google (8.8.8.8) | www.youtube.com | tcp | NOERROR x5 | 8: 142.251.150.4, 142.251.151.4, 142.251.152.4, 142.251.153.4, 142.251.154.4, 142.251.155.4 ... | 74 |
| google (8.8.8.8) | example.com | udp | NOERROR x5 | 2: 104.20.23.154, 172.66.147.243 | 46 |
| google (8.8.8.8) | example.com | tcp | NOERROR x4, timeout x1 | 2: 104.20.23.154, 172.66.147.243 | 194 |
| google (8.8.8.8) | ya.ru | udp | NOERROR x4, timeout x1 | 3: 5.255.255.242, 77.88.44.242, 77.88.55.242 | 37 |
| google (8.8.8.8) | ya.ru | tcp | NOERROR x4, timeout x1 | 3: 5.255.255.242, 77.88.44.242, 77.88.55.242 | 69 |
| cloudflare (1.1.1.1) | www.youtube.com | udp | NOERROR x5 | 8: 142.251.150.4, 142.251.151.4, 142.251.152.4, 142.251.153.4, 142.251.154.4, 142.251.155.4 ... | 43 |
| cloudflare (1.1.1.1) | www.youtube.com | tcp | NOERROR x5 | 8: 142.251.150.4, 142.251.151.4, 142.251.152.4, 142.251.153.4, 142.251.154.4, 142.251.155.4 ... | 75 |
| cloudflare (1.1.1.1) | example.com | udp | NOERROR x5 | 2: 104.20.23.154, 172.66.147.243 | 32 |
| cloudflare (1.1.1.1) | example.com | tcp | NOERROR x4, timeout x1 | 2: 104.20.23.154, 172.66.147.243 | 115 |
| cloudflare (1.1.1.1) | ya.ru | udp | NOERROR x5 | 3: 5.255.255.242, 77.88.44.242, 77.88.55.242 | 37 |
| cloudflare (1.1.1.1) | ya.ru | tcp | NOERROR x5 | 3: 5.255.255.242, 77.88.44.242, 77.88.55.242 | 61 |
| system (10.128.0.1) | www.youtube.com | udp | NOERROR x5 | 8: 142.251.150.4, 142.251.151.4, 142.251.152.4, 142.251.153.4, 142.251.154.4, 142.251.155.4 ... | 45 |
| system (10.128.0.1) | www.youtube.com | tcp | NOERROR x5 | 8: 142.251.150.4, 142.251.151.4, 142.251.152.4, 142.251.153.4, 142.251.154.4, 142.251.155.4 ... | 68 |
| system (10.128.0.1) | example.com | udp | NOERROR x5 | 2: 104.20.23.154, 172.66.147.243 | 35 |
| system (10.128.0.1) | example.com | tcp | NOERROR x3, timeout x2 | 2: 104.20.23.154, 172.66.147.243 | 64 |
| system (10.128.0.1) | ya.ru | udp | NOERROR x4, timeout x1 | 3: 5.255.255.242, 77.88.44.242, 77.88.55.242 | 30 |
| system (10.128.0.1) | ya.ru | tcp | NOERROR x4, timeout x1 | 3: 5.255.255.242, 77.88.44.242, 77.88.55.242 | 65 |

Negative controls: no cell failed outright. Partial loss: a.res-nsdi.ru example.com tcp answered 4 of 5 (timeout x1); a.res-nsdi.ru ya.ru tcp answered 4 of 5 (timeout x1); b.res-nsdi.ru example.com tcp answered 4 of 5 (timeout x1); google example.com tcp answered 4 of 5 (timeout x1); google ya.ru udp answered 4 of 5 (timeout x1); google ya.ru tcp answered 4 of 5 (timeout x1); cloudflare example.com tcp answered 4 of 5 (timeout x1); system example.com tcp answered 3 of 5 (timeout x2); system ya.ru udp answered 4 of 5 (timeout x1); system ya.ru tcp answered 4 of 5 (timeout x1).

## 4. Comparison with the December 2025 window TSVs (read through dnslook.read_rows)

NSDI egress set = union of the egress IPs in section 2 (both addresses, both transports, both qnames), measured 2026-10-21; see the caveat at the top.

NSDI egress IPs (14): 74.125.114.218, 104.23.163.40, 104.23.163.67, 141.101.104.145, 172.68.49.204, 172.217.40.16, 173.194.170.80, 193.46.232.196, 193.46.232.197, 2400:cb00:114:1024::ac44:31cd, 2a00:1450:4013:c1a::122, 2a00:c380:f002:3:9999::195, 2a00:c380:f002:4:9999::196, 2a00:c380:f002:5:9999::197

NSDI egress /24s (7): 104.23.163.0/24, 141.101.104.0/24, 172.217.40.0/24, 172.68.49.0/24, 173.194.170.0/24, 193.46.232.0/24, 74.125.114.0/24

| set | file | rows | distinct resolver_ip | overlap with NSDI egress (exact IP) | overlap by /24 |
|---|---|---|---|---|---|
| (a) NXDOMAIN rows | window_dec_onset.tsv | 50 | 20 | 0 | 1 |
| (b) AS206385 rows | window_dec_onset.tsv | 0 | 0 | 0 | 0 |
| (a) NXDOMAIN rows | window_dec_allru.tsv | 34 | 13 | 0 | 1 |
| (b) AS206385 rows | window_dec_allru.tsv | 72 | 2 | 0 | 0 |
| (a) NXDOMAIN rows | both files (union) | | 20 | 0 | 1 |
| (b) AS206385 rows | both files (union) | | 2 | 0 | 0 |

**(a) NXDOMAIN rows, window_dec_onset.tsv**: resolver_ip values (excluding unrecorded ['', '127.0.0.2']):

| resolver_ip | prefix | origin ASN | holder | in NSDI egress (exact) | NSDI /24 |
|---|---|---|---|---|---|
| 74.125.74.21 | 74.125.72.0/22 | AS15169 | GOOGLE - Google LLC | no | no |
| 74.125.114.156 | 74.125.0.0/16 | AS15169 | GOOGLE - Google LLC | no | yes |
| 172.68.9.62 | 172.68.9.0/24 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. | no | no |
| 193.232.93.51 | 193.232.93.0/24 | AS43832 | RIPN-NS5-RU-MSK Join-stock company "Internet Exchange"MSK-IX" | no | no |
| 193.232.139.57 | 193.232.139.0/24 | AS47445 | RIPN-RU-RND Join-stock company "Internet Exchange"MSK-IX" | no | no |
| 193.232.160.48 | 193.232.160.0/24 | AS43832 | RIPN-NS5-RU-MSK Join-stock company "Internet Exchange"MSK-IX" | no | no |
| 193.232.160.51 | 193.232.160.0/24 | AS43832 | RIPN-NS5-RU-MSK Join-stock company "Internet Exchange"MSK-IX" | no | no |
| 193.232.177.49 | 193.232.177.0/24 | AS43832 | RIPN-NS5-RU-MSK Join-stock company "Internet Exchange"MSK-IX" | no | no |
| 193.232.177.50 | 193.232.177.0/24 | AS43832 | RIPN-NS5-RU-MSK Join-stock company "Internet Exchange"MSK-IX" | no | no |
| 193.232.177.51 | 193.232.177.0/24 | AS43832 | RIPN-NS5-RU-MSK Join-stock company "Internet Exchange"MSK-IX" | no | no |
| 193.232.230.48 | 193.232.230.0/24 | AS42139 | RIPN-RU-NSK Join-stock company "Internet Exchange"MSK-IX" | no | no |
| 193.232.230.51 | 193.232.230.0/24 | AS42139 | RIPN-RU-NSK Join-stock company "Internet Exchange"MSK-IX" | no | no |
| 193.232.231.48 | 193.232.231.0/24 | AS42728 | RIPN-RU-EKT Join-stock company "Internet Exchange"MSK-IX" | no | no |
| 193.232.231.51 | 193.232.231.0/24 | AS42728 | RIPN-RU-EKT Join-stock company "Internet Exchange"MSK-IX" | no | no |
| 193.232.236.51 | 193.232.236.0/24 | AS47445 | RIPN-RU-RND Join-stock company "Internet Exchange"MSK-IX" | no | no |
| 193.232.240.49 | 193.232.240.0/24 | AS42139 | RIPN-RU-NSK Join-stock company "Internet Exchange"MSK-IX" | no | no |
| 193.232.240.50 | 193.232.240.0/24 | AS42139 | RIPN-RU-NSK Join-stock company "Internet Exchange"MSK-IX" | no | no |
| 194.226.75.82 | 194.226.75.0/24 | AS43832 | RIPN-NS5-RU-MSK Join-stock company "Internet Exchange"MSK-IX" | no | no |
| 194.226.75.83 | 194.226.75.0/24 | AS43832 | RIPN-NS5-RU-MSK Join-stock company "Internet Exchange"MSK-IX" | no | no |
| 212.1.244.99 | 212.1.224.0/19 | AS12714 | MEGAFON-AS PJSC MegaFon | no | no |

**(b) AS206385 rows, window_dec_onset.tsv**: resolver_ip values (excluding unrecorded ['', '127.0.0.2']):

| resolver_ip | prefix | origin ASN | holder | in NSDI egress (exact) | NSDI /24 |
|---|---|---|---|---|---|
| (none) | | | | | |

**(a) NXDOMAIN rows, window_dec_allru.tsv**: resolver_ip values (excluding unrecorded ['', '127.0.0.2']):

| resolver_ip | prefix | origin ASN | holder | in NSDI egress (exact) | NSDI /24 |
|---|---|---|---|---|---|
| 74.125.74.21 | 74.125.72.0/22 | AS15169 | GOOGLE - Google LLC | no | no |
| 74.125.114.156 | 74.125.0.0/16 | AS15169 | GOOGLE - Google LLC | no | yes |
| 172.68.9.62 | 172.68.9.0/24 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. | no | no |
| 193.232.93.51 | 193.232.93.0/24 | AS43832 | RIPN-NS5-RU-MSK Join-stock company "Internet Exchange"MSK-IX" | no | no |
| 193.232.139.57 | 193.232.139.0/24 | AS47445 | RIPN-RU-RND Join-stock company "Internet Exchange"MSK-IX" | no | no |
| 193.232.160.48 | 193.232.160.0/24 | AS43832 | RIPN-NS5-RU-MSK Join-stock company "Internet Exchange"MSK-IX" | no | no |
| 193.232.160.51 | 193.232.160.0/24 | AS43832 | RIPN-NS5-RU-MSK Join-stock company "Internet Exchange"MSK-IX" | no | no |
| 193.232.177.49 | 193.232.177.0/24 | AS43832 | RIPN-NS5-RU-MSK Join-stock company "Internet Exchange"MSK-IX" | no | no |
| 193.232.177.50 | 193.232.177.0/24 | AS43832 | RIPN-NS5-RU-MSK Join-stock company "Internet Exchange"MSK-IX" | no | no |
| 193.232.230.48 | 193.232.230.0/24 | AS42139 | RIPN-RU-NSK Join-stock company "Internet Exchange"MSK-IX" | no | no |
| 193.232.231.51 | 193.232.231.0/24 | AS42728 | RIPN-RU-EKT Join-stock company "Internet Exchange"MSK-IX" | no | no |
| 193.232.236.51 | 193.232.236.0/24 | AS47445 | RIPN-RU-RND Join-stock company "Internet Exchange"MSK-IX" | no | no |
| 193.232.240.49 | 193.232.240.0/24 | AS42139 | RIPN-RU-NSK Join-stock company "Internet Exchange"MSK-IX" | no | no |

**(b) AS206385 rows, window_dec_allru.tsv**: resolver_ip values (excluding unrecorded ['', '127.0.0.2']):

| resolver_ip | prefix | origin ASN | holder | in NSDI egress (exact) | NSDI /24 |
|---|---|---|---|---|---|
| 194.85.108.60 | 194.85.108.0/24 | AS43832 | RIPN-NS5-RU-MSK Join-stock company "Internet Exchange"MSK-IX" | no | no |
| 194.85.108.61 | 194.85.108.0/24 | AS43832 | RIPN-NS5-RU-MSK Join-stock company "Internet Exchange"MSK-IX" | no | no |

### Reading

NSDI egress origin ASNs seen now: {AS13335, AS15169, AS50629}; dnslook.MSK_IX_ASNS (the December NXDOMAIN egress ASNs): {AS42139, AS42728, AS43832, AS47445}; intersection {}.

Exact-IP overlap of the NSDI egress set with (a) the December NXDOMAIN resolver_ip values: 0 of 20 (none); by /24: 1 of 20 (74.125.114.156). 16 of the 20 NXDOMAIN resolver IPs have an MSK-IX origin ASN; the ones outside the two /24s seen here sit in sibling 193.232.x / 194.226.75.x /24s of AS42139, AS43832, AS42728 and AS47445.

Exact-IP overlap with (b) the AS206385 resolver_ip values: 0 of 2 (none); by /24: 0 of 2. The AS206385 values (194.85.108.60, 194.85.108.61) are in a /24 this run never saw as NSDI egress.


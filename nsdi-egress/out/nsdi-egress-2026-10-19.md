# NSDI resolver egress, active measurement from this Mac, 2026-10-19

**Caveat.** This measures the egress of 195.208.4.1 / 195.208.5.1 as of 2026-10-19 (October 2026). The comparison in section 4 with the December 2025 window TSVs assumes the egress pool was stable between December 2025 and this run; nothing here checks that. It is also one vantage point: the NSDI addresses are anycast, so the node (and egress pool) reached from this machine in Germany need not be the one Russian probes reached in December; an egress IP in a sibling /24 with the same MSK-IX origin ASN is consistent with another node of the same service, not evidence against it.

Run from public IP 92.209.188.249 (origin AS3209, VODANET Vodafone GmbH); system resolver 2a02:908:2:b::1. 430 queries sent (cap 500); one attempt each, 5 s timeout; >= 1 s between queries to one target; whoami rounds 15 s apart (20 rounds for NSDI, 10 for the controls), ground-truth rounds 5 s apart (5 rounds). Per-query records: `nsdi-egress-2026-10-19-queries.tsv`. Registry data: RIPEstat via T6/ripestat.py.

## 1. Control table: resolver -> egress IPs -> origin ASN -> holder

Expected: 8.8.8.8 -> AS15169, 1.1.1.1 -> AS13335, system resolver -> this machine's ISP ASN (AS3209 from the public IP above).

### google (8.8.8.8): 40 whoami queries, NOERROR x40, median RTT 41 ms, 27 distinct egress IPs, origin ASNs {AS15169} -> expected AS15169: **PASS**

| egress IP | queries | prefix | origin ASN | holder |
|---|---|---|---|---|
| 172.217.33.210 | 4 | 172.217.0.0/16 | AS15169 | GOOGLE - Google LLC |
| 172.253.1.212 | 3 | 172.253.0.0/16 | AS15169 | GOOGLE - Google LLC |
| 172.253.237.157 | 3 | 172.253.0.0/16 | AS15169 | GOOGLE - Google LLC |
| 172.217.33.213 | 3 | 172.217.0.0/16 | AS15169 | GOOGLE - Google LLC |
| 172.253.14.18 | 2 | 172.253.0.0/16 | AS15169 | GOOGLE - Google LLC |
| 172.253.1.220 | 2 | 172.253.0.0/16 | AS15169 | GOOGLE - Google LLC |
| 172.217.33.218 | 2 | 172.217.0.0/16 | AS15169 | GOOGLE - Google LLC |
| 172.253.1.218 | 2 | 172.253.0.0/16 | AS15169 | GOOGLE - Google LLC |
| 2a00:1450:4001:c07::127 | 1 | 2a00:1450:4001::/48 | AS15169 | GOOGLE - Google LLC |
| 172.217.34.25 | 1 | 172.217.0.0/16 | AS15169 | GOOGLE - Google LLC |
| 172.217.33.151 | 1 | 172.217.0.0/16 | AS15169 | GOOGLE - Google LLC |
| 172.253.1.217 | 1 | 172.253.0.0/16 | AS15169 | GOOGLE - Google LLC |
| 172.253.14.28 | 1 | 172.253.0.0/16 | AS15169 | GOOGLE - Google LLC |
| 172.253.1.214 | 1 | 172.253.0.0/16 | AS15169 | GOOGLE - Google LLC |
| 2a00:1450:4001:c07::122 | 1 | 2a00:1450:4001::/48 | AS15169 | GOOGLE - Google LLC |
| 172.217.33.146 | 1 | 172.217.0.0/16 | AS15169 | GOOGLE - Google LLC |
| 172.253.14.25 | 1 | 172.253.0.0/16 | AS15169 | GOOGLE - Google LLC |
| 172.217.33.149 | 1 | 172.217.0.0/16 | AS15169 | GOOGLE - Google LLC |
| 172.253.1.210 | 1 | 172.253.0.0/16 | AS15169 | GOOGLE - Google LLC |
| 172.217.34.24 | 1 | 172.217.0.0/16 | AS15169 | GOOGLE - Google LLC |
| 172.217.34.29 | 1 | 172.217.0.0/16 | AS15169 | GOOGLE - Google LLC |
| 172.253.1.215 | 1 | 172.253.0.0/16 | AS15169 | GOOGLE - Google LLC |
| 2a00:1450:4001:c07::123 | 1 | 2a00:1450:4001::/48 | AS15169 | GOOGLE - Google LLC |
| 172.217.33.219 | 1 | 172.217.0.0/16 | AS15169 | GOOGLE - Google LLC |
| 172.217.33.153 | 1 | 172.217.0.0/16 | AS15169 | GOOGLE - Google LLC |
| 172.217.33.150 | 1 | 172.217.0.0/16 | AS15169 | GOOGLE - Google LLC |
| 172.217.33.214 | 1 | 172.217.0.0/16 | AS15169 | GOOGLE - Google LLC |

### cloudflare (1.1.1.1): 40 whoami queries, NOERROR x40, median RTT 42 ms, 28 distinct egress IPs, origin ASNs {AS13335} -> expected AS13335: **PASS**

| egress IP | queries | prefix | origin ASN | holder |
|---|---|---|---|---|
| 172.70.245.120 | 3 | 172.70.245.0/24 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. |
| 162.158.93.149 | 3 | 162.158.93.0/24 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. |
| 172.69.149.145 | 2 | 172.69.149.0/24 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. |
| 162.158.93.77 | 2 | 162.158.93.0/24 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. |
| 2400:cb00:928:1024::ac47:a864 | 2 | 2400:cb00:928::/48 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. |
| 2400:cb00:931:1024::ac44:143e | 2 | 2400:cb00:931::/48 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. |
| 2400:cb00:933:1024::ac46:f464 | 2 | 2400:cb00:933::/48 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. |
| 172.69.149.215 | 2 | 172.69.149.0/24 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. |
| 172.70.244.99 | 2 | 172.70.244.0/24 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. |
| 2400:cb00:636:1024::a29e:5d96 | 1 | 2400:cb00:636::/48 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. |
| 162.158.85.5 | 1 | 162.158.84.0/22 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. |
| 2400:cb00:470:1024::ac46:f197 | 1 | 2400:cb00:470::/48 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. |
| 162.158.93.75 | 1 | 162.158.93.0/24 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. |
| 172.68.194.27 | 1 | 172.68.194.0/24 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. |
| 172.70.244.38 | 1 | 172.70.244.0/24 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. |
| 104.23.240.37 | 1 | 104.23.240.0/24 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. |
| 172.68.20.39 | 1 | 172.68.20.0/24 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. |
| 172.68.192.52 | 1 | 172.68.192.0/24 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. |
| 172.68.192.54 | 1 | 172.68.192.0/24 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. |
| 162.158.109.82 | 1 | 162.158.109.0/24 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. |
| 172.69.113.38 | 1 | 172.69.113.0/24 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. |
| 2400:cb00:608:1024::ac47:f577 | 1 | 2400:cb00:608::/48 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. |
| 172.68.24.103 | 1 | 172.68.24.0/24 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. |
| 104.22.123.205 | 1 | 104.22.123.0/24 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. |
| 172.70.241.151 | 1 | 172.70.241.0/24 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. |
| 172.69.149.144 | 1 | 172.69.149.0/24 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. |
| 172.68.24.43 | 1 | 172.68.24.0/24 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. |
| 172.71.168.100 | 1 | 172.71.168.0/24 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. |

### system (2a02:908:2:b::1): 40 whoami queries, NOERROR x40, median RTT 39 ms, 8 distinct egress IPs, origin ASNs {AS3209} -> expected AS3209: **PASS**

| egress IP | queries | prefix | origin ASN | holder |
|---|---|---|---|---|
| 139.7.84.15 | 6 | 139.7.0.0/16 | AS3209 | VODANET Vodafone GmbH |
| 2a01:860:4:100d::7:0 | 6 | 2a01:860::/32 | AS3209 | VODANET Vodafone GmbH |
| 139.7.84.17 | 6 | 139.7.0.0/16 | AS3209 | VODANET Vodafone GmbH |
| 139.7.84.12 | 6 | 139.7.0.0/16 | AS3209 | VODANET Vodafone GmbH |
| 139.7.84.14 | 6 | 139.7.0.0/16 | AS3209 | VODANET Vodafone GmbH |
| 2a01:860:4:100d::a:0 | 5 | 2a01:860::/32 | AS3209 | VODANET Vodafone GmbH |
| 139.7.84.16 | 3 | 139.7.0.0/16 | AS3209 | VODANET Vodafone GmbH |
| 139.7.84.13 | 2 | 139.7.0.0/16 | AS3209 | VODANET Vodafone GmbH |

**Controls: PASS, the method is sound.**

## 2. NSDI table: egress per address, UDP and TCP separately

### a.res-nsdi.ru (195.208.4.1) over UDP: 40 whoami queries (20 per qname), NOERROR x40, median RTT 99 ms; **7 distinct egress IPs**; origin ASNs {AS42139} (all in dnslook.MSK_IX_ASNS)

| egress IP | queries | prefix | origin ASN | holder |
|---|---|---|---|---|
| 193.232.230.50 | 10 | 193.232.230.0/24 | AS42139 | RIPN-RU-NSK Join-stock company "Internet Exchange"MSK-IX" |
| 193.232.230.51 | 10 | 193.232.230.0/24 | AS42139 | RIPN-RU-NSK Join-stock company "Internet Exchange"MSK-IX" |
| 193.232.230.48 | 9 | 193.232.230.0/24 | AS42139 | RIPN-RU-NSK Join-stock company "Internet Exchange"MSK-IX" |
| 2001:67c:1211:2000:1000::104 | 5 | 2001:67c:1211::/48 | AS42139 | RIPN-RU-NSK Join-stock company "Internet Exchange"MSK-IX" |
| 193.232.230.49 | 4 | 193.232.230.0/24 | AS42139 | RIPN-RU-NSK Join-stock company "Internet Exchange"MSK-IX" |
| 2001:67c:1211:2000:1000::103 | 1 | 2001:67c:1211::/48 | AS42139 | RIPN-RU-NSK Join-stock company "Internet Exchange"MSK-IX" |
| 2001:67c:1211:2000:1000::101 | 1 | 2001:67c:1211::/48 | AS42139 | RIPN-RU-NSK Join-stock company "Internet Exchange"MSK-IX" |

### a.res-nsdi.ru (195.208.4.1) over TCP: 40 whoami queries (20 per qname), NOERROR x40, median RTT 202 ms; **8 distinct egress IPs**; origin ASNs {AS42139} (all in dnslook.MSK_IX_ASNS)

| egress IP | queries | prefix | origin ASN | holder |
|---|---|---|---|---|
| 193.232.230.48 | 9 | 193.232.230.0/24 | AS42139 | RIPN-RU-NSK Join-stock company "Internet Exchange"MSK-IX" |
| 193.232.230.51 | 7 | 193.232.230.0/24 | AS42139 | RIPN-RU-NSK Join-stock company "Internet Exchange"MSK-IX" |
| 193.232.230.49 | 7 | 193.232.230.0/24 | AS42139 | RIPN-RU-NSK Join-stock company "Internet Exchange"MSK-IX" |
| 193.232.230.50 | 7 | 193.232.230.0/24 | AS42139 | RIPN-RU-NSK Join-stock company "Internet Exchange"MSK-IX" |
| 2001:67c:1211:2000:1000::104 | 4 | 2001:67c:1211::/48 | AS42139 | RIPN-RU-NSK Join-stock company "Internet Exchange"MSK-IX" |
| 2001:67c:1211:2000:1000::101 | 2 | 2001:67c:1211::/48 | AS42139 | RIPN-RU-NSK Join-stock company "Internet Exchange"MSK-IX" |
| 2001:67c:1211:2000:1000::102 | 2 | 2001:67c:1211::/48 | AS42139 | RIPN-RU-NSK Join-stock company "Internet Exchange"MSK-IX" |
| 2001:67c:1211:2000:1000::103 | 2 | 2001:67c:1211::/48 | AS42139 | RIPN-RU-NSK Join-stock company "Internet Exchange"MSK-IX" |

Egress sets by qname for a.res-nsdi.ru: akamai.net 4 IPs, akahelp.net 8 IPs, 4 in common.

### b.res-nsdi.ru (195.208.5.1) over UDP: 40 whoami queries (20 per qname), NOERROR x40, median RTT 55 ms; **4 distinct egress IPs**; origin ASNs {AS43832} (all in dnslook.MSK_IX_ASNS)

| egress IP | queries | prefix | origin ASN | holder |
|---|---|---|---|---|
| 193.232.177.48 | 18 | 193.232.177.0/24 | AS43832 | RIPN-NS5-RU-MSK Join-stock company "Internet Exchange"MSK-IX" |
| 193.232.177.49 | 16 | 193.232.177.0/24 | AS43832 | RIPN-NS5-RU-MSK Join-stock company "Internet Exchange"MSK-IX" |
| 2a0c:a9c7:177:2000:1000::102 | 3 | 2a0c:a9c7:177::/48 | AS43832 | RIPN-NS5-RU-MSK Join-stock company "Internet Exchange"MSK-IX" |
| 2a0c:a9c7:177:2000:1000::101 | 3 | 2a0c:a9c7:177::/48 | AS43832 | RIPN-NS5-RU-MSK Join-stock company "Internet Exchange"MSK-IX" |

### b.res-nsdi.ru (195.208.5.1) over TCP: 40 whoami queries (20 per qname), NOERROR x40, median RTT 115 ms; **4 distinct egress IPs**; origin ASNs {AS43832} (all in dnslook.MSK_IX_ASNS)

| egress IP | queries | prefix | origin ASN | holder |
|---|---|---|---|---|
| 193.232.177.49 | 20 | 193.232.177.0/24 | AS43832 | RIPN-NS5-RU-MSK Join-stock company "Internet Exchange"MSK-IX" |
| 193.232.177.48 | 12 | 193.232.177.0/24 | AS43832 | RIPN-NS5-RU-MSK Join-stock company "Internet Exchange"MSK-IX" |
| 2a0c:a9c7:177:2000:1000::102 | 4 | 2a0c:a9c7:177::/48 | AS43832 | RIPN-NS5-RU-MSK Join-stock company "Internet Exchange"MSK-IX" |
| 2a0c:a9c7:177:2000:1000::101 | 4 | 2a0c:a9c7:177::/48 | AS43832 | RIPN-NS5-RU-MSK Join-stock company "Internet Exchange"MSK-IX" |

Egress sets by qname for b.res-nsdi.ru: akamai.net 2 IPs, akahelp.net 4 IPs, 2 in common.

## 3. Ground-truth table: rcode per (resolver, qname, transport)

5 queries per cell. example.com and ya.ru are negative controls and must answer; www.youtube.com is the current ground truth for the DNS stage.

| resolver | qname | transport | rcodes / errors | distinct A answers | median RTT ms |
|---|---|---|---|---|---|
| a.res-nsdi.ru (195.208.4.1) | www.youtube.com | udp | NXDOMAIN x5 | 0:  | 106 |
| a.res-nsdi.ru (195.208.4.1) | www.youtube.com | tcp | NXDOMAIN x5 | 0:  | 198 |
| a.res-nsdi.ru (195.208.4.1) | example.com | udp | NOERROR x5 | 2: 8.47.69.0, 8.6.112.0 | 106 |
| a.res-nsdi.ru (195.208.4.1) | example.com | tcp | NOERROR x5 | 2: 8.47.69.0, 8.6.112.0 | 200 |
| a.res-nsdi.ru (195.208.4.1) | ya.ru | udp | NOERROR x5 | 3: 5.255.255.242, 77.88.44.242, 77.88.55.242 | 99 |
| a.res-nsdi.ru (195.208.4.1) | ya.ru | tcp | NOERROR x5 | 3: 5.255.255.242, 77.88.44.242, 77.88.55.242 | 199 |
| b.res-nsdi.ru (195.208.5.1) | www.youtube.com | udp | NXDOMAIN x5 | 0:  | 55 |
| b.res-nsdi.ru (195.208.5.1) | www.youtube.com | tcp | NXDOMAIN x5 | 0:  | 120 |
| b.res-nsdi.ru (195.208.5.1) | example.com | udp | NOERROR x4, timeout x1 | 2: 8.47.69.0, 8.6.112.0 | 58 |
| b.res-nsdi.ru (195.208.5.1) | example.com | tcp | NOERROR x5 | 2: 8.47.69.0, 8.6.112.0 | 125 |
| b.res-nsdi.ru (195.208.5.1) | ya.ru | udp | NOERROR x5 | 3: 5.255.255.242, 77.88.44.242, 77.88.55.242 | 65 |
| b.res-nsdi.ru (195.208.5.1) | ya.ru | tcp | NOERROR x5 | 3: 5.255.255.242, 77.88.44.242, 77.88.55.242 | 132 |
| google (8.8.8.8) | www.youtube.com | udp | NOERROR x5 | 8: 142.251.150.4, 142.251.151.4, 142.251.152.4, 142.251.153.4, 142.251.154.4, 142.251.155.4 ... | 28 |
| google (8.8.8.8) | www.youtube.com | tcp | NOERROR x5 | 8: 142.251.150.4, 142.251.151.4, 142.251.152.4, 142.251.153.4, 142.251.154.4, 142.251.155.4 ... | 46 |
| google (8.8.8.8) | example.com | udp | NOERROR x5 | 2: 104.20.23.154, 172.66.147.243 | 18 |
| google (8.8.8.8) | example.com | tcp | NOERROR x5 | 2: 104.20.23.154, 172.66.147.243 | 52 |
| google (8.8.8.8) | ya.ru | udp | NOERROR x5 | 3: 5.255.255.242, 77.88.44.242, 77.88.55.242 | 25 |
| google (8.8.8.8) | ya.ru | tcp | NOERROR x5 | 3: 5.255.255.242, 77.88.44.242, 77.88.55.242 | 44 |
| cloudflare (1.1.1.1) | www.youtube.com | udp | NOERROR x5 | 8: 142.251.150.4, 142.251.151.4, 142.251.152.4, 142.251.153.4, 142.251.154.4, 142.251.155.4 ... | 22 |
| cloudflare (1.1.1.1) | www.youtube.com | tcp | NOERROR x5 | 8: 142.251.150.4, 142.251.151.4, 142.251.152.4, 142.251.153.4, 142.251.154.4, 142.251.155.4 ... | 47 |
| cloudflare (1.1.1.1) | example.com | udp | NOERROR x5 | 2: 104.20.23.154, 172.66.147.243 | 18 |
| cloudflare (1.1.1.1) | example.com | tcp | NOERROR x5 | 2: 104.20.23.154, 172.66.147.243 | 53 |
| cloudflare (1.1.1.1) | ya.ru | udp | NOERROR x5 | 3: 5.255.255.242, 77.88.44.242, 77.88.55.242 | 17 |
| cloudflare (1.1.1.1) | ya.ru | tcp | NOERROR x5 | 3: 5.255.255.242, 77.88.44.242, 77.88.55.242 | 43 |
| system (2a02:908:2:b::1) | www.youtube.com | udp | NOERROR x5 | 8: 142.251.150.4, 142.251.151.4, 142.251.152.4, 142.251.153.4, 142.251.154.4, 142.251.155.4 ... | 18 |
| system (2a02:908:2:b::1) | www.youtube.com | tcp | NOERROR x5 | 8: 142.251.150.4, 142.251.151.4, 142.251.152.4, 142.251.153.4, 142.251.154.4, 142.251.155.4 ... | 50 |
| system (2a02:908:2:b::1) | example.com | udp | NOERROR x5 | 2: 104.20.23.154, 172.66.147.243 | 18 |
| system (2a02:908:2:b::1) | example.com | tcp | NOERROR x5 | 2: 104.20.23.154, 172.66.147.243 | 48 |
| system (2a02:908:2:b::1) | ya.ru | udp | NOERROR x5 | 3: 5.255.255.242, 77.88.44.242, 77.88.55.242 | 19 |
| system (2a02:908:2:b::1) | ya.ru | tcp | NOERROR x5 | 3: 5.255.255.242, 77.88.44.242, 77.88.55.242 | 46 |

Negative controls: no cell failed outright. Partial loss: b.res-nsdi.ru example.com udp answered 4 of 5 (timeout x1).

## 4. Comparison with the December 2025 window TSVs (read through dnslook.read_rows)

NSDI egress set = union of the egress IPs in section 2 (both addresses, both transports, both qnames), measured 2026-10-19; see the caveat at the top.

NSDI egress IPs (12): 193.232.177.48, 193.232.177.49, 193.232.230.48, 193.232.230.49, 193.232.230.50, 193.232.230.51, 2001:67c:1211:2000:1000::101, 2001:67c:1211:2000:1000::102, 2001:67c:1211:2000:1000::103, 2001:67c:1211:2000:1000::104, 2a0c:a9c7:177:2000:1000::101, 2a0c:a9c7:177:2000:1000::102

NSDI egress /24s (2): 193.232.177.0/24, 193.232.230.0/24

| set | file | rows | distinct resolver_ip | overlap with NSDI egress (exact IP) | overlap by /24 |
|---|---|---|---|---|---|
| (a) NXDOMAIN rows | window_dec_onset.tsv | 50 | 20 | 3 | 5 |
| (b) AS206385 rows | window_dec_onset.tsv | 0 | 0 | 0 | 0 |
| (a) NXDOMAIN rows | window_dec_allru.tsv | 34 | 13 | 2 | 3 |
| (b) AS206385 rows | window_dec_allru.tsv | 72 | 2 | 0 | 0 |
| (a) NXDOMAIN rows | both files (union) | | 20 | 3 | 5 |
| (b) AS206385 rows | both files (union) | | 2 | 0 | 0 |

**(a) NXDOMAIN rows, window_dec_onset.tsv**: resolver_ip values (excluding unrecorded ['', '127.0.0.2']):

| resolver_ip | prefix | origin ASN | holder | in NSDI egress (exact) | NSDI /24 |
|---|---|---|---|---|---|
| 74.125.74.21 | 74.125.72.0/22 | AS15169 | GOOGLE - Google LLC | no | no |
| 74.125.114.156 | 74.125.0.0/16 | AS15169 | GOOGLE - Google LLC | no | no |
| 172.68.9.62 | 172.68.9.0/24 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. | no | no |
| 193.232.93.51 | 193.232.93.0/24 | AS43832 | RIPN-NS5-RU-MSK Join-stock company "Internet Exchange"MSK-IX" | no | no |
| 193.232.139.57 | 193.232.139.0/24 | AS47445 | RIPN-RU-RND Join-stock company "Internet Exchange"MSK-IX" | no | no |
| 193.232.160.48 | 193.232.160.0/24 | AS43832 | RIPN-NS5-RU-MSK Join-stock company "Internet Exchange"MSK-IX" | no | no |
| 193.232.160.51 | 193.232.160.0/24 | AS43832 | RIPN-NS5-RU-MSK Join-stock company "Internet Exchange"MSK-IX" | no | no |
| 193.232.177.49 | 193.232.177.0/24 | AS43832 | RIPN-NS5-RU-MSK Join-stock company "Internet Exchange"MSK-IX" | yes | yes |
| 193.232.177.50 | 193.232.177.0/24 | AS43832 | RIPN-NS5-RU-MSK Join-stock company "Internet Exchange"MSK-IX" | no | yes |
| 193.232.177.51 | 193.232.177.0/24 | AS43832 | RIPN-NS5-RU-MSK Join-stock company "Internet Exchange"MSK-IX" | no | yes |
| 193.232.230.48 | 193.232.230.0/24 | AS42139 | RIPN-RU-NSK Join-stock company "Internet Exchange"MSK-IX" | yes | yes |
| 193.232.230.51 | 193.232.230.0/24 | AS42139 | RIPN-RU-NSK Join-stock company "Internet Exchange"MSK-IX" | yes | yes |
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
| 74.125.114.156 | 74.125.0.0/16 | AS15169 | GOOGLE - Google LLC | no | no |
| 172.68.9.62 | 172.68.9.0/24 | AS13335 | CLOUDFLARENET - Cloudflare, Inc. | no | no |
| 193.232.93.51 | 193.232.93.0/24 | AS43832 | RIPN-NS5-RU-MSK Join-stock company "Internet Exchange"MSK-IX" | no | no |
| 193.232.139.57 | 193.232.139.0/24 | AS47445 | RIPN-RU-RND Join-stock company "Internet Exchange"MSK-IX" | no | no |
| 193.232.160.48 | 193.232.160.0/24 | AS43832 | RIPN-NS5-RU-MSK Join-stock company "Internet Exchange"MSK-IX" | no | no |
| 193.232.160.51 | 193.232.160.0/24 | AS43832 | RIPN-NS5-RU-MSK Join-stock company "Internet Exchange"MSK-IX" | no | no |
| 193.232.177.49 | 193.232.177.0/24 | AS43832 | RIPN-NS5-RU-MSK Join-stock company "Internet Exchange"MSK-IX" | yes | yes |
| 193.232.177.50 | 193.232.177.0/24 | AS43832 | RIPN-NS5-RU-MSK Join-stock company "Internet Exchange"MSK-IX" | no | yes |
| 193.232.230.48 | 193.232.230.0/24 | AS42139 | RIPN-RU-NSK Join-stock company "Internet Exchange"MSK-IX" | yes | yes |
| 193.232.231.51 | 193.232.231.0/24 | AS42728 | RIPN-RU-EKT Join-stock company "Internet Exchange"MSK-IX" | no | no |
| 193.232.236.51 | 193.232.236.0/24 | AS47445 | RIPN-RU-RND Join-stock company "Internet Exchange"MSK-IX" | no | no |
| 193.232.240.49 | 193.232.240.0/24 | AS42139 | RIPN-RU-NSK Join-stock company "Internet Exchange"MSK-IX" | no | no |

**(b) AS206385 rows, window_dec_allru.tsv**: resolver_ip values (excluding unrecorded ['', '127.0.0.2']):

| resolver_ip | prefix | origin ASN | holder | in NSDI egress (exact) | NSDI /24 |
|---|---|---|---|---|---|
| 194.85.108.60 | 194.85.108.0/24 | AS43832 | RIPN-NS5-RU-MSK Join-stock company "Internet Exchange"MSK-IX" | no | no |
| 194.85.108.61 | 194.85.108.0/24 | AS43832 | RIPN-NS5-RU-MSK Join-stock company "Internet Exchange"MSK-IX" | no | no |

### Reading

NSDI egress origin ASNs seen now: {AS42139, AS43832}; dnslook.MSK_IX_ASNS (the December NXDOMAIN egress ASNs): {AS42139, AS42728, AS43832, AS47445}; intersection {AS42139, AS43832}.

Exact-IP overlap of the NSDI egress set with (a) the December NXDOMAIN resolver_ip values: 3 of 20 (193.232.177.49, 193.232.230.48, 193.232.230.51); by /24: 5 of 20 (193.232.177.49, 193.232.177.50, 193.232.177.51, 193.232.230.48, 193.232.230.51). 16 of the 20 NXDOMAIN resolver IPs have an MSK-IX origin ASN; the ones outside the two /24s seen here sit in sibling 193.232.x / 194.226.75.x /24s of AS42139, AS43832, AS42728 and AS47445.

Exact-IP overlap with (b) the AS206385 resolver_ip values: 0 of 2 (none); by /24: 0 of 2. The AS206385 values (194.85.108.60, 194.85.108.61) are in a /24 this run never saw as NSDI egress.


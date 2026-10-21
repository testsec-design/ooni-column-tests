# 4 May 2026 МГТС whitelist report: Atlas plain HTTP and TLS built-ins and OONI

5 Oct 2026. This applies the instruments that detected 14 Jan 2025 (`jan14-2025-dissection-2026-10-05.md`) to the ntc.party report 24403 #23: МГТС GPON in Moscow on whitelists at 11:00 MSK (08:00 UTC) on 4 May 2026, with "the same yesterday about the same time" (#24). Pulled through the browser pane.

## Atlas

The probe set is the current registry's RU probes. Window: 1–6 May 2026.

- **12027 (plain HTTP to http://193.0.6.141, hourly):** 76,219 RU results in 576 15-minute bins. The median failure share is 0.017, the 95th percentile 0.043 and the 99th percentile 0.051. No bin is above 0.08. **All 8 МГТС (AS25513) probes** (27180, 50520, 51972, 1002176, 1003804, 1007226, 1011052, 1014636) returned one result per hour on 4 May 06:00–12:00 UTC, and every one succeeded. Over 1–6 May the МГТС probes failed 1 time in 1,175 results. The 3 May 06:00–10:00 and 2 May 11:00–16:00 windows look the same (RU 0–8 failures per bin of about 120–145 results). DE control on 4 May 06:00–12:00: 2% failures per hour.
- **14001/14002 (TLS to RIPE, 12-hourly):** 12,709 RU results. Excluding the recurring alert-40 failures, no hour in 1–6 May has a failure share above 0.08. **МГТС probe 51972 completed both TLS handshakes at 08:29 and 08:31 UTC on 4 May**, inside the reported window. Every МГТС TLS result on 2–4 May succeeded.

This extends the 24 Sept `selective` test (6 МГТС probes, controller-disconnection windows, same result) to every RU probe and to fixed clock windows.

## OONI web_connectivity

RU, 1–4 May 2026, 05:00–10:00 UTC (the pull stopped at 4 May 10:00 UTC). AS25513's anomaly share per 15-minute bin swings between 0.1 and 1.0 on every day, because it depends on which probe and test list happen to run, so the raw share cannot be read directly. Restricted to the 1,108 inputs with at least 20 RU measurements and an anomaly share below 0.05 on 1–3 May ("normally reachable"):

| AS25513, hour (UTC) | n | anomaly | failure |
|---|---|---|---|
| 3 May 07 / 08 / 09 | 76 / 184 / 33 | 2 / 4 / 2 | 12 / 11 / 8 |
| **4 May 07 / 08 / 09** | 137 / 166 / 83 | 4 / 8 / 1 | 12 / 9 / 8 |

All RU, same inputs: an anomaly share of 0.024–0.030 on 4 May 06:00–10:00 UTC. Twelve raw AS25513 HTTPS measurements sampled from 08:03–08:40 UTC on 4 May came from four reports. Nine completed the TLS handshake (wordpress.org, gitlab.com, bitly.com, dl.google.com, googleusercontent.com, bl.ink and others). Three timed out (prq.se twice, valence.community).

## Reading

At the reported time, none of the МГТС vantage points in Atlas (8 probes) or OONI (at least 4 measurement sessions) showed whitelist behaviour. New TCP connections to foreign hosts completed, plain HTTP and TLS both. Under the 14 Jan 2025 signature, the same instruments would have shown failure shares near 0.9.

What this supports: within these vantage points, the 4 May report is not corroborated. It does not exclude a whitelist on part of МГТС's network. The report is a single first-hand post about GPON. The Atlas probes' access technology is unknown, and the OONI probes have no network_type annotation. Other explanations are a regime applied to some subscriber segments, a misattributed local fault, or a false report.

**Consequence for `atlas-mgts-whitelist-prediction-2026-09-24.md`:** the slow controller reconnection of the МГТС probes after 08:03 UTC cannot be read as whitelist enforcement. The same probes were opening new HTTP and TLS connections to RIPE hosts at the same time. Something specific to the controller connection (the SSH tunnel to ctr-dub-*, or the controller address block) has to explain it.

## Not done

The OONI pull for 4 May 10:00 UTC to 6 May. Radar (needs the token). IODA (Mac).

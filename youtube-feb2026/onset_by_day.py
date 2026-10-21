#!/usr/bin/env python3
"""When did RU web_connectivity measurements of a domain start showing DNS-stage blocking?
Day-by-day counts from the OONI aggregation API only (no raw fetches).

    ../../venv/bin/python onset_by_day.py [--domain www.youtube.com] [--since 2025-12-01]
                                          [--until 2026-03-01] [--pause 3] [--no-daily-asn]

Calls /api/v1/aggregation with test_name=web_connectivity, probe_cc=RU, domain=<domain>,
axis_x=measurement_start_day, time_grain=day, for 1 Dec 2025 .. 28 Feb 2026 (until is exclusive):
  1. no axis_y                      -> all RU probes, one row per day
  2. axis_y=probe_asn               -> one row per day x probe_asn (distinct ASNs measuring /
                                       with an anomaly, per day)
  3. axis_y=blocking_type           -> one row per day x blocking_type (dns, tcp_ip, http-*, ...)
  4. axis_y=blocking_type with a probe_asn filter, for each ASN in ASNS (the three that returned
     NXDOMAIN for www.youtube.com in check_youtube_dns.py) -> days with blocking_type=dns per ASN.
     Only attempted when call 3 is accepted.
  5. one call per day with axis_x=probe_asn, axis_y=blocking_type -> distinct ASNs with at least
     one blocking_type=dns measurement that day (the API takes two axes only, so a day x asn x
     blocking_type table needs one call per day). Skipped with --no-daily-asn.
If the API refuses axis_y=blocking_type (4xx) the script says so and goes on without it. If call 1
returns no rows (the domain is not in the RU test list for the range) the script stops there.

Responses are saved under raw_api/aggregation/<domain>_<name>.json (existing files are reused,
so a re-run costs nothing). Tables go to stdout and out/onset_by_day_<domain>.tsv, one long table:
  series  day  measurement_count  anomaly_count  confirmed_count  failure_count  anomaly_share
          dns_count  dns_share  n_asn  n_asn_anomaly  n_asn_dns
where series is "all" or one of ASNS; dns_count/dns_share come from the blocking_type calls (empty
when that axis is unavailable); n_asn* are filled for the "all" series only (distinct probe_asn
values with measurement_count > 0 / anomaly_count > 0 / a blocking_type=dns row that day).

Caveats: (1) classification: the aggregation API counts the pipeline's anomaly flag (and, with
axis_y=blocking_type, the pipeline's blocking_type classification), not dns_nxdomain_error
specifically; blocking_type "dns" covers every DNS-stage inconsistency the pipeline flags
(NXDOMAIN, bogus answers, DNS timeouts ...), so a rise in it is the onset of DNS-stage anomalies,
not of NXDOMAIN as such. (2) volume: per-ASN daily counts are small (often 1-2 measurements, one
probe), and the RU probe population changes over the range, so shares move with who measured.

Job: day series from the aggregation API only; no TSVs. API client: T0/pull_api.Client (serial,
waits out 429s, logs rate-limit headers), via dnslook, which points its ratelimit.csv at raw_api/ here.

Also here, for inventory.py: the aggregation API filters `domain` exactly, so "any label of
googlevideo.com" needs a listing first. inputs_matching() makes one call with axis_x=input (no
time axis) over a range, derives each input's host with domain_of(), and keeps the inputs whose
host domain_matches() a pattern (the domain itself or any subdomain of it). RESPONSES records
(name, status, seconds) of every call fetch() actually sent, for the per-response report.
"""
from __future__ import annotations

import argparse
import collections
import csv
import datetime as dt
import json
import time
import urllib.parse

from dnslook import AGG, API, OUT, pull_api

ASNS = ["AS208397", "AS29182", "AS12714"]     # NXDOMAIN probes for www.youtube.com in check_youtube_dns.py
COUNTS = ["measurement_count", "anomaly_count", "confirmed_count", "failure_count"]


class Refused(Exception):
    pass


RESPONSES: list[tuple[str, int, float]] = []   # (name, status, seconds) of every call fetch() sent


def domain_of(inp: str) -> str:
    """The host of an input URL, lower-cased (no port); '' when the input has no host."""
    try:
        return (urllib.parse.urlsplit(inp or "").hostname or "").lower()
    except ValueError:
        return ""


def domain_matches(host: str, pattern: str) -> bool:
    """pattern 'googlevideo.com' matches googlevideo.com and every subdomain (rr1---sn-x.googlevideo.com,
    redirector.googlevideo.com); 'www.youtube.com' matches only itself and its subdomains. Exact otherwise."""
    pattern = pattern.lower().rstrip(".")
    return host == pattern or host.endswith("." + pattern)


def inputs_matching(c: pull_api.Client, since: str, until: str, patterns: list[str]) -> dict[str, list[dict]]:
    """One aggregation call, RU web_connectivity, axis_x=input, since..until (no time axis), cached as
    raw_api/aggregation/inputs_<since>_<until>.json -> pattern -> rows (input, measurement_count,
    anomaly_count, ...) whose host domain_matches() the pattern, largest measurement_count first."""
    rows = fetch(c, f"inputs_{since}_{until}",
                 {"test_name": "web_connectivity", "probe_cc": "RU", "since": since, "until": until,
                  "axis_x": "input"})["result"]
    out: dict[str, list[dict]] = {p: [] for p in patterns}
    for r in rows:
        h = domain_of(r.get("input") or "")
        for p in patterns:
            if h and domain_matches(h, p):
                out[p].append(r)
    for p in out:
        out[p].sort(key=lambda r: -int(r.get("measurement_count") or 0))
    return out


def fetch(c: pull_api.Client, name: str, params: dict) -> dict:
    """One aggregation call, cached as raw_api/aggregation/<name>.json. Raises Refused on a 4xx
    (the Client retries 4xx eight times before raising; we want to know, not to retry)."""
    p = AGG / f"{name}.json"
    if p.exists():
        return json.loads(p.read_text())
    gap = c.pause - (time.time() - c.last)                           # keep the Client's spacing
    if gap > 0:
        time.sleep(gap)
    c.last = t0 = time.time()
    r = c.s.get(f"{API}/aggregation", params=params, timeout=300)   # probe once for a 4xx
    secs = round(time.time() - t0, 2)
    now = dt.datetime.now(dt.timezone.utc).replace(tzinfo=None).isoformat(timespec="seconds")
    c.w.writerow([now, "/aggregation",
                  json.dumps(params), r.status_code, secs, *[r.headers.get(h, "") for h in pull_api.RL_HEADERS]])
    c.log.flush()
    RESPONSES.append((name, r.status_code, secs))
    if 400 <= r.status_code < 500 and r.status_code != 429:
        raise Refused(f"HTTP {r.status_code}: {r.text[:300]}")
    j = r.json() if r.status_code == 200 else c.get(f"{API}/aggregation", params)
    pull_api.save_json(p, j)
    return j


def day_key(row: dict) -> str:
    return str(row["measurement_start_day"])[:10]


def table(rows: list[dict], key=None) -> dict:
    """day -> dict of summed counts, optionally restricted/grouped by key(row)."""
    out: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for r in rows:
        if key is not None and not key(r):
            continue
        for k in COUNTS:
            out[day_key(r)][k] += int(r.get(k) or 0)
    return out


def distinct_asns(asn_rows: list[dict]) -> dict:
    """day -> (ASNs with measurement_count > 0, ASNs with anomaly_count > 0) from the day x probe_asn call."""
    out = collections.defaultdict(lambda: (set(), set()))
    for r in asn_rows:
        d = day_key(r)
        if int(r.get("measurement_count") or 0):
            out[d][0].add(r.get("probe_asn"))
        if int(r.get("anomaly_count") or 0):
            out[d][1].add(r.get("probe_asn"))
    return out


def days_between(since: str, until: str) -> list[str]:
    d0, d1 = dt.date.fromisoformat(since), dt.date.fromisoformat(until)
    return [(d0 + dt.timedelta(days=i)).isoformat() for i in range((d1 - d0).days)]


def share(a: int, n: int) -> str:
    return f"{a / n:.3f}" if n else ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--domain", default="www.youtube.com")
    ap.add_argument("--since", default="2025-12-01")
    ap.add_argument("--until", default="2026-03-01", help="exclusive")
    ap.add_argument("--pause", type=float, default=3.0)
    ap.add_argument("--no-daily-asn", action="store_true", help="skip the one-call-per-day asn x blocking_type pull")
    a = ap.parse_args()
    c = pull_api.Client(a.pause, 3600.0, 6 * 3600.0)
    base = {"test_name": "web_connectivity", "probe_cc": "RU", "domain": a.domain,
            "axis_x": "measurement_start_day", "time_grain": "day"}
    span = {"since": a.since, "until": a.until}
    dom = a.domain

    all_rows = fetch(c, f"{dom}_all", {**base, **span})["result"]
    if not all_rows:
        print(f"{dom}: no RU web_connectivity measurements between {a.since} and {a.until}; nothing to tabulate")
        return
    asn_rows = fetch(c, f"{dom}_probe_asn", {**base, **span, "axis_y": "probe_asn"})["result"]
    bt_ok, bt_rows, bt_asn = True, [], {}
    try:
        bt_rows = fetch(c, f"{dom}_blocking_type", {**base, **span, "axis_y": "blocking_type"})["result"]
        for asn in ASNS:
            bt_asn[asn] = fetch(c, f"{dom}_blocking_type_{asn}",
                                {**base, **span, "axis_y": "blocking_type", "probe_asn": asn})["result"]
    except Refused as e:
        bt_ok = False
        print(f"\naxis_y=blocking_type REFUSED by the API ({e}); dns counts not available\n", flush=True)

    days = sorted({day_key(r) for r in all_rows})
    is_dns = lambda r: (r.get("blocking_type") or "") == "dns"      # noqa: E731
    dns_asns: dict[str, set] = {}
    if bt_ok and not a.no_daily_asn:
        for d in days_between(a.since, a.until):
            rows = fetch(c, f"{dom}_asn_x_bt_{d}",
                         {"test_name": "web_connectivity", "probe_cc": "RU", "domain": dom, "since": d,
                          "until": (dt.date.fromisoformat(d) + dt.timedelta(days=1)).isoformat(),
                          "axis_x": "probe_asn", "axis_y": "blocking_type"})["result"]
            dns_asns[d] = {r.get("probe_asn") for r in rows if is_dns(r) and int(r.get("measurement_count") or 0)}
    nasn = distinct_asns(asn_rows)

    series = {"all": (table(all_rows), table(bt_rows, is_dns) if bt_ok else {})}
    for asn in ASNS:
        n = int(asn[2:])                                          # API returns probe_asn as a bare int
        series[asn] = (table(asn_rows, lambda r, n=n: int(r.get("probe_asn") or 0) == n),
                       table(bt_asn.get(asn, []), is_dns) if bt_ok else {})
    if bt_ok:
        kinds = collections.Counter(r.get("blocking_type") or "" for r in bt_rows)
        print("blocking_type values seen (rows):", dict(kinds))

    OUT.mkdir(exist_ok=True)
    hdr = ["series", "day", *COUNTS, "anomaly_share", "dns_count", "dns_share", "n_asn", "n_asn_anomaly", "n_asn_dns"]
    out_path = OUT / f"onset_by_day_{dom}.tsv"
    with open(out_path, "w", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(hdr)
        for name, (t, tdns) in series.items():
            print(f"\n== {name}  (RU web_connectivity, domain={dom}, {a.since}..{a.until})")
            print("\t".join(hdr[1:]))
            for d in days:
                r = t.get(d, collections.Counter())
                n, an = r["measurement_count"], r["anomaly_count"]
                dn = tdns.get(d, collections.Counter())["measurement_count"] if bt_ok else ""
                row = [name, d, *[r[k] for k in COUNTS], share(an, n), dn, share(dn, n) if bt_ok else ""]
                if name == "all":
                    row += [len(nasn[d][0]), len(nasn[d][1]), len(dns_asns[d]) if d in dns_asns else ""]
                else:
                    row += ["", "", ""]
                w.writerow(row)
                if name == "all" or n:
                    print("\t".join(str(x) for x in row[1:]))
    print(f"\nwritten {out_path}; responses in {AGG}; "
          f"blocking_type axis {'accepted' if bt_ok else 'refused'}; "
          f"daily asn x blocking_type {'pulled' if dns_asns else 'skipped'}")


if __name__ == "__main__":
    main()

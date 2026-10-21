#!/usr/bin/env python3
"""A look at the DNS stage of OONI web_connectivity for a domain in Russia around a reported
change (first use: youtube.com, 10 Feb 2026 NSDI removal; expected symptom NXDOMAIN from the ISP
resolver). Question: does the record carry enough about the DNS stage to name the mechanism?

    ../../venv/bin/python check_youtube_dns.py [--domain youtube.com]
    ../../venv/bin/python check_youtube_dns.py --domain www.youtube.com \
        --window dec_before 2025-12-19T00:00 2025-12-22T00:00 \
        --window dec_onset  2025-12-22T00:00 2025-12-25T00:00 \
        --no-cap --asn AS12714 --asn AS208397 ... [--asn-day 2025-12-22]

Pull: RU web_connectivity measurements whose input domain is --domain, listed via the OONI
measurements API for each window (default: A = 11-13 Feb 2026, post-removal; B = 3-5 Feb,
quiet-day comparison). Up to PER_ASN measurements per probe_asn per window across every ASN that
appears, or every listed measurement with --no-cap. --asn (repeatable) keeps only those ASNs
(the section-6 runs used --asn --no-cap; before 19 Oct 2026 --asn implied --no-cap).
The raw measurement of each is fetched with WORKERS threads and cached in raw/<measurement_uid>.json.

Output: out/<domain>/window_<name>.tsv (one row per measurement x DNS query; a measurement without
queries still gets one row), a per-ASN summary on stdout, and raw `queries` blocks printed verbatim.
Without --asn: two blocks (first window: one with dns_nxdomain_error if any; second window: the
first one). With --asn: an onset report per ASN across the windows in the order given (counts,
reports, software, query failures, answers of inconsistent-but-answered queries, last measurement
without NXDOMAIN / first with, resolver_ip set with origin ASN and RIPEstat holder, whether the
resolver egress changed at onset) and the queries blocks of the last pre-onset and first at-onset
measurement for three ASNs (most measurements, one mobile, one fixed-line). --asn-day DAY
(repeatable) prints how many distinct ASNs tested the domain that day and how many had a
dns-classified measurement, from the cached aggregation response of onset_by_day.py or a fresh call.

What this does NOT do: no bootstrap or intervals, no stage classification (T0/extract_stages.py
is not used), no hygiene (dedup by report), no resolver-ownership lookup beyond the registry
holder, no claim about the mechanism. A pull of a few dozen measurements is a look at what the
record contains, not evidence. Mobile/fixed-line is T6/common.py's MOBILE_ASNS (registry names).

Job: fetch and write the window TSVs (columns, paths and the outcome/egress rules the readers use
are in dnslook.py). API client: T0/pull_api.Client is the repo's OONI API client (waits out HTTP
429, retries other errors, logs every response's rate-limit headers). It is serial by design; here
the listing uses one Client with its usual pause and the raw fetches use one Client per worker
thread with pause 0. dnslook points pull_api.OUT at this folder, so ratelimit.csv lands in raw_api/. Observed 19 Oct 2026: one raw_measurement fetch costs ~30-90 of a
~4000-unit budget whose readings are inconsistent; 616 fetches with 8 workers saw no 429.
Registry lookups: T6/ripestat.py (cached under T6/raw_api/ripestat/).
"""
from __future__ import annotations

import argparse
import collections
import csv
import datetime as dt
import ipaddress
import json
import pathlib
import threading
from concurrent.futures import ThreadPoolExecutor

from dnslook import AGG, API, NSDI, NXDOMAIN, OUT, RAW, TSV_COLS, pull_api, queries_json, raw, ripestat, tsv_path  # sets sys.path
from common import MOBILE_ASNS  # noqa: E402  (T6 code, imported, not modified)

WORKERS = 8                               # concurrent raw-measurement fetches
PER_ASN = 10                              # measurements per probe_asn per window (no --asn)
DOMAIN = "youtube.com"
WINDOWS = [("A", "2026-02-11T00:00:00", "2026-02-13T00:00:00"),     # post-removal
           ("B", "2026-02-03T00:00:00", "2026-02-05T00:00:00")]     # quiet-day comparison
NSDI_NETS = [ipaddress.ip_network(n) for n in NSDI]

_tl = threading.local()


def list_measurements(c: pull_api.Client, domain: str, since: str, until: str) -> list[dict]:
    url, params, rows = f"{API}/measurements", {"test_name": "web_connectivity", "probe_cc": "RU", "domain": domain,
                                                 "since": since, "until": until, "limit": 1000}, []
    while url:
        j = c.get(url, params)
        params = None
        rows += j["results"]
        url = j["metadata"].get("next_url") if j["results"] else None
    return rows


def pick_per_asn(rows: list[dict], n: int | None, asns: set[str] | None) -> list[dict]:
    """By start time: the first n measurements of every probe_asn that appears (n None = all),
    restricted to asns when given."""
    by = collections.defaultdict(list)
    for r in sorted(rows, key=lambda r: r["measurement_start_time"]):
        if asns is not None and r["probe_asn"] not in asns:
            continue
        if n is None or len(by[r["probe_asn"]]) < n:
            by[r["probe_asn"]].append(r)
    return [r for asn in sorted(by) for r in by[asn]]


def fetch_raw(uid: str) -> dict:
    p = RAW / f"{uid}.json"
    if p.exists():
        return raw(uid)
    if not hasattr(_tl, "client"):
        _tl.client = pull_api.Client(pause=0.0, wait_429=600.0, max_wait=3600.0)
    m = _tl.client.get(f"{API}/raw_measurement", {"measurement_uid": uid})
    pull_api.save_json(p, m)
    return m


def answers_of(q: dict) -> tuple[str, str]:
    ans = q.get("answers") or []
    return (";".join(str(a.get("answer_type")) for a in ans),
            ";".join(a.get("ipv4") or a.get("ipv6") or "" for a in ans))


def query_rows(window: str, m: dict) -> list[dict]:
    tk = m.get("test_keys") or {}
    ctl = (tk.get("control") or {}).get("dns") or {}
    base = {"window": window, "measurement_uid": m.get("measurement_uid", ""), "report_id": m.get("report_id"),
            "measurement_start_time": m.get("measurement_start_time"), "probe_asn": m.get("probe_asn"),
            "probe_network_name": m.get("probe_network_name"), "resolver_ip": m.get("resolver_ip"),
            "resolver_asn": m.get("resolver_asn"), "test_version": m.get("test_version"),
            "software_name": m.get("software_name"), "software_version": m.get("software_version"),
            "network_type": (m.get("annotations") or {}).get("network_type"),
            "input": m.get("input"),
            "dns_consistency": tk.get("dns_consistency"), "dns_experiment_failure": tk.get("dns_experiment_failure"),
            "blocking": tk.get("blocking"), "accessible": tk.get("accessible"),
            "control_dns_failure": ctl.get("failure"), "control_dns_addrs": ";".join(ctl.get("addrs") or [])}
    qs = tk.get("queries") or []
    if not qs:
        return [{**base, "q_index": "", "n_answers": ""}]
    rows = []
    for i, q in enumerate(qs):
        types, addrs = answers_of(q)
        rows.append({**base, "q_index": i, "hostname": q.get("hostname"), "query_type": q.get("query_type"),
                     "engine": q.get("engine"), "resolver_hostname": q.get("resolver_hostname"),
                     "resolver_address": q.get("resolver_address"), "failure": q.get("failure"),
                     "n_answers": len(q.get("answers") or []), "answer_types": types, "answers": addrs})
    return rows


def write_tsv(path: pathlib.Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, TSV_COLS, delimiter="\t", restval="")
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if v is None else v) for k, v in r.items()})


def in_nsdi(ip: str) -> bool:
    try:
        return any(ipaddress.ip_address(ip.split(":")[0] if ip.count(":") == 1 else ip) in n for n in NSDI_NETS)
    except ValueError:
        return False


def summarize(window: str, rows: list[dict]) -> None:
    by_asn = collections.defaultdict(list)
    for r in rows:
        by_asn[r["probe_asn"]].append(r)
    print(f"\n== window {window}: {len({r['measurement_uid'] for r in rows})} measurements, "
          f"{sum(1 for r in rows if r['q_index'] != '')} queries, {len(by_asn)} ASNs")
    for asn in sorted(by_asn):
        rs = by_asn[asn]
        ms = {r["measurement_uid"]: r for r in rs}.values()
        qs = [r for r in rs if r["q_index"] != ""]
        fail = collections.Counter("nxdomain" if r["failure"] == NXDOMAIN else "other" if r["failure"] else "none"
                                   for r in qs)
        cons = collections.Counter(str(r["dns_consistency"]) for r in ms)
        resolvers = sorted({r["resolver_ip"] for r in ms if r["resolver_ip"]}
                           | {r["resolver_address"] for r in qs if r.get("resolver_address")})
        nsdi = [ip for ip in resolvers if in_nsdi(ip)]
        print(f"  {asn} {next(iter(ms))['probe_network_name']}: {len(ms)} measurements, {len(qs)} queries")
        print(f"     query failure: nxdomain={fail['nxdomain']} other={fail['other']} none={fail['none']}")
        print(f"     dns_consistency: {dict(cons)}")
        print(f"     resolver IPs (top-level resolver_ip + queries.resolver_address): {resolvers}")
        print(f"     NSDI 195.208.4/5.0/24: {'YES ' + str(nsdi) if nsdi else 'no'}")
        other = collections.Counter(r["failure"] for r in qs if r["failure"] and r["failure"] != NXDOMAIN)
        if other:
            print(f"     other failures: {dict(other)}")


def print_queries(label: str, m: dict) -> None:
    print(f"\n== raw test_keys.queries, {label}: uid={m.get('measurement_uid', '?')} report_id={m.get('report_id')} "
          f"asn={m.get('probe_asn')} start={m.get('measurement_start_time')} resolver_ip={m.get('resolver_ip')} "
          f"test_version={m.get('test_version')} software={m.get('software_name')} {m.get('software_version')}")
    print(queries_json(m))


# ---- onset report (--asn) --------------------------------------------------------------------

def queries(m: dict) -> list[dict]:
    return (m.get("test_keys") or {}).get("queries") or []


def has_nx(m: dict) -> bool:
    return any(q.get("failure") == NXDOMAIN for q in queries(m))


def resolver_label(ip: str) -> str:
    if not ip:
        return "(empty)"
    asns, _ = ripestat.origin(ip)
    holders = [ripestat.holder(a)[0] for a in asns]
    return f"{ip} -> {'/'.join('AS' + a for a in asns) or 'AS?'} {' / '.join(holders)[:70]}"


def onset_report(domain: str, windows: list[tuple[str, str, str]], raws: dict[str, list[dict]], asns: list[str]):
    """Per window x ASN counts, then per ASN the NXDOMAIN onset bracket and resolver egress, then
    verbatim queries blocks for three ASNs."""
    print(f"\n#### onset report: domain={domain}, windows={[w[0] for w in windows]}, ASNs={len(asns)}")
    by: dict[str, list[dict]] = collections.defaultdict(list)          # asn -> all measurements, time order
    for name, _, _ in windows:
        for m in raws[name]:
            m["_window"] = name
            by[m["probe_asn"]].append(m)
    for asn in by:
        by[asn].sort(key=lambda m: m["measurement_start_time"])

    print("\n-- per window x ASN: measurements, distinct report_ids, software_versions; query failures "
          "nxdomain/other/none; answers of queries with no failure in an inconsistent measurement")
    for name, _, _ in windows:
        for asn in asns:
            ms = [m for m in by.get(asn, []) if m["_window"] == name]
            if not ms:
                print(f"  {name} {asn}: 0 measurements")
                continue
            qs = [q for m in ms for q in queries(m)]
            fail = collections.Counter("nxdomain" if q.get("failure") == NXDOMAIN else "other" if q.get("failure")
                                       else "none" for q in qs)
            other = collections.Counter(q.get("failure") for q in qs if q.get("failure") and q.get("failure") != NXDOMAIN)
            incons_answers = collections.Counter()
            for m in ms:
                if (m.get("test_keys") or {}).get("dns_consistency") == "inconsistent":
                    for q in queries(m):
                        if not q.get("failure"):
                            incons_answers[answers_of(q)[1] or "(no answers)"] += 1
            sw = collections.Counter(f"{m.get('software_name')} {m.get('software_version')}" for m in ms)
            print(f"  {name} {asn} {ms[0].get('probe_network_name')}: {len(ms)} msm, "
                  f"{len({m.get('report_id') for m in ms})} reports, software {dict(sw)}")
            print(f"       queries nxdomain={fail['nxdomain']} other={fail['other']} none={fail['none']}"
                  + (f"  other={dict(other)}" if other else ""))
            if incons_answers:
                print(f"       inconsistent-but-answered: {dict(incons_answers)}")

    print("\n-- per ASN: onset bracket and resolver egress (resolver_ip -> origin ASN, RIPEstat holder)")
    for asn in asns:
        ms = by.get(asn, [])
        if not ms:
            print(f"  {asn}: no measurements in these windows")
            continue
        first_nx = next((m for m in ms if has_nx(m)), None)
        last_pre = None
        if first_nx is not None:
            i = ms.index(first_nx)
            last_pre = next((m for m in reversed(ms[:i]) if not has_nx(m)), None)
            after_ok = sum(1 for m in ms[i:] if not has_nx(m))
        resolvers = collections.Counter(m.get("resolver_ip") or "" for m in ms)
        print(f"  {asn} {ms[0].get('probe_network_name')} ({'mobile' if asn[2:] in MOBILE_ASNS else 'fixed-line'}): "
              f"{len(ms)} msm {ms[0]['measurement_start_time']} .. {ms[-1]['measurement_start_time']}")
        if first_nx is None:
            print(f"       no dns_nxdomain_error in any query")
        else:
            print(f"       last without NXDOMAIN: {last_pre['measurement_start_time'] + ' ' + last_pre['_window'] + ' uid=' + last_pre['measurement_uid'] if last_pre else '(none before)'}")
            print(f"       first with NXDOMAIN:   {first_nx['measurement_start_time']} {first_nx['_window']} uid={first_nx['measurement_uid']}")
            print(f"       measurements without NXDOMAIN after the first: {after_ok} of {len(ms) - ms.index(first_nx)}")
            if last_pre is not None:
                a, b = last_pre.get("resolver_ip") or "", first_nx.get("resolver_ip") or ""
                same_ip = a == b
                same_as = ripestat.origin(a)[0] == ripestat.origin(b)[0] if a and b else False
                print(f"       resolver egress changed at onset? {'no (same IP)' if same_ip else 'IP changed, same origin ASN' if same_as else 'yes'}: "
                      f"{a or '(empty)'} -> {b or '(empty)'}")
        for ip, n in resolvers.most_common():
            print(f"       resolver_ip x{n}: {resolver_label(ip)}")
        m0 = ms[0]
        print(f"       resolver_asn as recorded by OONI: {sorted({m.get('resolver_asn') for m in ms})}")

    # verbatim blocks: most measurements, one mobile, one fixed-line
    ranked = sorted((a for a in asns if by.get(a)), key=lambda a: -len(by[a]))
    chosen = []
    if ranked:
        chosen.append(ranked[0])
    mob = next((a for a in ranked if a[2:] in MOBILE_ASNS and a not in chosen), None)
    fix = next((a for a in ranked if a[2:] not in MOBILE_ASNS and a not in chosen), None)
    print(f"\n-- verbatim queries blocks: most measurements={ranked[0] if ranked else None}, "
          f"mobile={mob or 'none among these ASNs'}, fixed-line={fix or 'none'}")
    for a in [x for x in (ranked[0] if ranked else None, mob, fix) if x]:
        ms = by[a]
        first_nx = next((m for m in ms if has_nx(m)), None)
        if first_nx is None:
            print_queries(f"{a} (no NXDOMAIN; first measurement)", ms[0])
            continue
        i = ms.index(first_nx)
        last_pre = next((m for m in reversed(ms[:i]) if not has_nx(m)), None)
        if last_pre is not None:
            print_queries(f"{a} last pre-onset", last_pre)
        else:
            print(f"\n== {a}: no measurement without NXDOMAIN before the first with it")
        print_queries(f"{a} first at-onset", first_nx)


def asn_day(c: pull_api.Client, domain: str, day: str) -> None:
    """Distinct ASNs testing the domain on `day` and distinct ASNs with a dns-classified
    measurement, from the cached onset_by_day.py response or a fresh aggregation call."""
    p = AGG / f"{domain}_asn_x_bt_{day}.json"
    if p.exists():
        rows = json.loads(p.read_text())["result"]
    else:
        until = (dt.date.fromisoformat(day) + dt.timedelta(days=1)).isoformat()
        rows = c.get(f"{API}/aggregation", {"test_name": "web_connectivity", "probe_cc": "RU", "domain": domain,
                                            "since": day, "until": until, "axis_x": "probe_asn",
                                            "axis_y": "blocking_type"})["result"]
        pull_api.save_json(p, rows and {"result": rows} or {"result": []})
    testing = {r["probe_asn"] for r in rows if r.get("measurement_count")}
    dns = {r["probe_asn"] for r in rows if r.get("measurement_count") and (r.get("blocking_type") or "") == "dns"}
    print(f"\n-- {domain} on {day}: {len(testing)} distinct ASNs tested it; {len(dns)} had a dns-classified "
          f"measurement: {sorted('AS' + str(a) for a in dns)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--domain", default=DOMAIN)
    ap.add_argument("--asn", action="append", help="probe_asn filter, repeatable (ASnnn); adds the onset report")
    ap.add_argument("--no-cap", action="store_true", help="fetch every listed measurement instead of PER_ASN per ASN")
    ap.add_argument("--window", action="append", nargs=3, metavar=("NAME", "SINCE", "UNTIL"),
                    help="repeatable; default: A 11-13 Feb 2026, B 3-5 Feb 2026")
    ap.add_argument("--asn-day", action="append", help="print distinct ASNs testing / dns-classified on this day")
    a = ap.parse_args()
    windows = [tuple(w) for w in a.window] if a.window else WINDOWS
    asns = [x if x.startswith("AS") else "AS" + x for x in a.asn] if a.asn else None
    lister = pull_api.Client(pause=3.0, wait_429=600.0, max_wait=3600.0)   # built first: creates ratelimit.csv
    raws: dict[str, list[dict]] = {}
    for w, since, until in windows:
        listed = list_measurements(lister, a.domain, since, until)
        picked = pick_per_asn(listed, None if a.no_cap else PER_ASN, set(asns) if asns else None)
        print(f"window {w} ({since}..{until}): listed {len(listed)} measurements from "
              f"{len({r['probe_asn'] for r in listed})} ASNs, fetching {len(picked)}", flush=True)
        with ThreadPoolExecutor(WORKERS) as ex:
            ms = list(ex.map(fetch_raw, [r["measurement_uid"] for r in picked]))
        for r, m in zip(picked, ms):
            m["measurement_uid"] = r["measurement_uid"]      # raw records do not carry their own uid
        raws[w] = ms
        rows = [row for m in ms for row in query_rows(w, m)]
        write_tsv(tsv_path(a.domain, w), rows)
        summarize(w, rows)

    if asns:
        onset_report(a.domain, windows, raws, asns)
    else:
        w0, w1 = windows[0][0], windows[-1][0]
        nx = [m for m in raws[w0] if has_nx(m)]
        if nx:
            print_queries(f"window {w0}, first measurement with a dns_nxdomain_error query", nx[0])
        elif raws[w0]:
            print_queries(f"window {w0} (no measurement has a dns_nxdomain_error query), first measurement", raws[w0][0])
        if raws[w1]:
            print_queries(f"window {w1}, first measurement", raws[w1][0])
    for d in a.asn_day or []:
        asn_day(lister, a.domain, d)


if __name__ == "__main__":
    main()

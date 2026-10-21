#!/usr/bin/env python3
"""Within-ASN mixture of NXDOMAIN and answered measurements for www.youtube.com, RU, 19-24 Dec
2025 (section 6 of notes-2026-10-19.md reports that most of the 19 onset ASNs keep returning
answered measurements after their first NXDOMAIN). No API calls: reads
out/www.youtube.com/window_dec_before.tsv and window_dec_onset.tsv (written by
check_youtube_dns.py, which carries network_type from annotations) and raw/<uid>.json only for
the verbatim queries blocks of AS42893.

    ../../venv/bin/python mixture_dec.py > out/mixture_dec.md

Outcome letters from dnslook.outcome(): N nxdomain, D android_no_data, F other_failure, A
answered_consistent, I answered_inconsistent. "Answered" below means A or I.

Probe key: (probe_asn, software_name, software_version, network_type, resolver_ip); the number of
distinct report_ids per key says where one key is likely several probes. A key is pure_nx /
pure_answered / pure_d / pure_f when all its measurements have that outcome class, otherwise
mixed. Flips: changes of outcome letter between consecutive measurements of a key in time
order; the gaps are hours between consecutive flip times. "Differ" (resolver_ip, resolver_asn
as recorded by OONI, network_type): yes when the set of non-empty values over the ASN's N
measurements and the set over its answered measurements share no value, no when they share
one, n/a when either side has no non-empty value. Tables only; no interpretation.
"""
from __future__ import annotations

import collections
import statistics

import dnslook
from dnslook import ANSWERED

DOMAIN = "www.youtube.com"
ASNS = dnslook.ONSET_ASNS[DOMAIN]
DAYS = ["2025-12-22", "2025-12-23", "2025-12-24"]


def key(m: dict) -> tuple:
    return (m["asn"], m["software"], m["network_type"], m["resolver_ip"])


def key_class(letters: str) -> str:
    s = set(letters)
    if s == {"N"}:
        return "pure_nx"
    if s <= ANSWERED:
        return "pure_answered"
    if s == {"D"}:
        return "pure_d"
    if s == {"F"}:
        return "pure_f"
    return "mixed"


def flips(ms: list[dict]) -> tuple[int, str, str]:
    """number of flips and median / max hours between consecutive flip times ('-' when < 2 flips)."""
    times = [ms[i]["t"] for i in range(1, len(ms)) if ms[i]["letter"] != ms[i - 1]["letter"]]
    gaps = [(b - a).total_seconds() / 3600 for a, b in zip(times, times[1:])]
    if not gaps:
        return len(times), "-", "-"
    return len(times), f"{statistics.median(gaps):.1f}", f"{max(gaps):.1f}"


def differ(ms: list[dict], field: str) -> str:
    a = {m[field] for m in ms if m["letter"] == "N" and m[field]}          # empty values count as absent
    b = {m[field] for m in ms if m["letter"] in ANSWERED and m[field]}
    if not a or not b:
        return "n/a"
    return "yes" if a.isdisjoint(b) else "no"


def per_asn(asn: str, ms: list[dict]) -> dict:
    keys: dict[tuple, list[dict]] = collections.defaultdict(list)
    for m in ms:
        keys[key(m)].append(m)
    classes = collections.Counter(key_class("".join(m["letter"] for m in v)) for v in keys.values())
    print(f"\n#### {asn}: {len(ms)} measurements, {len({m['report_id'] for m in ms})} report_ids, {len(keys)} keys "
          f"(pure_nx {classes['pure_nx']}, pure_answered {classes['pure_answered']}, pure_d {classes['pure_d']}, "
          f"pure_f {classes['pure_f']}, mixed {classes['mixed']})")
    print("\n| software | network_type | resolver_ip | resolver_asn | msm | report_ids | outcomes (time order) | class |")
    print("|---|---|---|---|---|---|---|---|")
    for k, v in sorted(keys.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        letters = "".join(m["letter"] for m in v)
        print(f"| {k[1]} | {k[2] or '(none)'} | {k[3] or '(empty)'} | {v[0]['resolver_asn']} | {len(v)} | "
              f"{len({m['report_id'] for m in v})} | {letters if len(letters) <= 60 else letters[:57] + '...'} | "
              f"{key_class(letters)} |")
    mixed = [(k, v) for k, v in keys.items() if key_class("".join(m["letter"] for m in v)) == "mixed"]
    if mixed:
        print("\nMixed keys: outcomes in time order, flips, median / max hours between consecutive flips")
        print("\n| key | outcomes | flips | median h | max h |")
        print("|---|---|---|---|---|")
        for k, v in mixed:
            n, med, mx = flips(v)
            print(f"| {k[1]}, {k[2] or '(none)'}, {k[3] or '(empty)'} | {''.join(m['letter'] for m in v)} | {n} | {med} | {mx} |")
    frac = []
    for d in DAYS:
        dm = [m for m in ms if m["t"].date().isoformat() == d]
        ans = sum(1 for m in dm if m["letter"] in ANSWERED)
        frac.append(f"{ans}/{len(dm)}" + (f" ({ans / len(dm):.2f})" if dm else ""))
    print(f"\nAnswered fraction per day (22, 23, 24 Dec): {' | '.join(frac)}")
    d_ip, d_asn, d_net = differ(ms, "resolver_ip"), differ(ms, "resolver_asn"), differ(ms, "network_type")
    print(f"NX vs answered measurements differ in resolver_ip: {d_ip}; resolver_asn: {d_asn}; network_type: {d_net}")
    nets = {m["network_type"] for m in ms}
    return {"asn": asn, "msm": len(ms), "keys": len(keys), **classes, "d_ip": d_ip, "d_asn": d_asn, "d_net": d_net,
            "frac": frac, "wifi_and_mobile": "wifi" in nets and "mobile" in nets}


def as42893(ms: list[dict]) -> None:
    print("\n#### AS42893: measurements in time order")
    print("\n| start (UTC) | window | resolver_ip | resolver_asn | outcome | software | network_type | report_id |")
    print("|---|---|---|---|---|---|---|---|")
    for m in ms:
        print(f"| {m['t']} | {m['window']} | {m['resolver_ip']} | {m['resolver_asn']} | {m['letter']} | {m['software']} | "
              f"{m['network_type'] or '(none)'} | {m['report_id']} |")
    for m in ms:
        if m["letter"] == "N":
            print(f"\nVerbatim test_keys.queries of NXDOMAIN measurement uid={m['uid']} start={m['t']} "
                  f"resolver_ip={m['resolver_ip']} software={m['software']}:\n")
            print("```json\n" + dnslook.queries_json(dnslook.raw(m["uid"])) + "\n```")


def main():
    ms = dnslook.measurements(dnslook.read_rows(DOMAIN, dnslook.ONSET_WINDOWS[DOMAIN]))
    by_asn = collections.defaultdict(list)
    for m in ms:
        by_asn[m["asn"]].append(m)
    none_cons = sum(1 for m in ms if m["letter"] == "I" and m["dns_consistency"] != "inconsistent")
    print(f"{len(ms)} measurements from {len(by_asn)} ASNs in the two windows; answered measurements with "
          f"dns_consistency neither consistent nor inconsistent (counted as I): {none_cons}; measurements with "
          f"network_type: {sum(1 for m in ms if m['network_type'])}")
    rows = [per_asn(asn, by_asn.get(asn, [])) for asn in ASNS if by_asn.get(asn)]
    print("\n#### Summary across the 19 ASNs")
    print("\n| ASN | msm | keys | pure_nx | pure_answered | pure_d | pure_f | mixed | answered 22 / 23 / 24 Dec | "
          "differ: resolver_ip | resolver_asn | network_type | wifi+mobile |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        print(f"| {r['asn']} | {r['msm']} | {r['keys']} | {r.get('pure_nx', 0)} | {r.get('pure_answered', 0)} | "
              f"{r.get('pure_d', 0)} | {r.get('pure_f', 0)} | {r.get('mixed', 0)} | {' / '.join(r['frac'])} | "
              f"{r['d_ip']} | {r['d_asn']} | {r['d_net']} | {'yes' if r['wifi_and_mobile'] else 'no'} |")
    both = [r["asn"] for r in rows if r["wifi_and_mobile"]]
    print(f"\nASNs carrying both wifi and mobile measurements: {len(both)} of {len(rows)} ({', '.join(both) or 'none'})")
    as42893(by_asn.get("AS42893", []))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Step 1 of the substitution test (notes section 10): which YouTube-related inputs are in the RU
web_connectivity test list between two dates, and with what volume. Aggregation API only, no raw fetches.

    ../../venv/bin/python inventory.py [--since 2025-11-01] [--until 2026-02-01] [--pause 3]
                                       [--max-per-pattern 10]

Calls: (1) one listing with axis_x=input over the range (onset_by_day.inputs_matching; the API filters
domain/input exactly, so "any label of googlevideo.com" is matched client-side on the listing);
(2) for each matching input, at most --max-per-pattern per pattern by total volume, one call with
input=<url>, axis_x=measurement_start_day, time_grain=day, axis_y=probe_asn -> per-day measurement
counts and distinct probe ASNs (onset_by_day.table / distinct_asns). Responses are cached under
raw_api/aggregation/ with the range in the file name (a re-run costs nothing).

Prints, as markdown: (1) the inputs found per pattern with totals over the range; (2) one day table
per input (day, measurements, anomalies, distinct ASNs); (3) a side-by-side day table of
"measurements/ASNs" with one column per input; (4) the per-response report: every aggregation
response the run sent (status, seconds), the 429 count. Writes out/inventory_<since>_<until>.tsv
(long: pattern, input, day, measurement_count, anomaly_count, n_asn).
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import re

import onset_by_day as ob
from dnslook import AGG, OUT, pull_api

PATTERNS = ["googlevideo.com", "i.ytimg.com", "yt3.ggpht.com", "m.youtube.com", "youtu.be",
            "www.youtube.com", "www.google.com"]          # www.google.com: the non-throttled control


def slug(inp: str) -> str:
    """A file-name-safe tag for an input URL: sanitised text plus a short hash (inputs differ in punctuation)."""
    txt = re.sub(r"[^A-Za-z0-9.-]+", "_", inp)[:60].strip("_")
    return f"{txt}_{hashlib.sha1(inp.encode()).hexdigest()[:8]}"


def short(inp: str) -> str:
    return inp if len(inp) <= 44 else inp[:41] + "..."


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="2025-11-01")
    ap.add_argument("--until", default="2026-02-01", help="exclusive")
    ap.add_argument("--pause", type=float, default=3.0)
    ap.add_argument("--max-per-pattern", type=int, default=10,
                    help="per-day calls for at most this many inputs per pattern (largest total first)")
    a = ap.parse_args()
    c = pull_api.Client(a.pause, 3600.0, 6 * 3600.0)
    rl_path = pull_api.OUT / "ratelimit.csv"
    rl_before = sum(1 for _ in open(rl_path)) if rl_path.exists() else 0

    found = ob.inputs_matching(c, a.since, a.until, PATTERNS)
    print(f"RU web_connectivity inputs matching the patterns, {a.since}..{a.until} (exclusive), "
          f"from one axis_x=input listing\n")
    print("| pattern | input | measurements | anomalies | per-day pulled |")
    print("|---|---|---|---|---|")
    chosen: list[tuple[str, str]] = []
    for p in PATTERNS:
        rows = found[p]
        if not rows:
            print(f"| {p} | (no input) | 0 | 0 | |")
            continue
        for i, r in enumerate(rows):
            pulled = i < a.max_per_pattern
            if pulled:
                chosen.append((p, r["input"]))
            print(f"| {p} | {r['input']} | {int(r.get('measurement_count') or 0)} | "
                  f"{int(r.get('anomaly_count') or 0)} | {'yes' if pulled else 'no (beyond cap)'} |")

    # per-input day series
    series: dict[str, tuple[dict, dict]] = {}
    for p, inp in chosen:
        rows = ob.fetch(c, f"input_{slug(inp)}_probe_asn_{a.since}_{a.until}",
                        {"test_name": "web_connectivity", "probe_cc": "RU", "input": inp,
                         "since": a.since, "until": a.until,
                         "axis_x": "measurement_start_day", "time_grain": "day", "axis_y": "probe_asn"})["result"]
        series[inp] = (ob.table(rows), ob.distinct_asns(rows))
    days = ob.days_between(a.since, a.until)

    OUT.mkdir(exist_ok=True)
    out_path = OUT / f"inventory_{a.since}_{a.until}.tsv"
    with open(out_path, "w", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["pattern", "input", "day", "measurement_count", "anomaly_count", "n_asn"])
        for p, inp in chosen:
            t, nasn = series[inp]
            asns_all = set().union(*[nasn[d][0] for d in days if d in nasn]) if nasn else set()
            n_days = sum(1 for d in days if t.get(d, collections.Counter())["measurement_count"])
            print(f"\n### {p}: `{inp}` — {sum(t[d]['measurement_count'] for d in t)} measurements on "
                  f"{n_days} of {len(days)} days, {len(asns_all)} distinct probe ASNs over the range\n")
            print("| day | measurements | anomalies | distinct ASNs |")
            print("|---|---|---|---|")
            for d in days:
                r = t.get(d, collections.Counter())
                n = len(nasn[d][0]) if d in nasn else 0
                w.writerow([p, inp, d, r["measurement_count"], r["anomaly_count"], n])
                if r["measurement_count"]:
                    print(f"| {d} | {r['measurement_count']} | {r['anomaly_count']} | {n} |")

    if chosen:
        print(f"\n### Side by side: measurements/distinct ASNs per day, {a.since}..{a.until}\n")
        heads = [short(inp) for _, inp in chosen]
        print("| day | " + " | ".join(heads) + " |")
        print("|---|" + "---|" * len(heads))
        for d in days:
            cells = []
            for _, inp in chosen:
                t, nasn = series[inp]
                n = t.get(d, collections.Counter())["measurement_count"]
                cells.append(f"{n}/{len(nasn[d][0]) if d in nasn else 0}" if n else "")
            print(f"| {d} | " + " | ".join(cells) + " |")

    # per-response report, from the Client's ratelimit.csv (every response this run sent, retries included)
    with open(rl_path, newline="") as f:
        new = list(csv.DictReader(f))[max(0, rl_before - 1):]
    agg = [r for r in new if r["path"] == "/aggregation"]
    n429 = sum(1 for r in agg if r["status"] == "429")
    secs = [float(r["seconds"]) for r in agg if r["seconds"]]
    print(f"\n### Responses: {len(agg)} aggregation responses sent this run, {n429} x HTTP 429, "
          f"{1 + len(chosen) - len(ob.RESPONSES)} served from cache")
    print("\n| utc | status | seconds | x-ratelimit-remaining | call |")
    print("|---|---|---|---|---|")
    for r in agg:
        call = r["params"]
        print(f"| {r['utc']} | {r['status']} | {r['seconds']} | {r['x-ratelimit-remaining']} | `{call[:90]}` |")
    if secs:
        print(f"\nseconds per response: min {min(secs):.2f}, median {sorted(secs)[len(secs) // 2]:.2f}, "
              f"max {max(secs):.2f}")
    print(f"\nwritten {out_path}; responses cached in {AGG}")


if __name__ == "__main__":
    main()

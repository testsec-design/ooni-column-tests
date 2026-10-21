#!/usr/bin/env python3
"""Job: per day x resolver-egress class, the DNS outcome of a domain's RU web_connectivity
measurements in window TSVs already on disk. No API calls: reads the TSVs of --window (default
dnslook.ONSET_WINDOWS[domain]); registry holders from the T6 RIPEstat cache (a lookup not yet
cached does go to stat.ripe.net).

    ../../venv/bin/python egress_table.py [--domain www.youtube.com] [--window dec_allru ...] \
        [--name-asn AS206385 [--compare-window dec_allru]] \
        > out/egress_table_<domain>[_<window>].md 2> run_egress_<domain>_<window>.log

Tables, markdown on stdout, one function each: (1) per day, distinct probe ASNs with a
measurement via MSK-IX (the union of the three MSK-IX classes) and via any other class, and how
many of each had at least one N, and at least one N or D; (2) day x egress class: measurements and
the N / D / A / I / F split (fractions only where the count is >= 5, raw counts always); (3) the
same restricted to dnslook.ONSET_ASNS[domain], or a note when the TSVs hold only those ASNs; (4)
the MSK-IX union by origin ASN per day; (5) every probe ASN with a measurement via an MSK-IX class,
one row per (day, probe ASN, class): its measurements in that class and their outcomes, its
same-day measurements outside the three MSK-IX classes and theirs, the origin ASNs seen, the
RIPEstat holder, sorted by N+D descending; (6) the "other" class: top ten resolver ASNs by
measurements, with RIPEstat holder; (7) every NXDOMAIN measurement whose egress is not an MSK-IX
class, with its verbatim queries block on stderr; (8, only with --name-asn ASxxx) per day, N+D
count and fraction in nsdi-measured, nsdi-inferred and msk-ix-other side by side, naming the class
the given probe ASN's rows land in, followed by the same rows for each --compare-window. Outcome letters and egress classes are dnslook.outcome() and
dnslook.egress_class(); the MSK-IX classes are nsdi-measured / nsdi-inferred / msk-ix-other, whose
union is asserted against dnslook.PREVIOUS_MSK_IX (the msk-ix counts before the split). Tables only. The day x group table, its cell
formatting and the N D A I F counts are dnslook.day_table / split / counts (moved there 19 Oct 2026), called
here with the outcome letter as the row classifier.
"""
from __future__ import annotations

import argparse
import collections
import sys

import dnslook
from dnslook import MSK_IX_ASNS, MSK_IX_CLASSES, ripestat

CLASSES = [*MSK_IX_CLASSES, "google", "cloudflare", "yandex", "own-asn", "unrecorded", "other"]
LETTERS = "NDAIF"


LETTER = lambda m: m["letter"]      # noqa: E731  the row classifier of these tables: the dnslook outcome letter


def counts(ms: list[dict]) -> str:
    return dnslook.counts(ms, LETTER, LETTERS)


def split(ms: list[dict]) -> str:
    return dnslook.split(ms, LETTER, LETTERS)


def denominators(ms: list[dict]) -> None:
    print("\n#### 1. Distinct probe ASNs per day by egress, and how many had an NXDOMAIN (N) or N or android_no_data (N+D)")
    print("\n| day | ASNs via MSK-IX (3 classes) | with N | with N+D | ASNs via anything else | with N | with N+D | both |")
    print("|---|---|---|---|---|---|---|---|")
    for d in sorted({m["day"] for m in ms}):
        dm = [m for m in ms if m["day"] == d]
        via = [m for m in dm if m["egress"] in MSK_IX_CLASSES]
        rest = [m for m in dm if m["egress"] not in MSK_IX_CLASSES]
        asns = lambda xs, letters: {m["asn"] for m in xs if m["letter"] in letters}   # noqa: E731
        print(f"| {d} | {len(asns(via, LETTERS))} | {len(asns(via, 'N'))} | {len(asns(via, 'ND'))} | "
              f"{len(asns(rest, LETTERS))} | {len(asns(rest, 'N'))} | {len(asns(rest, 'ND'))} | "
              f"{len(asns(via, LETTERS) & asns(rest, LETTERS))} |")


def by_class(ms: list[dict], onset: set[str]) -> None:
    print("\n#### 2. Day x egress class")
    dnslook.day_table(ms, lambda m: m["egress"], CLASSES, "egress", LETTER, LETTERS)
    print("\n#### 3. Restricted to the onset ASNs")
    asns = {m["asn"] for m in ms}
    if asns <= onset:
        print(f"\nThe window TSVs hold only {len(asns)} of the {len(onset)} onset ASNs "
              f"({len(onset - asns)} had no measurements), so table 2 already is the restricted table.")
    else:
        print(f"\n{len(asns & onset)} of the {len(onset)} onset ASNs appear among the {len(asns)} ASNs in these windows.")
        dnslook.day_table([m for m in ms if m["asn"] in onset], lambda m: m["egress"], CLASSES, "egress", LETTER, LETTERS)


def msk_ix(ms: list[dict]) -> None:
    print("\n#### 4. MSK-IX classes (union of nsdi-measured, nsdi-inferred, msk-ix-other) by origin ASN")
    mx = [m for m in ms if m["egress"] in MSK_IX_CLASSES]
    dnslook.day_table(mx, lambda m: m["resolver_asn"], ["AS" + x for x in sorted(MSK_IX_ASNS)], "origin ASN", LETTER, LETTERS)
    print("\n#### 5. Probe ASNs with a measurement via an MSK-IX class, per (day, class) (sorted by N+D in the class, descending)")
    print("\n| day | probe ASN | class | via class | N D A I F | via non-MSK-IX classes | N D A I F | origin ASNs | RIPEstat holder |")
    print("|---|---|---|---|---|---|---|---|---|")
    rows = []
    for (d, asn, cls) in sorted({(m["day"], m["asn"], m["egress"]) for m in mx}):
        via = [m for m in mx if m["day"] == d and m["asn"] == asn and m["egress"] == cls]
        rest = [m for m in ms if m["day"] == d and m["asn"] == asn and m["egress"] not in MSK_IX_CLASSES]
        nd = sum(1 for m in via if m["letter"] in "ND")
        rows.append((-nd, d, asn, MSK_IX_CLASSES.index(cls), cls, via, rest))
    for _, d, asn, _, cls, via, rest in sorted(rows, key=lambda r: (r[0], r[1], r[2], r[3])):
        origins = ", ".join(sorted({m["resolver_asn"] for m in via}))
        print(f"| {d} | {asn} | {cls} | {len(via)} | {counts(via)} | {len(rest)} | {counts(rest) if rest else ''} | "
              f"{origins} | {ripestat.holder(asn)[0][:50]} |")


def others(ms: list[dict]) -> None:
    print("\n#### 6. The \"other\" class: top ten resolver ASNs")
    other = collections.Counter(m["resolver_asn"] for m in ms if m["egress"] == "other")
    print("\n| resolver_asn | msm | N D A I F | probe ASNs | RIPEstat holder |")
    print("|---|---|---|---|---|")
    for asn, n in other.most_common(10):
        om = [m for m in ms if m["egress"] == "other" and m["resolver_asn"] == asn]
        probes = sorted({m["asn"] for m in om})
        print(f"| {asn} | {n} | {counts(om)} | {', '.join(probes[:8])}{' ...' if len(probes) > 8 else ''} "
              f"({len(probes)}) | {ripestat.holder(asn)[0][:70]} |")
    if not other:
        print("| (none) | | | | |")


def strays(ms: list[dict]) -> None:
    st = [m for m in ms if m["letter"] == "N" and m["egress"] not in MSK_IX_CLASSES]
    print(f"\n#### 7. NXDOMAIN measurements whose egress is not an MSK-IX class: {len(st)} "
          f"(verbatim queries blocks on stderr / in the run log)")
    print("\n| start (UTC) | measurement_uid | probe_asn | egress | resolver_ip | resolver_asn | software |")
    print("|---|---|---|---|---|---|---|")
    for m in st:
        print(f"| {m['t']} | {m['uid']} | {m['asn']} | {m['egress']} | {m['resolver_ip']} | {m['resolver_asn']} | {m['software']} |")
        print(f"\n== {m['uid']} {m['asn']} {m['t']} egress={m['egress']} resolver_ip={m['resolver_ip']} "
              f"{m['resolver_asn']} {m['software']}\n{dnslook.queries_json(dnslook.raw(m['uid']))}", file=sys.stderr)


def nd_by_class(ms: list[dict], name_asn: str, compare: list[tuple[str, list[dict]]] = ()) -> None:
    """Table 8; `compare` = [(label, measurements)] adds the same per-day rows for other window sets
    beneath, the label in the day column, for a side-by-side comparison."""
    print(f"\n#### 8. N+D per day in the three MSK-IX classes side by side, and where {name_asn}'s rows land"
          + (" (comparison rows: " + ", ".join(lab for lab, _ in compare) + ")" if compare else ""))
    print("\n| day | " + " | ".join(f"{c}: N+D / msm (frac)" for c in MSK_IX_CLASSES) + f" | {name_asn} rows |")
    print("|---|" + "---|" * (len(MSK_IX_CLASSES) + 1))
    for label, mset in [("", ms), *compare]:
        for d in sorted({m["day"] for m in mset}):
            dm = [m for m in mset if m["day"] == d]
            cells = []
            for c in MSK_IX_CLASSES:
                cm = [m for m in dm if m["egress"] == c]
                nd = sum(1 for m in cm if m["letter"] in "ND")
                cells.append(f"{nd} / {len(cm)} ({nd / len(cm):.2f})" if cm else "0 / 0")
            named = collections.Counter(m["egress"] for m in dm if m["asn"] == name_asn)
            named_nd = collections.Counter(m["egress"] for m in dm if m["asn"] == name_asn and m["letter"] in "ND")
            where = "; ".join(f"{c}: {n} msm, N+D {named_nd[c]}" for c, n in named.most_common()) or "none"
            print(f"| {d}{' (' + label + ')' if label else ''} | " + " | ".join(cells) + f" | {where} |")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--domain", default="www.youtube.com")
    ap.add_argument("--window", nargs="+", help="window names (default: the domain's onset windows)")
    ap.add_argument("--name-asn", help="probe ASN to name in table 8 (table 8 is printed only with this)")
    ap.add_argument("--compare-window", nargs="+", help="other window names whose per-day rows table 8 repeats beneath, for comparison")
    a = ap.parse_args()
    windows = tuple(a.window) if a.window else dnslook.ONSET_WINDOWS[a.domain]
    ms = dnslook.measurements(dnslook.read_rows(a.domain, windows))
    assert sum(m["egress"] in MSK_IX_CLASSES for m in ms) == dnslook.PREVIOUS_MSK_IX.get((a.domain, windows), sum(m["egress"] in MSK_IX_CLASSES for m in ms)), "MSK-IX class union != previous msk-ix count"
    days = sorted({m["day"] for m in ms})
    print(f"{a.domain}, windows {windows}: {len(ms)} measurements, {len({m['asn'] for m in ms})} probe ASNs, "
          f"{days[0]} .. {days[-1]}")
    denominators(ms)
    by_class(ms, set(dnslook.ONSET_ASNS[a.domain]))
    msk_ix(ms)
    others(ms)
    strays(ms)
    if a.name_asn:
        cmp_ = [(w, dnslook.measurements(dnslook.read_rows(a.domain, [w]))) for w in a.compare_window or []]
        nd_by_class(ms, a.name_asn, cmp_)


if __name__ == "__main__":
    main()

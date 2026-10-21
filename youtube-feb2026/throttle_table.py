#!/usr/bin/env python3
"""Job: the substitution tables of notes section 10 (pre-registered 19 Oct 2026). No API calls: reads the
window TSVs of --domain and --control (default windows pre, post) and the cached raw records in raw/,
classifies every measurement with dnslook.stage() (the first-failing-stage rule of the column tests) and
prints, as markdown on stdout:

    ../../venv/bin/python throttle_table.py [--domain www.youtube.com] [--control www.google.com]
        [--window pre post] [--reps 2000] > out/throttle_table_<domain>.md

  1. day x egress class x stage family, count and fraction, one table per domain (dnslook.day_table with
     the stage family as the row classifier and dnslook.egress_class as the group);
  2. the same restricted to measurements whose DNS resolved through something other than NSDI, i.e. egress
     class not in dnslook.NSDI_CLASSES (nsdi-measured, nsdi-inferred);
  3. per day, the TLS-failure fraction of the domain beside the control, among DNS-resolving measurements
     and among all;
  4. pre/post difference of the TLS-failure fraction with per-ASN bootstrap intervals (dnslook.boot_share /
     boot_contrast, unit = probe ASN, 2000 resamples, seed 6), for the domain and the control, DNS-resolving
     and all.

Stage family = the stage name up to its first underscore: dns (dns_fail), tcp (tcp_fail), tls (tls_timeout,
tls_reset, tls_alert, tls_other and tls_or_http_unsplit: https, no TLS handshake recorded, an HTTP failure),
http (http_timeout/reset/other/diff), ok; none when the record has no test_keys. The unsplit count is shown
beside every tls count in tables 3 and 4. No hygiene (no dedup by report, no mobile filter), every listed
measurement counts once; the input is restricted to the https input of the domain. Tables only.
"""
from __future__ import annotations

import argparse
import collections

import dnslook

CLASSES = [*dnslook.MSK_IX_CLASSES, "google", "cloudflare", "yandex", "own-asn", "unrecorded", "other"]
FAMILIES = ["dns", "tcp", "tls", "http", "ok"]
UNSPLIT = "tls_or_http_unsplit"


def family(stage: str) -> str:
    return "none" if stage == "no_test_keys" else stage.split("_")[0]


def load(domain: str, windows, inp: str) -> list[dict]:
    """Measurements of the domain's windows with input `inp`, each with its stage and family."""
    ms = [m for m in dnslook.measurements(dnslook.read_rows(domain, windows))]
    out = []
    for m in ms:
        r = dnslook.raw(m["uid"])
        if (r.get("input") or "") != inp:
            continue
        tk = r.get("test_keys")
        st = dnslook.stage(tk, inp.lower().startswith("https"))[0] if isinstance(tk, dict) else "no_test_keys"
        out.append({**m, "stage": st, "family": family(st), "resolving": m["egress"] not in dnslook.NSDI_CLASSES})
    return out


def cell(ms: list[dict]) -> str:
    tls = [m for m in ms if m["family"] == "tls"]
    un = sum(1 for m in tls if m["stage"] == UNSPLIT)
    return f"{len(tls)} ({un}) / {len(ms)} = {len(tls) / len(ms):.3f}" if ms else "0 / 0"


def by_day(dom: str, ctl: str, ms_d: list[dict], ms_c: list[dict]) -> None:
    print(f"\n| day | {dom}, DNS-resolving: tls (unsplit) / msm = frac | {dom}, all | {ctl}, DNS-resolving | {ctl}, all |")
    print("|---|---|---|---|---|")
    for d in sorted({m["day"] for m in ms_d} | {m["day"] for m in ms_c}):
        dd = [m for m in ms_d if m["day"] == d]
        cc = [m for m in ms_c if m["day"] == d]
        print(f"| {d} | {cell([m for m in dd if m['resolving']])} | {cell(dd)} | "
              f"{cell([m for m in cc if m['resolving']])} | {cell(cc)} |")


def contrast(label: str, pre: list[dict], post: list[dict], reps: int) -> str:
    tls = lambda m: m["family"] == "tls"      # noqa: E731
    a = dnslook.boot_share(pre, tls, reps=reps, unit="asn")
    b = dnslook.boot_share(post, tls, reps=reps, unit="asn")
    c = dnslook.boot_contrast(post, tls, pre, tls, reps=reps, unit="asn")
    f = lambda x: "nan" if x != x else f"{x:.3f}"    # noqa: E731
    un = lambda ms: sum(1 for m in ms if m["stage"] == UNSPLIT)    # noqa: E731
    return (f"| {label} | {sum(map(tls, pre))} ({un(pre)}) / {a[3]} = {f(a[0])} [{f(a[1])}, {f(a[2])}] | {a[4]} | "
            f"{sum(map(tls, post))} ({un(post)}) / {b[3]} = {f(b[0])} [{f(b[1])}, {f(b[2])}] | {b[4]} | "
            f"{f(c[0])} [{f(c[1])}, {f(c[2])}] |")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--domain", default="www.youtube.com")
    ap.add_argument("--control", default="www.google.com")
    ap.add_argument("--window", nargs=2, default=["pre", "post"], metavar=("PRE", "POST"))
    ap.add_argument("--reps", type=int, default=2000)
    a = ap.parse_args()
    pre_w, post_w = a.window
    data = {}
    for dom in (a.domain, a.control):
        data[dom] = load(dom, [pre_w, post_w], f"https://{dom}/")
    fam = lambda m: m["family"]      # noqa: E731
    egress = lambda m: m["egress"]   # noqa: E731
    cats = FAMILIES + (["none"] if any(m["family"] == "none" for ms in data.values() for m in ms) else [])

    for dom, ms in data.items():
        days = sorted({m["day"] for m in ms})
        st = collections.Counter(m["stage"] for m in ms)
        print(f"\n{dom} (`https://{dom}/`), windows {pre_w} + {post_w}: {len(ms)} measurements, "
              f"{len({m['asn'] for m in ms})} probe ASNs, {days[0]} .. {days[-1]}; stages: "
              + ", ".join(f"{k} {v}" for k, v in st.most_common()))

    print("\n#### 1. Day x egress class x stage family (count; fractions from n >= 5)")
    for dom, ms in data.items():
        print(f"\n{dom}:")
        dnslook.day_table(ms, egress, CLASSES, "egress", fam, cats)

    print("\n#### 2. The same restricted to DNS-resolving measurements (egress class not nsdi-measured / nsdi-inferred)")
    for dom, ms in data.items():
        res = [m for m in ms if m["resolving"]]
        print(f"\n{dom}: {len(res)} of {len(ms)} measurements, {len({m['asn'] for m in res})} probe ASNs")
        dnslook.day_table(res, egress, [c for c in CLASSES if c not in dnslook.NSDI_CLASSES], "egress", fam, cats)

    print(f"\n#### 3. TLS-failure fraction per day, {a.domain} beside {a.control} (tls count, in brackets how many are {UNSPLIT})")
    by_day(a.domain, a.control, data[a.domain], data[a.control])

    print(f"\n#### 4. Pre/post difference in TLS-failure fraction, per-ASN bootstrap ({a.reps} resamples of probe ASNs, seed 6; "
          f"Clopper-Pearson on measurements when fewer than 20 ASNs)")
    print(f"\n| domain, subset | {pre_w}: tls (unsplit) / msm = share [95 %] | ASNs | {post_w}: tls (unsplit) / msm = share [95 %] | ASNs | {post_w} - {pre_w} [95 %] |")
    print("|---|---|---|---|---|---|")
    for dom, ms in data.items():
        for sub, keep in (("DNS-resolving", lambda m: m["resolving"]), ("all", lambda m: True)):
            pre = [m for m in ms if m["window"] == pre_w and keep(m)]
            post = [m for m in ms if m["window"] == post_w and keep(m)]
            print(contrast(f"{dom}, {sub}", pre, post, a.reps))


if __name__ == "__main__":
    main()

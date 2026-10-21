#!/usr/bin/env python3
"""Active measurement, run from this Mac: through which addresses and origin ASNs do a.res-nsdi.ru
(195.208.4.1) and b.res-nsdi.ru (195.208.5.1) egress when they recurse, and do those addresses match
the resolver_ip values on the December 2025 NXDOMAIN rows (window_dec_onset.tsv, window_dec_allru.tsv)
rather than the AS206385 rows.

NOTE: this measures the NSDI egress as of October 2026 (the run date). The comparison with the
December 2025 TSVs assumes that egress pool was stable between December 2025 and the run; the script
cannot check that.

Method (one function per query type): A whoami.akamai.net (the answer is the egress IP of the
recursive resolver that reached Akamai) and TXT whoami.ds.akahelp.net ("ns" <egress IP>), each over
UDP and over TCP, 20 rounds at >= 15 s spacing per target so a cached answer cannot hide a pool.
Positive controls 8.8.8.8, 1.1.1.1 and the system resolver get 10 rounds (the 500-query cap; the
rounds are enough for the ASN check): they must egress from AS15169, AS13335 and the ASN of this
machine's public IP, or the method is wrong. Ground truth: A www.youtube.com, A example.com, A ya.ru,
UDP and TCP, 5 rounds each per target; example.com and ya.ru are negative controls that must answer.
Rules: <= 500 queries in total, >= 1 s between queries to either NSDI address, one attempt per query
(5 s timeout, no retry); an NSDI address whose four whoami queries all fail in round 1 is marked
dead, its failure types recorded, and it gets no further queries.

Reads nothing from OONI except, at the end, two sets of resolver_ip values from the December TSVs
through dnslook.read_rows (NXDOMAIN rows, and probe_asn AS206385 rows). Imports T6/ripestat.py
(registry lookups, cached under T6/raw_api/ripestat/) and dnslook's MSK_IX_ASNS; nothing else.

    ../../venv/bin/python nsdi_egress.py 2> run-<date>.log   # writes out/nsdi-egress-<date>.md and
                                                              #        out/nsdi-egress-<date>-queries.tsv
    ../../venv/bin/python nsdi_egress.py --report-only        # rebuild the .md from the saved TSV, no queries
"""
from __future__ import annotations

import collections
import csv
import datetime as dt
import ipaddress
import pathlib
import sys
import time

import dns.exception
import dns.message
import dns.query
import dns.rcode
import dns.rdatatype
import dns.resolver

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "T6"))
sys.path.insert(0, str(HERE.parent / "youtube-feb2026"))
import ripestat  # noqa: E402  (T6 code, imported, not modified)
import dnslook  # noqa: E402  (only MSK_IX_ASNS, NXDOMAIN and read_rows are used)
from dnslook import MSK_IX_ASNS  # noqa: E402

DATE = dt.date.today().isoformat()
OUT = HERE / "out"
MD = OUT / f"nsdi-egress-{DATE}.md"
QTSV = OUT / f"nsdi-egress-{DATE}-queries.tsv"

NSDI = {"195.208.4.1": "a.res-nsdi.ru", "195.208.5.1": "b.res-nsdi.ru"}
CONTROLS = {"8.8.8.8": ("google", "15169"), "1.1.1.1": ("cloudflare", "13335")}
SYSTEM_NS = dns.resolver.get_default_resolver().nameservers[0]
TARGETS = {**NSDI, **{k: v[0] for k, v in CONTROLS.items()}, SYSTEM_NS: "system"}

WHOAMI_ROUNDS_NSDI, WHOAMI_ROUNDS_CTRL, ROUND_GAP = 20, 10, 15.0
GT_QNAMES, GT_ROUNDS, GT_ROUND_GAP = ["www.youtube.com", "example.com", "ya.ru"], 5, 5.0
NEGATIVE_CONTROLS = {"example.com", "ya.ru"}
TIMEOUT, MIN_GAP, CAP = 5.0, 1.0, 500
TRANSPORTS = ("udp", "tcp")

DOMAIN, WINDOWS, PROBE_ASN = "www.youtube.com", ("dec_onset", "dec_allru"), "AS206385"

sent = 0
last_sent: dict[str, float] = collections.defaultdict(float)
records: list[dict] = []
dead: dict[str, str] = {}


def pace(target: str) -> None:
    wait = last_sent[target] + MIN_GAP - time.monotonic()
    if wait > 0:
        time.sleep(wait)


def send(target: str, qname: str, qtype: str, transport: str, phase: str, rnd: int) -> dict:
    """One query, one attempt. Records target, transport, qname, qtype, rcode, answer, RTT and error."""
    global sent
    if sent >= CAP:
        raise RuntimeError(f"query cap {CAP} reached")
    pace(target)
    msg = dns.message.make_query(qname, qtype)
    rec = {"phase": phase, "round": rnd, "t": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
           "target": target, "label": TARGETS[target], "transport": transport, "qname": qname, "qtype": qtype,
           "rcode": "", "answer": "", "rtt_ms": "", "error": ""}
    t0 = time.monotonic()
    try:
        fn = dns.query.udp if transport == "udp" else dns.query.tcp
        resp = fn(msg, target, timeout=TIMEOUT)
        rec["rtt_ms"] = f"{(time.monotonic() - t0) * 1000:.0f}"
        rec["rcode"] = dns.rcode.to_text(resp.rcode())
        rec["answer"] = ";".join(parse_answer(resp, qname, qtype))
    except dns.exception.Timeout:
        rec["rtt_ms"] = f"{(time.monotonic() - t0) * 1000:.0f}"
        rec["error"] = "timeout"
    except Exception as e:  # noqa: BLE001  (BadResponse, ConnectionRefused, OSError ...)
        rec["rtt_ms"] = f"{(time.monotonic() - t0) * 1000:.0f}"
        rec["error"] = type(e).__name__
    sent += 1
    last_sent[target] = time.monotonic()
    records.append(rec)
    print(f"{rec['t']} {phase} r{rnd} {TARGETS[target]:10s} {transport} {qtype:3s} {qname:24s} "
          f"{rec['rcode'] or rec['error']:9s} {rec['answer'][:60]} {rec['rtt_ms']}ms", file=sys.stderr, flush=True)
    return rec


def parse_answer(resp: dns.message.Message, qname: str, qtype: str) -> list[str]:
    out = []
    for rrset in resp.answer:
        if rrset.rdtype == dns.rdatatype.A:
            out += [r.address for r in rrset]
        elif rrset.rdtype == dns.rdatatype.TXT:
            for r in rrset:
                out.append(" ".join(s.decode(errors="replace") for s in r.strings))
        else:
            out += [f"{dns.rdatatype.to_text(rrset.rdtype)}:{r.to_text()}" for r in rrset]
    return out


# One function per query type.
def query_whoami_akamai(target: str, transport: str, rnd: int) -> dict:
    """A whoami.akamai.net: the A answer is the recursive resolver's egress IP as seen by Akamai."""
    rec = send(target, "whoami.akamai.net", "A", transport, "whoami", rnd)
    rec["egress"] = rec["answer"].split(";")[0] if rec["rcode"] == "NOERROR" and rec["answer"] else ""
    return rec


def query_whoami_akahelp(target: str, transport: str, rnd: int) -> dict:
    """TXT whoami.ds.akahelp.net: the TXT 'ns <ip>' string is the egress IP (an 'ecs' string may follow)."""
    rec = send(target, "whoami.ds.akahelp.net", "TXT", transport, "whoami", rnd)
    eg = ""
    for s in rec["answer"].split(";"):
        parts = s.split()
        if len(parts) >= 2 and parts[0] == "ns":
            eg = parts[1]
    rec["egress"] = eg
    return rec


def query_a(target: str, qname: str, transport: str, rnd: int) -> dict:
    """A <qname>: ground truth / negative control, rcode and answers recorded."""
    return send(target, qname, "A", transport, "ground-truth", rnd)


def query_my_ip() -> str:
    """TXT o-o.myaddr.l.google.com at ns1.google.com answers with the address this machine queried from."""
    msg = dns.message.make_query("o-o.myaddr.l.google.com", "TXT")
    global sent
    if "--report-only" not in sys.argv:
        sent += 1
    try:
        resp = dns.query.udp(msg, dns.resolver.resolve("ns1.google.com", "A")[0].address, timeout=TIMEOUT)
        for s in parse_answer(resp, "", "TXT"):
            try:
                ipaddress.ip_address(s)
                return s
            except ValueError:
                pass
    except Exception as e:  # noqa: BLE001
        print(f"my-ip lookup failed: {e!r}", file=sys.stderr)
    return ""


def failed(rec: dict) -> bool:
    return bool(rec["error"]) or rec["rcode"] not in ("NOERROR", "NXDOMAIN")


def run_whoami() -> None:
    for rnd in range(1, WHOAMI_ROUNDS_NSDI + 1):
        t_round = time.monotonic()
        targets = list(NSDI) + ([*CONTROLS, SYSTEM_NS] if rnd <= WHOAMI_ROUNDS_CTRL else [])
        for fn in (query_whoami_akamai, query_whoami_akahelp):
            for transport in TRANSPORTS:
                for target in targets:
                    if target in dead:
                        continue
                    fn(target, transport, rnd)
        if rnd == 1:
            for target in NSDI:
                rs = [r for r in records if r["target"] == target]
                if rs and all(failed(r) for r in rs):
                    kinds = collections.Counter(r["error"] or r["rcode"] for r in rs)
                    dead[target] = ", ".join(f"{k} x{n}" for k, n in kinds.items())
                    print(f"{target} ({NSDI[target]}) does not answer from here: {dead[target]}; no further queries",
                          file=sys.stderr)
        if rnd < WHOAMI_ROUNDS_NSDI:
            time.sleep(max(0.0, ROUND_GAP - (time.monotonic() - t_round)))


def run_ground_truth() -> None:
    for rnd in range(1, GT_ROUNDS + 1):
        t_round = time.monotonic()
        for qname in GT_QNAMES:
            for transport in TRANSPORTS:
                for target in TARGETS:
                    if target in dead:
                        continue
                    query_a(target, qname, transport, rnd)
        if rnd < GT_ROUNDS:
            time.sleep(max(0.0, GT_ROUND_GAP - (time.monotonic() - t_round)))


def ipkey(ip: str):
    """Sort key for a mixed IPv4/IPv6 set (ipaddress objects of different versions do not compare)."""
    a = ipaddress.ip_address(ip)
    return (a.version, int(a))


def origin_of(ip: str) -> tuple[str, str, str]:
    """ip -> (origin ASNs joined, prefix, holder of the first origin ASN) via T6/ripestat (cached)."""
    asns, prefix = ripestat.origin(ip)
    holder = ripestat.holder(asns[0])[0] if asns else ""
    return ",".join(asns), prefix, holder


def egress_table(recs: list[dict]) -> list[str]:
    """Rows: egress IP -> origin ASN -> holder, with the number of queries that returned it."""
    c = collections.Counter(r["egress"] for r in recs if r.get("egress"))
    lines = []
    for ip, n in c.most_common():
        asn, prefix, holder = origin_of(ip)
        lines.append(f"| {ip} | {n} | {prefix} | AS{asn} | {holder} |")
    return lines


def rcode_summary(recs: list[dict]) -> str:
    c = collections.Counter(r["rcode"] or r["error"] for r in recs)
    return ", ".join(f"{k} x{n}" for k, n in c.most_common())


def median_rtt(recs: list[dict]) -> str:
    v = sorted(int(r["rtt_ms"]) for r in recs if r["rtt_ms"] and not r["error"])
    return f"{v[len(v) // 2]}" if v else "-"


def write_report(my_ip: str, my_asn: str, my_holder: str) -> None:
    L = []
    w = L.append
    w(f"# NSDI resolver egress, active measurement from this Mac, {DATE}")
    w("")
    w(f"**Caveat.** This measures the egress of 195.208.4.1 / 195.208.5.1 as of {DATE} (October 2026). "
      "The comparison in section 4 with the December 2025 window TSVs assumes the egress pool was stable "
      "between December 2025 and this run; nothing here checks that. It is also one vantage point: the NSDI "
      "addresses are anycast, so the node (and egress pool) reached from this machine in Germany need not be the "
      "one Russian probes reached in December; an egress IP in a sibling /24 with the same MSK-IX origin ASN "
      "is consistent with another node of the same service, not evidence against it.")
    w("")
    w(f"Run from public IP {my_ip or '(unknown)'} (origin AS{my_asn or '?'}, {my_holder or '?'}); system resolver "
      f"{SYSTEM_NS}. {sent} queries sent (cap {CAP}); one attempt each, {TIMEOUT:.0f} s timeout; >= {MIN_GAP:.0f} s "
      f"between queries to one target; whoami rounds {ROUND_GAP:.0f} s apart ({WHOAMI_ROUNDS_NSDI} rounds for NSDI, "
      f"{WHOAMI_ROUNDS_CTRL} for the controls), ground-truth rounds {GT_ROUND_GAP:.0f} s apart ({GT_ROUNDS} rounds). "
      f"Per-query records: `{QTSV.name}`. Registry data: RIPEstat via T6/ripestat.py.")
    w("")
    if dead:
        w("**NSDI addresses that did not answer from here (stopped after round 1):**")
        for t, why in dead.items():
            w(f"- {t} ({NSDI[t]}): {why}")
        w("")
    whoami = [r for r in records if r["phase"] == "whoami"]

    # 1. Controls
    w("## 1. Control table: resolver -> egress IPs -> origin ASN -> holder")
    w("")
    w("Expected: 8.8.8.8 -> AS15169, 1.1.1.1 -> AS13335, system resolver -> this machine's ISP ASN "
      f"(AS{my_asn or '?'} from the public IP above).")
    w("")
    verdicts = []
    for target, label in TARGETS.items():
        if target in NSDI:
            continue
        rs = [r for r in whoami if r["target"] == target]
        asns = {origin_of(r["egress"])[0] for r in rs if r.get("egress")}
        expect = CONTROLS[target][1] if target in CONTROLS else my_asn
        ok = bool(asns) and all(a == expect for a in asns)
        verdicts.append(ok)
        w(f"### {label} ({target}): {len(rs)} whoami queries, {rcode_summary(rs)}, median RTT {median_rtt(rs)} ms, "
          f"{len({r['egress'] for r in rs if r.get('egress')})} distinct egress IPs, origin ASNs {{{', '.join('AS' + a for a in sorted(asns))}}} "
          f"-> expected AS{expect}: **{'PASS' if ok else 'FAIL'}**")
        w("")
        w("| egress IP | queries | prefix | origin ASN | holder |")
        w("|---|---|---|---|---|")
        L.extend(egress_table(rs))
        w("")
    controls_ok = all(verdicts)
    w(f"**Controls: {'PASS, the method is sound' if controls_ok else 'FAIL, the method is wrong and the NSDI rows below are not to be trusted'}.**")
    w("")

    # 2. NSDI
    w("## 2. NSDI table: egress per address, UDP and TCP separately")
    w("")
    nsdi_egress: dict[str, set[str]] = {}
    for target, label in NSDI.items():
        for transport in TRANSPORTS:
            rs = [r for r in whoami if r["target"] == target and r["transport"] == transport]
            ips = {r["egress"] for r in rs if r.get("egress")}
            nsdi_egress[target] = nsdi_egress.get(target, set()) | ips
            asns = {origin_of(ip)[0] for ip in ips}
            in_mskix = {a for a in asns if a in MSK_IX_ASNS}
            w(f"### {label} ({target}) over {transport.upper()}: {len(rs)} whoami queries "
              f"({len(rs) // 2 if rs else 0} per qname), {rcode_summary(rs)}, median RTT {median_rtt(rs)} ms; "
              f"**{len(ips)} distinct egress IPs**; origin ASNs {{{', '.join('AS' + a for a in sorted(asns))}}}"
              f"{' (all in dnslook.MSK_IX_ASNS)' if asns and in_mskix == asns else (' (' + str(len(in_mskix)) + ' of ' + str(len(asns)) + ' in dnslook.MSK_IX_ASNS)' if asns else '')}")
            w("")
            w("| egress IP | queries | prefix | origin ASN | holder |")
            w("|---|---|---|---|---|")
            L.extend(egress_table(rs))
            w("")
        # per-qname agreement
        rs = [r for r in whoami if r["target"] == target]
        byq = {q: {r["egress"] for r in rs if r["qname"] == q and r.get("egress")} for q in
               ("whoami.akamai.net", "whoami.ds.akahelp.net")}
        w(f"Egress sets by qname for {label}: akamai.net {len(byq['whoami.akamai.net'])} IPs, akahelp.net "
          f"{len(byq['whoami.ds.akahelp.net'])} IPs, {len(byq['whoami.akamai.net'] & byq['whoami.ds.akahelp.net'])} in common.")
        w("")

    # 3. Ground truth
    w("## 3. Ground-truth table: rcode per (resolver, qname, transport)")
    w("")
    w(f"{GT_ROUNDS} queries per cell. example.com and ya.ru are negative controls and must answer; www.youtube.com is "
      "the current ground truth for the DNS stage.")
    w("")
    w("| resolver | qname | transport | rcodes / errors | distinct A answers | median RTT ms |")
    w("|---|---|---|---|---|---|")
    gt = [r for r in records if r["phase"] == "ground-truth"]
    neg_fail = []
    for target, label in TARGETS.items():
        for qname in GT_QNAMES:
            for transport in TRANSPORTS:
                rs = [r for r in gt if r["target"] == target and r["qname"] == qname and r["transport"] == transport]
                if not rs:
                    continue
                answers = {a for r in rs for a in r["answer"].split(";") if a}
                w(f"| {label} ({target}) | {qname} | {transport} | {rcode_summary(rs)} | {len(answers)}: "
                  f"{', '.join(sorted(answers)[:6])}{' ...' if len(answers) > 6 else ''} | {median_rtt(rs)} |")
                if qname in NEGATIVE_CONTROLS:
                    ok = [r for r in rs if r["rcode"] == "NOERROR" and r["answer"]]
                    if len(ok) < len(rs):
                        neg_fail.append((f"{label} {qname} {transport}", len(ok), len(rs),
                                         rcode_summary([r for r in rs if r not in ok])))
    w("")
    unanswered = [f for f in neg_fail if f[1] == 0]
    partial = [f for f in neg_fail if f[1] > 0]
    w("Negative controls: " + ("every cell answered NOERROR with A records in all queries." if not neg_fail else
                               ("**FAILED** (no answer at all) for " + ", ".join(f[0] for f in unanswered) + ". " if unanswered else
                                "no cell failed outright. ") +
                               ("Partial loss: " + "; ".join(f"{f[0]} answered {f[1]} of {f[2]} ({f[3]})" for f in partial) + "."
                                if partial else "")))
    w("")

    # 4. Comparison with December TSVs
    w("## 4. Comparison with the December 2025 window TSVs (read through dnslook.read_rows)")
    w("")
    w("NSDI egress set = union of the egress IPs in section 2 (both addresses, both transports, both qnames), "
      f"measured {DATE}; see the caveat at the top.")
    w("")
    all_nsdi = set().union(*nsdi_egress.values()) if nsdi_egress else set()
    all_nsdi24 = {str(ipaddress.ip_network(ip + "/24", strict=False)) for ip in all_nsdi if ":" not in ip}
    w(f"NSDI egress IPs ({len(all_nsdi)}): {', '.join(sorted(all_nsdi, key=ipkey))}")
    w("")
    w(f"NSDI egress /24s ({len(all_nsdi24)}): {', '.join(sorted(all_nsdi24))}")
    w("")
    w("| set | file | rows | distinct resolver_ip | overlap with NSDI egress (exact IP) | overlap by /24 |")
    w("|---|---|---|---|---|---|")
    detail = []
    sets = {}
    for window in WINDOWS:
        rows = dnslook.read_rows(DOMAIN, [window])
        for name, pick in (("(a) NXDOMAIN rows", lambda r: r["failure"] == dnslook.NXDOMAIN),
                           (f"(b) {PROBE_ASN} rows", lambda r: r["probe_asn"] == PROBE_ASN)):
            sel = [r for r in rows if pick(r)]
            ips = {r["resolver_ip"] for r in sel} - dnslook.UNRECORDED_IPS
            sets[(name, window)] = ips
            exact = ips & all_nsdi
            by24 = {ip for ip in ips if ":" not in ip and str(ipaddress.ip_network(ip + "/24", strict=False)) in all_nsdi24}
            w(f"| {name} | window_{window}.tsv | {len(sel)} | {len(ips)} | {len(exact)} | {len(by24)} |")
            detail.append((name, window, ips, exact, by24))
    for name in ("(a) NXDOMAIN rows", f"(b) {PROBE_ASN} rows"):
        u = set().union(*(v for k, v in sets.items() if k[0] == name))
        exact = u & all_nsdi
        by24 = {ip for ip in u if ":" not in ip and str(ipaddress.ip_network(ip + "/24", strict=False)) in all_nsdi24}
        w(f"| {name} | both files (union) | | {len(u)} | {len(exact)} | {len(by24)} |")
    w("")
    for name, window, ips, exact, by24 in detail:
        w(f"**{name}, window_{window}.tsv**: resolver_ip values (excluding unrecorded "
          f"{sorted(dnslook.UNRECORDED_IPS)}):")
        w("")
        w("| resolver_ip | prefix | origin ASN | holder | in NSDI egress (exact) | NSDI /24 |")
        w("|---|---|---|---|---|---|")
        for ip in sorted(ips, key=ipkey):
            asn, prefix, holder = origin_of(ip)
            w(f"| {ip} | {prefix} | AS{asn} | {holder} | {'yes' if ip in exact else 'no'} | {'yes' if ip in by24 else 'no'} |")
        if not ips:
            w("| (none) | | | | | |")
        w("")
    w("### Reading")
    w("")
    nsdi_asns = {origin_of(ip)[0] for ip in all_nsdi}
    w(f"NSDI egress origin ASNs seen now: {{{', '.join('AS' + a for a in sorted(nsdi_asns))}}}; "
      f"dnslook.MSK_IX_ASNS (the December NXDOMAIN egress ASNs): {{{', '.join('AS' + a for a in sorted(MSK_IX_ASNS))}}}; "
      f"intersection {{{', '.join('AS' + a for a in sorted(nsdi_asns & MSK_IX_ASNS))}}}.")
    w("")
    a_u = set().union(*(v for k, v in sets.items() if k[0] == "(a) NXDOMAIN rows"))
    b_u = set().union(*(v for k, v in sets.items() if k[0] == f"(b) {PROBE_ASN} rows"))
    a_exact, b_exact = a_u & all_nsdi, b_u & all_nsdi
    a_24 = {ip for ip in a_u if ":" not in ip and str(ipaddress.ip_network(ip + "/24", strict=False)) in all_nsdi24}
    a_msk = {ip for ip in a_u if origin_of(ip)[0] in MSK_IX_ASNS}
    b_24 = {ip for ip in b_u if ":" not in ip and str(ipaddress.ip_network(ip + "/24", strict=False)) in all_nsdi24}
    w(f"Exact-IP overlap of the NSDI egress set with (a) the December NXDOMAIN resolver_ip values: {len(a_exact)} of "
      f"{len(a_u)} ({', '.join(sorted(a_exact, key=ipkey)) or 'none'}); by /24: {len(a_24)} of {len(a_u)} "
      f"({', '.join(sorted(a_24, key=ipkey)) or 'none'}). {len(a_msk)} of the {len(a_u)} NXDOMAIN resolver IPs have an "
      f"MSK-IX origin ASN; the ones outside the two /24s seen here sit in sibling 193.232.x / 194.226.75.x /24s of "
      f"AS42139, AS43832, AS42728 and AS47445.")
    w("")
    w(f"Exact-IP overlap with (b) the {PROBE_ASN} resolver_ip values: {len(b_exact)} of {len(b_u)} "
      f"({', '.join(sorted(b_exact, key=ipkey)) or 'none'}); by /24: {len(b_24)} of {len(b_u)}. The {PROBE_ASN} values "
      f"({', '.join(sorted(b_u, key=ipkey)) or 'none'}) are in a /24 this run never saw as NSDI egress.")
    w("")
    MD.write_text("\n".join(L) + "\n")


def write_queries() -> None:
    cols = ["phase", "round", "t", "target", "label", "transport", "qname", "qtype", "rcode", "answer", "rtt_ms", "error", "egress"]
    with open(QTSV, "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=cols, delimiter="\t", extrasaction="ignore")
        wr.writeheader()
        for r in records:
            wr.writerow({c: r.get(c, "") for c in cols})


def load_queries() -> None:
    """--report-only: rebuild the report from the saved per-query TSV without sending anything."""
    global sent
    with open(QTSV, newline="") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            records.append(r)
    sent = len(records)
    for target in NSDI:
        rs = [r for r in records if r["target"] == target and r["phase"] == "whoami" and r["round"] == "1"]
        if rs and all(failed(r) for r in rs):
            kinds = collections.Counter(r["error"] or r["rcode"] for r in rs)
            dead[target] = ", ".join(f"{k} x{n}" for k, n in kinds.items())


def main() -> None:
    if "--report-only" in sys.argv:
        load_queries()
        my_ip = query_my_ip()
        my_asn, _, my_holder = origin_of(my_ip) if my_ip else ("", "", "")
        write_report(my_ip, my_asn, my_holder)
        print(f"rebuilt {MD} from {QTSV}; {sent} recorded queries", file=sys.stderr)
        return
    planned = (len(NSDI) * WHOAMI_ROUNDS_NSDI + 3 * WHOAMI_ROUNDS_CTRL) * 4 + len(TARGETS) * len(GT_QNAMES) * 2 * GT_ROUNDS + 1
    assert planned <= CAP, planned
    print(f"{DATE} targets {TARGETS}; planned queries {planned} (cap {CAP})", file=sys.stderr)
    my_ip = query_my_ip()
    my_asn, _, my_holder = origin_of(my_ip) if my_ip else ("", "", "")
    print(f"public IP {my_ip} AS{my_asn} {my_holder}", file=sys.stderr)
    try:
        run_whoami()
        run_ground_truth()
    finally:
        write_queries()
        write_report(my_ip, my_asn, my_holder)
        print(f"wrote {MD} and {QTSV}; {sent} queries", file=sys.stderr)


if __name__ == "__main__":
    main()

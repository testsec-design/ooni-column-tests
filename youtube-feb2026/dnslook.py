"""Shared pieces of the youtube-feb2026 look: paths, the OONI API client and registry helper from
T0/T6, the window-TSV contract (columns, path, reader), the per-measurement outcome rule, the
resolver-egress rule, the facts about the world those rules need, and three rules the column tests
share (moved here unchanged on 19 Oct 2026, the only copies): stage() with kind(), the first-failing-stage
rule of T0/T1/T2/T4 extract_stages.py, which import it from here; boot_share() / boot_contrast() with
_boot_ratio() and the Clopper-Pearson fallback (clopper, _betainc, _betacf, _beta_q) of T6/common.py,
the per-unit bootstrap (unit="probe_asn" makes it per-ASN), which T6/common.py imports from here; and
day_table() with counts() / split(), the per-day-per-group table of egress_table.py, now taking the row
classifier (outcome letter or stage) and its category list as arguments. The scripts each keep one
job: check_youtube_dns.py fetches and writes window TSVs; onset_by_day.py builds day series from
the aggregation API; mixture_dec.py tabulates the within-ASN mixture; egress_table.py tabulates
outcomes by egress. They share this module and the TSVs, nothing else.
"""
from __future__ import annotations

import collections
import csv
import datetime as dt
import ipaddress
import json
import math
import pathlib
import random
import sys

try:
    import numpy as np
except ImportError:  # the bootstrap then runs in pure Python (slow on large units)
    np = None

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "T0"))
sys.path.insert(0, str(HERE.parent / "T6"))
import pull_api  # noqa: E402  (T0 code, imported, not modified)
import ripestat  # noqa: E402  (T6 code, imported, not modified; caches under T6/raw_api/ripestat/)

pull_api.OUT = HERE / "raw_api"          # the Client's ratelimit.csv lands here, not in T0
API = pull_api.API
RAW = HERE / "raw"                        # raw measurement JSON, one file per measurement_uid
OUT = HERE / "out"
AGG = HERE / "raw_api" / "aggregation"    # cached aggregation responses of onset_by_day.py

# Facts about the world, each with where it came from.
NXDOMAIN = "dns_nxdomain_error"
ANDROID_NO_DATA = "android_dns_cache_no_data"      # Android's resolver wrapper; hides the rcode
MSK_IX_ASNS = {"43832", "47445", "42139", "42728"}  # origin ASNs of the 193.232.x / 194.226.75.x egress
#   seen in Dec 2025; RIPEstat holder of all four is MSK-IX ("RIPN-NS5-RU-MSK", "RIPN-RU-RND",
#   "RIPN-RU-NSK", "RIPN-RU-EKT"), notes sections 3 and 6. AS45018 (RU-VLV) was seen once and is left out.
PUBLIC_RESOLVER_ASNS = {"15169": "google", "13335": "cloudflare", "13238": "yandex"}  # RIPEstat holders;
#   Yandex DNS (77.88.8.x) is a common Russian public resolver, origin AS13238
UNRECORDED_IPS = {"", "127.0.0.2"}        # OONI writes resolver_ip 127.0.0.2 when its whoami lookup fails
NSDI = ("195.208.4.0/24", "195.208.5.0/24")  # a/b.res-nsdi.ru service ranges, origin AS41740 "NDNS" (MSK-IX)
# The msk-ix egress class is split three ways by resolver_ip (all three still require an MSK-IX origin ASN):
NSDI_MEASURED_24 = {"193.232.230.0/24",   # egress of a.res-nsdi.ru 195.208.4.1 (AS42139 RIPN-RU-NSK)
                    "193.232.177.0/24"}   # egress of b.res-nsdi.ru 195.208.5.1 (AS43832 RIPN-NS5-RU-MSK)
#   measured from Frankfurt (AS3209) on 19 Oct 2026, 80 whoami queries per address over UDP+TCP, every one in
#   these two /24s (or their IPv6 siblings 2001:67c:1211::/48, 2a0c:a9c7:177::/48, which OONI never records):
#   ../nsdi-egress/out/nsdi-egress-2026-10-19.md. One vantage point; NSDI is anycast.
NSDI_INFERRED_24 = {"193.232.93.0/24",    # AS43832 RIPN-NS5-RU-MSK
                    "193.232.139.0/24",   # AS47445 RIPN-RU-RND
                    "193.232.160.0/24",   # AS43832 RIPN-NS5-RU-MSK
                    "193.232.231.0/24",   # AS42728 RIPN-RU-EKT
                    "193.232.236.0/24",   # AS47445 RIPN-RU-RND
                    "193.232.240.0/24",   # AS42139 RIPN-RU-NSK
                    "194.226.75.0/24"}    # AS43832 RIPN-NS5-RU-MSK
#   the /24s of every resolver_ip with an MSK-IX origin ASN on a dns_nxdomain_error row of the December
#   www.youtube.com windows (dec_before: none; dec_onset and dec_allru: these seven plus the two measured ones),
#   derived once on 19 Oct 2026 from out/www.youtube.com/window_dec_{before,onset,allru}.tsv and written down
#   here, not recomputed; sibling /24s of the measured egress in the same four MSK-IX ASNs, taken to be other
#   anycast nodes of the same service. Any other MSK-IX resolver_ip is msk-ix-other.
MSK_IX_CLASSES = ("nsdi-measured", "nsdi-inferred", "msk-ix-other")   # their union is the old msk-ix class
NSDI_CLASSES = ("nsdi-measured", "nsdi-inferred")   # the two whose egress is the NSDI service: DNS does not resolve there after 22 Dec
PREVIOUS_MSK_IX = {("www.youtube.com", ("dec_before", "dec_onset")): 229,   # msk-ix counts before the split,
                   ("www.youtube.com", ("dec_allru",)): 105,                 # notes sections 8, 8b, 9 of
                   ("www.whatsapp.com", ("jan_before", "jan_onset")): 3}     # 19 Oct 2026 (first pass)

# Facts about this look (which windows and ASNs the fetch script was run with).
ONSET_WINDOWS = {"www.youtube.com": ("dec_before", "dec_onset"),       # 19-21 / 22-24 Dec 2025
                 "www.whatsapp.com": ("jan_before", "jan_onset")}      # 10-13 / 14-16 Jan 2026
ONSET_ASNS = {"www.youtube.com": ["AS12714", "AS12958", "AS15378", "AS25513", "AS25515", "AS29182", "AS31430",
                                  "AS39927", "AS41275", "AS42893", "AS48128", "AS49551", "AS51004", "AS56707",
                                  "AS57712", "AS201643", "AS203891", "AS207103", "AS208397"],
              "www.whatsapp.com": ["AS5429", "AS28775", "AS31133", "AS41668", "AS200679"]}

# The window TSV: one row per measurement x DNS query (q_index empty when a measurement has no queries).
TSV_COLS = ["window", "measurement_uid", "report_id", "measurement_start_time", "probe_asn", "probe_network_name",
            "resolver_ip", "resolver_asn", "test_version", "software_name", "software_version", "network_type", "input",
            "dns_consistency", "dns_experiment_failure", "blocking", "accessible",
            "control_dns_failure", "control_dns_addrs",
            "q_index", "hostname", "query_type", "engine", "resolver_hostname", "resolver_address", "failure",
            "n_answers", "answer_types", "answers"]

OUTCOMES = {"nxdomain": "N", "android_no_data": "D", "answered_consistent": "A", "answered_inconsistent": "I",
            "other_failure": "F"}
ANSWERED = {"A", "I"}


def tsv_path(domain: str, window: str) -> pathlib.Path:
    return OUT / domain / f"window_{window}.tsv"


def read_rows(domain: str, windows) -> list[dict]:
    rows = []
    for w in windows:
        with open(tsv_path(domain, w), newline="") as f:
            rows += list(csv.DictReader(f, delimiter="\t"))
    return rows


def outcome(rows: list[dict]) -> str:
    """One measurement's query rows -> nxdomain (any query with dns_nxdomain_error), android_no_data
    (else any with android_dns_cache_no_data), other_failure (else any other failure, or no queries),
    answered_consistent (no failure, dns_consistency consistent), answered_inconsistent (no failure,
    dns_consistency anything else, including empty)."""
    qs = [r for r in rows if r["q_index"] != ""]
    fails = [r["failure"] for r in qs]
    if NXDOMAIN in fails:
        return "nxdomain"
    if ANDROID_NO_DATA in fails:
        return "android_no_data"
    if any(fails) or not qs:
        return "other_failure"
    return "answered_consistent" if rows[0]["dns_consistency"] == "consistent" else "answered_inconsistent"


def slash24(ip: str) -> str:
    """'a.b.c.d' -> 'a.b.c.0/24'; '' for anything that is not an IPv4 address."""
    try:
        a = ipaddress.ip_address(ip)
    except ValueError:
        return ""
    return str(ipaddress.ip_network(f"{ip}/24", strict=False)) if a.version == 4 else ""


def egress_class(row: dict) -> str:
    """Where the query egressed, from resolver_ip / resolver_asn (the egress OONI's whoami saw, not the
    configured resolver): nsdi-measured (MSK-IX origin ASN and resolver_ip in NSDI_MEASURED_24), nsdi-inferred
    (MSK-IX origin ASN and resolver_ip in NSDI_INFERRED_24), msk-ix-other (any other MSK-IX origin ASN; the
    three together are the former msk-ix class), google, cloudflare, yandex, own-asn (resolver_asn ==
    probe_asn, which misses multi-ASN operators such as Rostelecom and MegaFon), unrecorded (resolver_ip
    empty or 127.0.0.2, or resolver_asn 0/empty), other (anything else; the row keeps the ASN)."""
    asn = (row["resolver_asn"] or "").removeprefix("AS")
    if row["resolver_ip"] in UNRECORDED_IPS or asn in ("", "0"):
        return "unrecorded"
    if asn in MSK_IX_ASNS:
        p = slash24(row["resolver_ip"])
        return "nsdi-measured" if p in NSDI_MEASURED_24 else "nsdi-inferred" if p in NSDI_INFERRED_24 else "msk-ix-other"
    if asn in PUBLIC_RESOLVER_ASNS:
        return PUBLIC_RESOLVER_ASNS[asn]
    if asn == row["probe_asn"].removeprefix("AS"):
        return "own-asn"
    return "other"


def measurements(rows: list[dict]) -> list[dict]:
    """TSV rows -> one dict per measurement, in time order, with its outcome letter and egress class."""
    by_uid = collections.defaultdict(list)
    for r in rows:
        by_uid[r["measurement_uid"]].append(r)
    ms = []
    for uid, qrows in by_uid.items():
        r = qrows[0]
        ms.append({"uid": uid, "asn": r["probe_asn"], "t": dt.datetime.fromisoformat(r["measurement_start_time"]),
                   "day": r["measurement_start_time"][:10], "report_id": r["report_id"],
                   "software": f"{r['software_name']} {r['software_version']}",
                   "network_type": r.get("network_type") or "", "resolver_ip": r["resolver_ip"],
                   "resolver_asn": r["resolver_asn"], "letter": OUTCOMES[outcome(qrows)],
                   "egress": egress_class(r), "dns_consistency": r["dns_consistency"], "window": r["window"]})
    return sorted(ms, key=lambda m: m["t"])


def raw(uid: str) -> dict:
    """The cached raw measurement (raw/<uid>.json); KeyError-free, FileNotFoundError when not fetched."""
    return json.loads((RAW / f"{uid}.json").read_text())


def queries_json(m: dict) -> str:
    """test_keys.queries of a raw measurement, verbatim, as indented JSON."""
    return json.dumps((m.get("test_keys") or {}).get("queries"), indent=1)


# ---- stage rule (T0/T1/T2/T4 extract_stages.py, byte-identical copies until 19 Oct 2026) ----------------------

def kind(f: str) -> str:
    f = f.lower()
    if "timeout" in f or "timed_out" in f or "deadline" in f:
        return "timeout"
    if "reset" in f or "forcibly closed" in f:
        return "reset"
    if f.startswith("ssl_") or "tls:" in f or "alert" in f or "x509" in f or "certificate" in f:
        return "alert"
    return "other"


def stage(tk: dict, https: bool) -> tuple[str, str, int]:
    """-> (stage, detail, tcp_partial)"""
    dnsf = tk.get("dns_experiment_failure")
    if dnsf:
        return "dns_fail", dnsf, 0
    tcp = tk.get("tcp_connect") or []
    tcp_ok = [t for t in tcp if (t.get("status") or {}).get("success")]
    tcp_bad = [t for t in tcp if not (t.get("status") or {}).get("success")]
    if tcp and not tcp_ok:
        return "tcp_fail", str((tcp_bad[0].get("status") or {}).get("failure")), 0
    partial = int(bool(tcp_ok and tcp_bad))
    httpf = tk.get("http_experiment_failure")
    if https:
        th = tk.get("tls_handshakes") or []
        if th:
            if not any(h.get("failure") is None for h in th):
                f = str(th[0].get("failure"))
                k = kind(f)
                return "tls_" + k, f, partial
        elif httpf:
            return "tls_or_http_unsplit", httpf, partial
    if httpf:
        k = kind(httpf)
        return "http_" + ("other" if k == "alert" else k), httpf, partial
    if tk.get("status_code_match") is False:
        return "http_diff", "status", partial
    if (tk.get("body_length_match") is False and tk.get("headers_match") is not True
            and tk.get("title_match") is not True):
        return "http_diff", "body", partial
    return "ok", "", partial


# ---- per-unit bootstrap and Clopper-Pearson fallback (T6/common.py until 19 Oct 2026) ---------------------------

def boot_share(rows, pred, reps=2000, seed=6, unit="report_id"):
    """share of rows satisfying pred, with a 95 % percentile interval resampling units (reports)."""
    by = collections.defaultdict(lambda: [0, 0])
    for r in rows:
        b = by[r[unit]]; b[1] += 1; b[0] += int(bool(pred(r)))
    units = list(by.values()); n = sum(u[1] for u in units); k = sum(u[0] for u in units)
    if n == 0: return (float("nan"), float("nan"), float("nan"), 0, 0)
    if len(units) < 20:  # Clopper-Pearson on measurements when few reports
        lo, hi = clopper(k, n); return (k / n, lo, hi, n, len(units))
    ests = _boot_ratio(units, reps, seed)
    return (k / n, ests[int(0.025 * reps)], ests[int(0.975 * reps) - 1], n, len(units))
def _boot_ratio(units, reps, seed):
    """bootstrap distribution of sum(successes)/sum(trials) over resampled units; numpy in chunks when available."""
    m = len(units)
    if np is not None:
        arr = np.asarray(units, dtype=np.int64); rng = np.random.default_rng(seed); out = []
        for start in range(0, reps, 200):
            idx = rng.integers(0, m, size=(min(200, reps - start), m))
            s = arr[idx, 0].sum(axis=1); f = arr[idx, 1].sum(axis=1)
            out.append(np.where(f > 0, s / np.maximum(f, 1), 0.0))
        return sorted(np.concatenate(out).tolist())
    rnd = random.Random(seed); ests = []
    for _ in range(reps):
        s = f = 0
        for _ in range(m):
            u = units[rnd.randrange(m)]; s += u[0]; f += u[1]
        ests.append(s / f if f else 0.0)
    return sorted(ests)
def boot_contrast(rows_a, pred_a, rows_b, pred_b, reps=2000, seed=6, unit="report_id"):
    """share(a) - share(b) with interval; a and b resampled independently over their reports."""
    def units(rows, pred):
        by = collections.defaultdict(lambda: [0, 0])
        for r in rows:
            b = by[r[unit]]; b[1] += 1; b[0] += int(bool(pred(r)))
        return list(by.values())
    ua, ub = units(rows_a, pred_a), units(rows_b, pred_b)
    na, nb = sum(u[1] for u in ua), sum(u[1] for u in ub)
    if na == 0 or nb == 0: return (float("nan"), float("nan"), float("nan"), na, nb, len(ua), len(ub))
    pa, pb = sum(u[0] for u in ua) / na, sum(u[0] for u in ub) / nb
    ea, eb = _boot_ratio(ua, reps, seed), _boot_ratio(ub, reps, seed + 1)
    rnd = random.Random(seed); rnd.shuffle(eb)  # independent pairing of the two resampled distributions
    ests = sorted(a - b for a, b in zip(ea, eb))
    return (pa - pb, ests[int(0.025 * reps)], ests[int(0.975 * reps) - 1], na, nb, len(ua), len(ub))
def clopper(k, n, alpha=0.05):
    # exact interval via the beta quantile, computed by bisection on the regularized incomplete beta
    if n == 0: return (float("nan"), float("nan"))
    lo = 0.0 if k == 0 else _beta_q(alpha / 2, k, n - k + 1)
    hi = 1.0 if k == n else _beta_q(1 - alpha / 2, k + 1, n - k)
    return (lo, hi)
def _betainc(a, b, x):
    # regularized incomplete beta by continued fraction (Numerical Recipes betacf)
    if x <= 0: return 0.0
    if x >= 1: return 1.0
    lbeta = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x)
    if x < (a + 1) / (a + b + 2): return math.exp(lbeta) * _betacf(a, b, x) / a
    return 1 - math.exp(lbeta) * _betacf(b, a, 1 - x) / b
def _betacf(a, b, x, maxit=300, eps=3e-14):
    qab, qap, qam = a + b, a + 1, a - 1; c, d = 1.0, 1 - qab * x / qap
    d = 1 / d if abs(d) > 1e-300 else 1e300; h = d
    for m in range(1, maxit + 1):
        m2 = 2 * m; aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1 + aa * d; d = 1 / d if abs(d) > 1e-300 else 1e300; c = 1 + aa / c; c = c if abs(c) > 1e-300 else 1e-300; h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1 + aa * d; d = 1 / d if abs(d) > 1e-300 else 1e300; c = 1 + aa / c; c = c if abs(c) > 1e-300 else 1e-300
        de = d * c; h *= de
        if abs(de - 1) < eps: break
    return h
def _beta_q(p, a, b):
    lo, hi = 0.0, 1.0
    for _ in range(100):
        mid = (lo + hi) / 2
        if _betainc(a, b, mid) < p: lo = mid
        else: hi = mid
    return (lo + hi) / 2


# ---- per-day-per-group table (egress_table.py until 19 Oct 2026; classifier and categories now arguments) --------

def counts(ms: list[dict], classify, cats) -> str:
    """'N=.. D=.. ..' over classify(m) for the categories in order."""
    c = collections.Counter(classify(m) for m in ms)
    return " ".join(f"{k}={c[k]}" for k in cats)


def split(ms: list[dict], classify, cats) -> str:
    """'n | category counts | fractions' for one cell; fractions only when n >= 5."""
    c = collections.Counter(classify(m) for m in ms)
    frac = " ".join(f"{k} {c[k] / len(ms):.2f}" for k in cats) if len(ms) >= 5 else ""
    return f"{len(ms)} | {counts(ms, classify, cats)} | {frac}"


def day_table(ms: list[dict], group, groups: list[str], label: str, classify, cats) -> None:
    """Markdown table, one row per day x group (groups in the given order, empty ones skipped) plus an 'all'
    row per day: measurements, the per-category counts and, from n >= 5, fractions. group(m) -> group name;
    classify(m) -> category (dnslook outcome letter, or a stage family); cats = the categories in order."""
    print(f"\n| day | {label} | msm | {' '.join(cats)} | fractions (n >= 5) |")
    print("|---|---|---|---|---|")
    for d in sorted({m["day"] for m in ms}):
        dm = [m for m in ms if m["day"] == d]
        for g in groups:
            gm = [m for m in dm if group(m) == g]
            if gm:
                print(f"| {d} | {g} | {split(gm, classify, cats)} |")
        print(f"| {d} | all | {split(dm, classify, cats)} |")

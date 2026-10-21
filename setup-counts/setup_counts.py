"""Distinct software setups behind every per-ASN cell of T1, T4 and T5.
Setup = (software_name, software_version, web_connectivity test_version): the fields
present in the derived stage tables. Coarser than the AS39028 doc's setup key (no
platform/engine/origin), so the counts are lower bounds on distinct devices.
Reports are counted too; one device submits many reports, so reports are an upper bound."""
import csv, gzip, collections, sys, os
B = os.path.dirname(os.path.abspath(__file__)) + "/.."
BLOCK = {'tcp_fail','tls_timeout','tls_reset','tls_other','tls_or_http_unsplit'}
STALL = {'http_timeout','http_reset','http_other'}
NETFAIL = {'dns_fail','tcp_fail','tls_timeout','tls_reset','tls_alert','tls_other','tls_or_http_unsplit','http_timeout','http_reset','http_other'}
out = []
def summarise(study, event, group, family, asn, period, rows, fail):
    n = len(rows); f = [r for r in rows if fail(r)]
    su = collections.Counter((r['sw'], r['sw_ver'], r['tver']) for r in rows)
    fsu = collections.Counter((r['sw'], r['sw_ver'], r['tver']) for r in f)
    top = fsu.most_common(1)[0][1] / len(f) if f else ''
    out.append([study, event, group, family, asn, period, n, len(f), len(su), len({r['report_id'] for r in rows}),
                len(fsu), len({r['report_id'] for r in f}), round(top, 2) if f else '',
                '; '.join(f"{k[0]} {k[1]} ({v})" for k, v in fsu.most_common(3))])

# ---- T1: core window 14:05-14:25 on 14 Jan 2025, set F, control-ok; baseline same window on 7/13/15 Jan
sw = {}
for d in ['2025-01-07','2025-01-13','2025-01-14','2025-01-15']:
    for r in csv.DictReader(gzip.open(f'{B}/T1/derived/stages_{d}.csv.gz','rt')):
        sw[(r['report_id'], r['input'])] = (r['sw'], r['sw_ver'], r['tver'])
cells = collections.defaultdict(list)
for r in csv.DictReader(gzip.open(f'{B}/T1/derived/window_rows.csv.gz','rt')):
    hm = r['t'][11:16]
    if not ('14:05' <= hm < '14:25') or r['nr'] != '1' or r['ctl_fail'] == '1': continue
    s = sw.get((r['report_id'], r['input']), ('?','?','?'))
    r['sw'], r['sw_ver'], r['tver'] = s
    cells[(r['asn'], 'event' if r['day'] == '2025-01-14' else 'baseline')].append(r)
for asn in ['12389','50716','35728','8331','49346','3216','25513']:
    for p in ['baseline','event']:
        summarise('T1','14 Jan 2025','set F (all inputs)','netfail',asn,p,cells[(asn,p)], lambda r: r['stage'] in NETFAIL)

# ---- T4 / T5
def t4(ev, days_before, days_after, groups, family, asns, large=False, study='T4'):
    sel = {}
    for r in csv.DictReader(open(f'{B}/T4/derived/inputs_{ev}.csv')):
        if r['https'] == '1' and r['strict'] == '1' and r['group'] in groups:
            if large and r['size_bin'] != 'ge64k': continue
            sel[r['input']] = r['group']
    fam = BLOCK if family == 'blocked' else STALL
    c = collections.defaultdict(list)
    for period, days in (('before', days_before), ('after', days_after)):
        for d in days:
            for r in csv.DictReader(gzip.open(f'{B}/T4/derived/stages_{d}.csv.gz','rt')):
                g = sel.get(r['input'])
                if g is None or r['ctl_fail'] == '1' or r['nettype'] == 'mobile' or r['asn'] not in asns: continue
                c[(g, r['asn'], period)].append(r)
    for g in groups:
        for a in asns:
            for p in ('before','after'):
                summarise(study, ev, g + (' large' if large else ''), family, a, p, c[(g,a,p)], lambda r: r['stage'] in fam)

USABLE = ['12389','25513','8402','35807','50716','8359','31200']
E1b, E1a = ['2024-11-03','2024-11-04','2024-11-05'], ['2024-11-08','2024-11-09','2024-11-10']
E2b, E2a = ['2025-06-06','2025-06-07','2025-06-08'], ['2025-06-10','2025-06-11','2025-06-12']
t4('E1', E1b, E1a, ['hetzner','ovh'], 'blocked', USABLE + ['15868','47236','48558','50544','12668','9123','24955','42610'])
t4('E2', E2b, E2a, ['hetzner','cloudflare','ovh','digitalocean'], 'stall', USABLE + ['41668','16345','24955','48524','35728','207235','210616','34533','39812'])
t4('E2', E2b, E2a, ['cloudflare','hetzner','digitalocean'], 'stall', USABLE, large=True, study='T5')

with open('setup_counts.csv','w',newline='') as fh:
    w = csv.writer(fh)
    w.writerow(['study','event','group','family','asn','period','n_ctl_ok','n_fail','setups','reports','setups_with_fail','reports_with_fail','top_setup_share_of_fails','top_failing_setups'])
    w.writerows(out)
print(len(out), 'rows')

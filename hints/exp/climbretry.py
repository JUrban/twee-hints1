#!/usr/bin/env python3
"""climbretry.py [--start 'YYYY-MM-DD HH:MM'] [--dir loops/UL]: exp78's reading (24 Nov, notes/2026-11-24-cond-replay.md).

loop.py --retry-climb appends (epoch, goal) to DIR/climbretry.tsv when a climbed goal gets its fresh run. This reads
DIR/r5/results.tsv rows of the loop instance started at START (its t= column counts seconds from the start; rows of
earlier instances are skipped by the first reset of t when read from the end) and, for each retried goal, the rows
from its retry on: runs, CPU s (the seconds column), proved or not, and which level or member proved it. Prints the
totals, proofs per CPU h of those runs, and the same for all of the instance's rows."""
import collections, os, re, sys, time

a = sys.argv[1:]
D = a[a.index('--dir') + 1] if '--dir' in a else '/project/hintwork/loops/UL'
st = a[a.index('--start') + 1] if '--start' in a else '2026-11-24 01:15'
t0 = time.mktime(time.strptime(st, '%Y-%m-%d %H:%M'))
rows = []
prev = None
for l in reversed(open(os.path.join(D, 'r5', 'results.tsv')).read().splitlines()):
    m = re.search(r'\tt=(\d+)', l)
    if not m:
        continue
    t = int(m.group(1))
    if prev is not None and t > prev + 60:
        break
    prev = t
    w = l.split('\t')
    try:
        sec = float(w[2])
    except ValueError:
        sec = 0.0
    rows.append((t0 + t, w[0], w[1], sec, w[4] if len(w) > 4 else ''))
rows.reverse()
retry = {}
for l in open(os.path.join(D, 'climbretry.tsv')):
    w = l.split()
    if len(w) >= 2 and float(w[0]) >= t0 - 60:
        retry.setdefault(w[1], float(w[0]))
c = collections.Counter(); by = collections.Counter(); proved = []
for g, rt in retry.items():
    rs = [r for r in rows if r[1] == g and r[0] >= rt - 30]
    c['goals'] += 1; c['runs'] += len(rs); c['cpu'] += sum(r[3] for r in rs)
    th = [r for r in rs if r[2] == 'THM']
    if th:
        c['proved'] += 1; by[th[0][4]] += 1; proved.append(g)
allc = sum(r[3] for r in rows); allp = sum(1 for r in rows if r[2] == 'THM')
print(f'instance from {st}: {len(rows)} runs, {allp} THM, {allc / 3600:.2f} CPU h, {allp / (allc / 3600) if allc else 0:.2f} per CPU h')
print(f'climb retries: {c["goals"]} goals, {c["runs"]} runs after the retry, {c["cpu"] / 3600:.2f} CPU h, proved {c["proved"]}'
      f' ({c["proved"] / (c["cpu"] / 3600) if c["cpu"] else 0:.2f} per CPU h); by: {dict(by)}')
if proved:
    print('  proved:', ' '.join(sorted(proved)))

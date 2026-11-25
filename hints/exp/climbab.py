#!/usr/bin/env python3
"""climbab.py [DIR] [--from LINE] (default loops/CLS71): the --final-only-ab reading (24 Nov, notes/2026-11-23-climber-restart.md).

The climbs the current climber instance finished (DIR's log after its last 'reloaded' line), split by arm (bit 2 of
crc32 of the target's name: final-only, else the full climb) and by kind (a target in sets/cls71re is a re-climb):
finished, proved, CPU h (climb.tsv seconds of the target's runs from the instance's first row on), proofs per CPU h. --from LINE: from that log line (1-based) on instead, across restarts (the 08:59
instance, the first with --final-only-ab, starts at line 1047)."""
import collections, re, sys, zlib
H = '/project/hintwork'
A = sys.argv[1:]
FROM = int(A[A.index('--from') + 1]) if '--from' in A else 0
A = [x for i, x in enumerate(A) if x != '--from' and (i == 0 or A[i - 1] != '--from')]
D = A[0] if A else f'{H}/loops/CLS71'
log = f'{H}/loops/{D.rstrip("/").split("/")[-1]}.log'
L = open(log).read().splitlines()
i = FROM - 1 if FROM else max(n for n, l in enumerate(L) if l.startswith('reloaded'))
fin = {}
for l in L[i:]:
    m = re.match(r'(\S+__goal_\d+) (THM|NO) ', l)
    if m:
        fin[m.group(1)] = m.group(2)
RE = {l.strip() for l in open(f'{H}/sets/cls71re') if l.strip()}
# (25 Nov) a target's CPU: all its climb.tsv rows from the instance's first row on (the first row of a target new to
# it). Before, a re-climb counted only its r1-tagged rows when it had any (so the climbing arm's re-climbs left out
# their final, tagged 'final') and else every row (so the final-only arm's re-climbs took in the earlier climb's runs)
T = open(f'{D}/climb.tsv').read().splitlines()
first = {}
for n, l in enumerate(T):
    first.setdefault(l.split('\t', 1)[0], n)
T0 = min((first[g] for g in fin if g not in RE and g in first), default=0)
sec = collections.Counter()
for l in T[T0:]:
    w = l.split('\t')
    try:
        sec[w[0]] += float(w[5])
    except (ValueError, IndexError):
        continue
arm = lambda g: 'final-only' if (zlib.crc32(g.encode()) >> 2) % 2 else 'climb'
print(f'{log}: instance from line {i + 1} (climb.tsv row {T0 + 1}), {len(fin)} climbs finished')
for kind in ('new', 're-climb'):
    for a in ('climb', 'final-only'):
        gs = [g for g in fin if arm(g) == a and ((g in RE) == (kind == 're-climb'))]
        cpu = sum(sec[g] for g in gs) / 3600
        th = sorted(g for g in gs if fin[g] == 'THM')
        print(f'  {kind:8s} {a:10s} finished {len(gs):4d} proved {len(th):3d} CPU h {cpu:6.2f} per CPU h '
              f'{len(th) / cpu if cpu else 0:.2f}  {" ".join(th)}')

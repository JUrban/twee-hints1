#!/usr/bin/env python3
"""climbab.py [DIR] [--from LINE] (default loops/CLS71): the --final-only-ab reading (24 Nov, notes/2026-11-23-climber-restart.md).

The climbs the current climber instance finished (DIR's log after its last 'reloaded' line), split by arm (bit 2 of
crc32 of the target's name: final-only, else the full climb) and by kind (a target in sets/cls71re is a re-climb):
finished, proved, CPU h (climb.tsv seconds of the instance's runs: tags with the r1 prefix for a re-climb, the others
for a new target), proofs per CPU h. --from LINE: from that log line (1-based) on instead, across restarts (the 08:59
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
sec = collections.defaultdict(collections.Counter)
for l in open(f'{D}/climb.tsv'):
    w = l.rstrip('\n').split('\t')
    try:
        s = float(w[5])
    except (ValueError, IndexError):
        continue
    sec[w[0]]['r1' if w[1].startswith('r1') else 'r0'] += s
arm = lambda g: 'final-only' if (zlib.crc32(g.encode()) >> 2) % 2 else 'climb'
print(f'{log}: instance from line {i + 1}, {len(fin)} climbs finished')
for kind in ('new', 're-climb'):
    for a in ('climb', 'final-only'):
        gs = [g for g in fin if arm(g) == a and ((g in RE) == (kind == 're-climb'))]
        cpu = sum(sec[g]['r1' if kind == 're-climb' and sec[g]['r1'] else 'r0'] for g in gs) / 3600
        th = sorted(g for g in gs if fin[g] == 'THM')
        print(f'  {kind:8s} {a:10s} finished {len(gs):4d} proved {len(th):3d} CPU h {cpu:6.2f} per CPU h '
              f'{len(th) / cpu if cpu else 0:.2f}  {" ".join(th)}')

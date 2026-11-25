#!/bin/bash
# (25 Nov 10:23) exp85d: stage 1 on medium-hard goals (notes/2026-11-25-precedence-portfolio.md, "exp85d"). exp85b's
# window (1-5 abstract s) was at the work measure's floor and every order proved every goal. Here: exp85's 120 hard
# candidates (their captures in loops/P85C/cap, context t0758 without them).
# 1. Pre-pass: orders 0 and 60 at --abstract 40 (80,000 pairs), --cpu 120 safety cap, -j 10 (loops/P85C/pre40.tsv).
# 2. Dev set: goals whose lesser work of the two lies in [10000, 40000] pairs (5-20 abstract s); at most 30 (seed 85).
# 3. Replay: all 121 orders at --abstract 40 (twice the window's top), -j 10 (loops/P85C/replay40.tsv).
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
cd /project/hintwork
A=P85C; O=/project/twee/hints/exp/sets
[ -e loops/$A/pre40.tsv ] && { echo "loops/$A/pre40.tsv exists" >> loops/EXP85.pids; exit 1; }
echo "exp85d pre-pass start $(date '+%d %T')" >> loops/EXP85.pids
python3 -u /project/twee/hints/exp/prec_replay.py loops/$A/cap loops/$A/pre40.tsv --goals sets/exp85.cand --orders $O/exp85.pre.orders \
  -j 10 --cpu 120 --abstract 40 >> loops/EXP85.pids 2>&1
python3 - loops/$A <<'PY' >> loops/EXP85.pids
import collections, random, sys
d = sys.argv[1]
w = collections.defaultdict(dict)
for l in open(f'{d}/pre40.tsv'):
    x = l.rstrip('\n').split('\t')
    if x[2] == 'THM' and x[5] != '-':
        w[x[0]][x[1]] = int(x[5])
best = {g: min(v.values()) for g, v in w.items()}
dev = sorted(g for g, b in best.items() if 10000 <= b <= 40000)
n = len(dev)
if len(dev) > 30:
    random.seed(85); dev = sorted(random.sample(dev, 30))
open(f'{d}/dev40.txt', 'w').write(''.join(g + '\n' for g in dev))
print('exp85d pre-pass: proved', len(best), 'of 120; under 10000', sum(b < 10000 for b in best.values()), 'in [10000, 40000]', n,
      'over 40000', sum(b > 40000 for b in best.values()), 'dev', len(dev), flush=True)
PY
echo "exp85d replay start $(date '+%d %T')" >> loops/EXP85.pids
python3 -u /project/twee/hints/exp/prec_replay.py loops/$A/cap loops/$A/replay40.tsv --goals loops/$A/dev40.txt --orders $O/exp85.orders \
  -j 10 --cpu 120 --abstract 40 >> loops/EXP85.pids 2>&1
echo "exp85d done $(date '+%d %T')" >> loops/EXP85.pids

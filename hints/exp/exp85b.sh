#!/bin/bash
# (25 Nov 09:22) exp85b: stage 1 again on goals of the right difficulty (notes/2026-11-25-precedence-portfolio.md,
# "exp85b"). The user: the dev set was too hard for reliable statistics (BliStr keeps problems whose best value lies in
# [c_min, c_max]). exp85's 50 dev goals: 19 failed even the 40 s capture; at 10,000 pairs 9 of the first 14 failed
# under all 121 orders.
# 1. 300 random trusted goals (sets/exp85b.cand, seed 851, none of exp85's), captured as in exp85 (loops/P85D: the
#    context t0758.trusted without them, CLQ83's true.tsv, fillhints/, sketches/; CLQ83's final at 40 CPU s; -j 5).
# 2. Pre-pass: orders 0 (default) and 60 (exp/sets/exp85.pre.orders) at --abstract 20 (40,000 pairs), -j 5.
# 3. Dev set: goals whose lesser work of the two lies in [500, 10000] pairs; at most 60 (seed 85).
# 4. Replay: all 121 orders at --abstract 10 (20,000 pairs: twice the selection's top), --cpu 60 safety cap, -j 5.
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
cd /project/hintwork
A=P85D
[ -e loops/$A ] && { echo "loops/$A exists" >> loops/EXP85.pids; exit 1; }
python3 - loops/TRUSTNOW/t0758.trusted loops/$A sets/exp85b.cand <<'PY' >> loops/EXP85.pids
import os, sys, shutil
tr, d, cf = sys.argv[1:4]
cand = {l.strip() for l in open(cf) if l.strip()}
os.makedirs(f'{d}/hints')
T = [l.split()[0] for l in open(tr) if l.strip() and l.split()[0] not in cand]
open(f'{d}/solved.tsv', 'w').write(''.join(f'{g}\t0\t0.0\n' for g in T))
n = 0
for g in T:
    s = f'/project/hintwork/loops/UL/hints/{g}'
    if os.path.exists(s):
        shutil.copyfile(s, f'{d}/hints/{g}'); n += 1
shutil.copyfile('/project/hintwork/loops/CLQ83/true.tsv', f'{d}/true.tsv')
for s in ('fillhints', 'sketches'):
    shutil.copytree(f'/project/hintwork/loops/CLQ83/{s}', f'{d}/{s}')
print(d, len(T), 'solved', n, 'hints; candidates left out', len(cand), flush=True)
PY
echo "exp85b capture start $(date '+%d %T')" >> loops/EXP85.pids
CAPTURE_DIR=/project/hintwork/loops/$A/cap python3 -u /project/twee/hints/climb.py sets/all loops/$A --targets sets/exp85b.cand \
  --m 8 --knn 8 --theories 4 --theory-explore 2 --theory-lemmas 10 --updown --up-single --weaken 4 --chain --fill 3 \
  --min-sketch-steps 30 --runs 0 --sketch-time 5 --final-time 160 --final-cpu 40 -j 5 -- \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 30 --lemma-knn 400 --lemma-subsets --lemma-after --pool original --twee /project/twee/hints/exp/twee_capture.py --wall-factor 15 \
  --args="--abstract-time 2000 --no-eqhint-consider --conditional-encoding fresh" > loops/$A.log 2>&1
echo "exp85b capture done $(date '+%d %T')" >> loops/EXP85.pids
O=/project/twee/hints/exp/sets
python3 -u /project/twee/hints/exp/prec_replay.py loops/$A/cap loops/$A/pre.tsv --goals sets/exp85b.cand --orders $O/exp85.pre.orders \
  -j 5 --cpu 60 --abstract 20 >> loops/EXP85.pids 2>&1
echo "exp85b pre-pass done $(date '+%d %T')" >> loops/EXP85.pids
python3 - loops/$A <<'PY' >> loops/EXP85.pids
import collections, random, sys
d = sys.argv[1]
w = collections.defaultdict(dict)
for l in open(f'{d}/pre.tsv'):
    x = l.rstrip('\n').split('\t')
    if x[2] == 'THM' and x[5] != '-':
        w[x[0]][x[1]] = int(x[5])
best = {g: min(v.values()) for g, v in w.items()}
dev = sorted(g for g, b in best.items() if 500 <= b <= 10000)
n = len(dev)
if len(dev) > 60:
    random.seed(85); dev = sorted(random.sample(dev, 60))
open(f'{d}/dev.txt', 'w').write(''.join(g + '\n' for g in dev))
print('pre-pass: proved', len(best), 'in [500, 10000]', n, 'under 500', sum(b < 500 for b in best.values()),
      'over 10000', sum(b > 10000 for b in best.values()), 'dev', len(dev), flush=True)
PY
echo "exp85b replay start $(date '+%d %T')" >> loops/EXP85.pids
python3 -u /project/twee/hints/exp/prec_replay.py loops/$A/cap loops/$A/replay.tsv --goals loops/$A/dev.txt --orders $O/exp85.orders \
  -j 5 --cpu 60 --abstract 10 >> loops/EXP85.pids 2>&1
echo "exp85b done $(date '+%d %T')" >> loops/EXP85.pids

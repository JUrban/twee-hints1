#!/bin/bash
# (25 Nov 08:07) exp85: a precedence portfolio (notes/2026-11-25-precedence-portfolio.md). The user: Veroff tries all
# symbol precedences (120?), maybe reducible to the most complementary few; do not fix m, ld, rd, e, evaluate.
# 1. Capture (loops/P85C): CLQ83's final (clq83.sh's options, set mode, --final-cpu 40, -j 4) on 120 candidates
#    (sets/exp85.cand: 40 of ul84's L1 proofs, 80 climber-proved targets, seed 85), in t0758.trusted's context minus the
#    candidates (their solved rows and hints left out), with CLQ83's true.tsv, fillhints/, sketches/; --twee is
#    exp/twee_capture.py, which keeps each run's problem, hints and rule-goal files and arguments (loops/P85C/cap).
# 2. Dev set: candidates whose captured final proved with at least 1 CPU s, or failed; at most 50 (seed 85).
# 3. Replay (exp/prec_replay.py, loops/P85C/replay.tsv): each dev goal's captured final under 121 precedences
#    (exp/sets/exp85.orders: 0 = twee's default; 1-120 = each order of a,k,l,r,t once, m,ld,rd,e at random places),
#    --max-cpu 10, -j 5.
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
cd /project/hintwork
A=P85C
[ -e loops/$A ] && { echo "loops/$A exists" >> loops/EXP85.pids; exit 1; }
python3 - loops/TRUSTNOW/t0758.trusted loops/$A sets/exp85.cand <<'PY' >> loops/EXP85.pids
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
echo "capture start $(date '+%d %T')" >> loops/EXP85.pids
CAPTURE_DIR=/project/hintwork/loops/$A/cap python3 -u /project/twee/hints/climb.py sets/all loops/$A --targets sets/exp85.cand \
  --m 8 --knn 8 --theories 4 --theory-explore 2 --theory-lemmas 10 --updown --up-single --weaken 4 --chain --fill 3 \
  --min-sketch-steps 30 --runs 0 --sketch-time 5 --final-time 160 --final-cpu 40 -j 4 -- \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 30 --lemma-knn 400 --lemma-subsets --lemma-after --pool original --twee /project/twee/hints/exp/twee_capture.py --wall-factor 15 \
  --args="--abstract-time 2000 --no-eqhint-consider --conditional-encoding fresh" > loops/$A.log 2>&1
echo "capture done $(date '+%d %T')" >> loops/EXP85.pids
python3 - loops/$A <<'PY' >> loops/EXP85.pids
import random, sys
d = sys.argv[1]
fin = {}
for l in open(f'{d}/climb.tsv'):
    w = l.rstrip('\n').split('\t')
    if len(w) > 5 and w[1] == 'final' and w[0] not in fin:
        fin[w[0]] = (w[3], float(w[5]))
dev = sorted(g for g, (r, s) in fin.items() if r != 'THM' or s >= 1.0)
if len(dev) > 50:
    random.seed(85); dev = sorted(random.sample(dev, 50))
open(f'{d}/dev.txt', 'w').write(''.join(g + '\n' for g in dev))
print('finals', len(fin), 'proved', sum(r == 'THM' for r, _ in fin.values()), 'dev', len(dev), flush=True)
PY
echo "replay start $(date '+%d %T')" >> loops/EXP85.pids
python3 -u /project/twee/hints/exp/prec_replay.py loops/$A/cap loops/$A/replay.tsv --goals loops/$A/dev.txt \
  --orders /project/twee/hints/exp/sets/exp85.orders -j 5 --cpu 10 >> loops/EXP85.pids 2>&1
echo "exp85 done $(date '+%d %T')" >> loops/EXP85.pids

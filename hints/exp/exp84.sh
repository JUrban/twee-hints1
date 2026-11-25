#!/bin/bash
# (25 Nov 04:18) exp84: other KBO symbol precedences on the quick finals' failures (notes/2026-11-25-precedences.md).
# Veroff tries many symbol precedences on a subgoal; production, CLS71 and CLQ83 only ever use twee's default.
# 100 targets (sets/exp84.targets, seed 84) whose 40 CPU s CLQ83 final failed and which are still unsolved, each
# rerun with CLQ83's final (clq83.sh's options, --runs 0, --final-cpu 40, set mode with --targets) in five arms:
#   P84O0  twee's default precedence: the control (the context has grown since CLQ83's run)
#   P84Ok  ordering k = 1..4: loop.py --p9-orders 5 --p9-order-offset k-1 (no cascade: k = (1 + offset) mod 5),
#          twee --precedence with a fixed pseudo-random permutation of the problem's symbols (loop.py p9_precedence)
# Context: loops/TRUSTNOW/t0238.trusted with production's hints, CLQ83's true.tsv, fillhints/ and sketches/. -j 1 each.
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
cd /project/hintwork
for k in 0 1 2 3 4; do [ -e loops/P84O$k ] && { echo "loops/P84O$k exists" >> loops/EXP84.pids; exit 1; }; done
for k in 0 1 2 3 4; do
  A=P84O$k
  python3 - loops/TRUSTNOW/t0238.trusted loops/$A <<'PY' >> loops/EXP84.pids
import os, sys, shutil
tr, d = sys.argv[1], sys.argv[2]
os.makedirs(f'{d}/hints')
T = [l.split()[0] for l in open(tr) if l.strip()]
open(f'{d}/solved.tsv', 'w').write(''.join(f'{g}\t0\t0.0\n' for g in T))
n = 0
for g in T:
    s = f'/project/hintwork/loops/UL/hints/{g}'
    if os.path.exists(s):
        shutil.copyfile(s, f'{d}/hints/{g}'); n += 1
for f in ('true.tsv',):
    shutil.copyfile(f'/project/hintwork/loops/CLQ83/{f}', f'{d}/{f}')
for s in ('fillhints', 'sketches'):
    shutil.copytree(f'/project/hintwork/loops/CLQ83/{s}', f'{d}/{s}')
print(d, len(T), 'solved', n, 'hints', flush=True)
PY
  ORD=""; [ $k -gt 0 ] && ORD="--p9-orders 5 --p9-order-offset $((k - 1))"
  nohup python3 -u /project/twee/hints/climb.py sets/all loops/$A --targets sets/exp84.targets \
    --m 8 --knn 8 --theories 4 --theory-explore 2 --theory-lemmas 10 --updown --up-single --weaken 4 --chain --fill 3 \
    --min-sketch-steps 30 --runs 0 --sketch-time 5 --final-time 160 --final-cpu 40 -j 1 -- \
    --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
    --lemmas 30 --lemma-knn 400 --lemma-subsets --lemma-after --pool original --twee /project/bin/twee-pg61 --wall-factor 15 \
    $ORD --args="--abstract-time 2000 --no-eqhint-consider --conditional-encoding fresh" > loops/$A.log 2>&1 &
  echo "$A $! $(date '+%d %T')" >> loops/EXP84.pids
done
wait
echo "exp84 done $(date '+%d %T')" >> loops/EXP84.pids

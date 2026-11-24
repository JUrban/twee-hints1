#!/bin/bash
# (24 Nov 00:24) exp76: do CLS71's stalled goals need longer finals, and do the climb hints matter at that length?
# (notes/2026-11-24-cond-replay.md, "exp76"). CLS71 (abs/cls71.sh) ends each climb with a 20 s final; 0 real proofs in
# 119 finals by 00:40. exp67's arm B made its 7 real proofs in 160 s finals, at 7-380 CPU s each. Targets: 30 of
# CLS71's unsolved targets whose 20 s final failed (sets/exp76, exp/sets/exp76; seed 76, local heads left out).
# Two final-only climbs (--runs 0) with CLS71's lemma lists (30 siblings, 400 kNN), 160 abstract s:
#   F76S: CLS71's sketches/ and fillhints/ copied at launch (climb.py reloads them as each original's climb hints);
#   F76C: none (the pool hints and the lemmas alone: a long production-like run).
# Context: the newest loops/TRUSTNOW trusted set at launch, production's hints. -j 2 each. Starts when exp67's arms
# end ("exp67 done" in loops/EXP67.pids), so the CPU stays near its level. Proofs are merged into loops/UL at the end.
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
cd /project/hintwork
END=$(date -d "2026-11-24 10:00" +%s)
until grep -q "^exp67 done" loops/EXP67.pids || [ $(date +%s) -gt $END ]; do sleep 60; done
for A in F76S F76C; do [ -e loops/$A ] && { echo "loops/$A exists"; exit 1; }; done
TR=$(ls -t loops/TRUSTNOW/t*.trusted | head -1)
echo "targets sets/exp76 ($(wc -l < sets/exp76)) context $TR $(date '+%d %T')" > loops/EXP76.pids
CTX="--model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory --lemma-subsets --lemma-after --pool original --twee /project/bin/twee-pg61 --wall-factor 15"
PIDS=""
for A in F76S F76C; do
  python3 - $TR loops/$A $A <<'PY' >> loops/EXP76.pids
import os, sys, shutil
tr, d, arm = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(f'{d}/hints')
T = [l.split()[0] for l in open(tr) if l.strip()]
open(f'{d}/solved.tsv', 'w').write(''.join(f'{g}\t0\t0.0\n' for g in T))
n = 0
for g in T:
    s = f'/project/hintwork/loops/UL/hints/{g}'
    if os.path.exists(s):
        shutil.copyfile(s, f'{d}/hints/{g}'); n += 1
x = ''
if arm == 'F76S':
    for sub in ('sketches', 'fillhints'):
        shutil.copytree(f'/project/hintwork/loops/CLS71/{sub}', f'{d}/{sub}')
    x = f"; CLS71 sketches of {len(os.listdir(f'{d}/sketches'))} targets"
print(d, len(T), 'solved', n, 'hints' + x)
PY
  nohup python3 -u /project/twee/hints/climb.py sets/all loops/$A --targets sets/exp76 --m 8 --knn 8 --theories 4 \
    --theory-explore 2 --theory-lemmas 10 --updown --up-single --weaken 4 --chain --min-sketch-steps 30 --runs 0 \
    --final-time 160 -j ${J:-2} -- $CTX --lemmas 30 --lemma-knn 400 \
    --args="--abstract-time 2000 --no-eqhint-consider" > loops/$A.log 2>&1 &
  echo "$A $! $(date '+%d %T')" >> loops/EXP76.pids
  PIDS="$PIDS $!"
done
wait
for A in F76S F76C; do
  flock cond/merge.lock python3 /project/twee/hints/merge.py loops/UL loops/$A 2>&1 | tail -1 | sed "s/^/$(date '+%d %T') $A /" >> loops/EXP76.pids
done
echo "exp76 done $(date '+%d %T')" >> loops/EXP76.pids

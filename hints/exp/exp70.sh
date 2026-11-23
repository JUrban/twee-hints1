#!/bin/bash
# (23 Nov 23:04) exp70: a second Veroff round on exp69's 9 key goals (notes/2026-11-23-climber-restart.md, "exp70"). CLK69
# climbed them once (0 of 9; its fills, 3 s each, proved 93 of 219 gaps). Both arms start from CLK69's sketch hints
# and fill hints (sketches/, fillhints/; reloaded by climb.py as round 1's hints) and a fresh trusted context, with
# CLK69's setting otherwise:
#   K70F: gap filling 10 times longer (--fill 30, at most 300 CPU s per fill run);
#   K70R: CLK69's --fill 3 (the round-2 control: what reloading the sketches alone does).
# true.tsv is not copied: a climber started before 23 Nov 23:03 (climb.py's install) writes no premise record (fillprem.tsv), so the
# arms prove their own, recorded. --true-max 200 in both (CLK69's 60 was not reached). -j 1 each. Real proofs are
# merged into loops/UL every 10 minutes under cond/merge.lock.
# Usage: TRUSTED=loops/TRUSTNOW/tHHMM.trusted bash abs/exp70.sh
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
cd /project/hintwork
TR=${TRUSTED:?}
for A in K70F K70R; do [ -e loops/$A ] && { echo "loops/$A exists"; exit 1; }; done
echo "targets loops/EXP69.targets ($(wc -l < loops/EXP69.targets)) context $TR $(date '+%d %T')" > loops/EXP70.pids
CTX="--model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory --lemma-subsets --lemma-after --pool original --twee /project/bin/twee-pg61 --wall-factor 15"
PIDS=""
for A in K70F K70R; do
  case $A in K70F) FILL=30;; K70R) FILL=3;; esac
  python3 - $TR loops/$A <<'PY' >> loops/EXP70.pids
import os, sys, shutil
tr, d = sys.argv[1], sys.argv[2]
os.makedirs(f'{d}/hints')
T = [l.split()[0] for l in open(tr) if l.strip()]
with open(f'{d}/solved.tsv', 'w') as f:
    for g in T:
        f.write(f'{g}\t0\t0.0\n')
n = 0
for g in T:
    s = f'/project/hintwork/loops/UL/hints/{g}'
    if os.path.exists(s):
        shutil.copyfile(s, f'{d}/hints/{g}'); n += 1
for sub in ('sketches', 'fillhints'):
    shutil.copytree(f'/project/hintwork/loops/CLK69/{sub}', f'{d}/{sub}')
print(d, len(T), 'solved', n, 'hints; CLK69 sketches', len(os.listdir(f'{d}/sketches')), 'fillhints', len(os.listdir(f'{d}/fillhints')))
PY
  nohup python3 -u /project/twee/hints/climb.py sets/all loops/$A --targets loops/EXP69.targets --m 8 --knn 8 --theories 4 \
    --theory-explore 2 --theory-lemmas 10 --updown --up-single --weaken 12 --chain --fill $FILL --true-max 200 \
    --min-sketch-steps 30 --runs 24 --sketch-time 5 --final-time 160 -j ${J:-1} -- $CTX --lemmas 30 --lemma-knn 400 \
    --args="--abstract-time 2000 --no-eqhint-consider" > loops/$A.log 2>&1 &
  echo "$A $! fill $FILL $(date '+%d %T')" >> loops/EXP70.pids
  PIDS="$PIDS $!"
done
alive() { for p in $PIDS; do kill -0 $p 2>/dev/null && return 0; done; return 1; }
while alive; do
  sleep 600
  for A in K70F K70R; do
    flock cond/merge.lock python3 /project/twee/hints/merge.py loops/UL loops/$A 2>&1 | tail -1 | sed "s/^/$(date '+%d %T') $A /" >> loops/EXP70.merge
  done
done
for A in K70F K70R; do
  flock cond/merge.lock python3 /project/twee/hints/merge.py loops/UL loops/$A 2>&1 | tail -1 | sed "s/^/$(date '+%d %T') final $A /" >> loops/EXP70.merge
done
echo "exp70 done $(date '+%d %T')" >> loops/EXP70.pids

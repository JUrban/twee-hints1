#!/bin/bash
# (23 Nov 23:28) exp67's controls, CPU-matched (notes/2026-11-23-climber-restart.md, "The controls, corrected"). CC67 and
# CC67B (abs/exp67c.sh, exp67d.sh, 22:56-23:27) set their one run per head to the arm's CPU per finished head / 1.07,
# exp65's CPU per abstract second; on these heads it is 2.3-2.5 for long runs (3.1-3.6 in the arms' 160 s finals),
# so each head got about 2.3 times the arm's CPU. Now the run's limit is CPU itself: climb.py --final-cpu (twee
# --max-cpu) = the arm's CPU s per finished head at launch, --final-time 3000 (abstract, not reached). Otherwise as
# exp67c/d: the same 91 heads (loops/EXP67.heads) and context (t1854.trusted, production's hints), no sketches.
#   CC67C: arm A's lemmas (6 siblings, 30 kNN), CPU of CLA67;  CC67D: arm B's (30, 400), CPU of CLB67.
# -j 4 each.
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
cd /project/hintwork
for A in CC67C CC67D; do [ -e loops/$A ] && { echo "loops/$A exists" >> loops/EXP67.pids; exit 1; }; done
CTX="--model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory --lemma-subsets --lemma-after --pool original --twee /project/bin/twee-pg61 --wall-factor 15"
PIDS=""
for A in CC67C CC67D; do
  case $A in CC67C) ARM=CLA67; LEM="--lemmas 6 --lemma-knn 30";; CC67D) ARM=CLB67; LEM="--lemmas 30 --lemma-knn 400";; esac
  FC=$(python3 - $ARM <<'PY'
import sys
d = sys.argv[1]; cpu = 0; fin = set()
for l in open(f'loops/{d}/climb.tsv'):
    w = l.rstrip('\n').split('\t')
    try: cpu += float(w[5])
    except (IndexError, ValueError): pass
    if w[1:2] == ['final']: fin.add(w[0])
own = {l.split('\t')[0] for l in open(f'loops/{d}/solved.tsv') if l.split('\t')[1:2] == ['1']}
print(round(cpu / max(len(fin | own), 1)))
PY
)
  echo "$A final CPU $FC s ($ARM's CPU per finished head) $(date '+%d %T')" >> loops/EXP67.pids
  python3 - loops/TRUSTNOW/t1854.trusted loops/$A <<'PY' >> loops/EXP67.pids
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
print(d, len(T), 'solved', n, 'hints')
PY
  nohup python3 -u /project/twee/hints/climb.py sets/all loops/$A --targets loops/EXP67.heads --m 8 --knn 8 --theories 4 \
    --theory-explore 2 --theory-lemmas 10 --updown --up-single --weaken 4 --chain --min-sketch-steps 30 --runs 0 \
    --final-time 3000 --final-cpu $FC -j ${J:-4} -- $CTX $LEM --args="--abstract-time 2000 --no-eqhint-consider" > loops/$A.log 2>&1 &
  echo "$A $! $(date '+%d %T')" >> loops/EXP67.pids
  PIDS="$PIDS $!"
done
wait
echo "CC67C/CC67D done $(date '+%d %T')" >> loops/EXP67.pids

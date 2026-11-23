#!/bin/bash
# (23 Nov 18:57) exp67: two climber settings, paired, on the same frozen heads (notes/2026-11-23-climber-restart.md,
# "exp67"). The heads of TRUSTED (exp/heads.py), each arm a set-mode climb (climb.py --targets) from the same context:
# solved.tsv = the trusted goals, hints = their production hints (copied, so nothing is written into loops/UL).
#   CLA67: abs/clhl3.sh's setting (6 sibling and 30 kNN lemmas);
#   CLB67: the same with 30 sibling and 400 kNN lemmas (the plain sweeps' finding: size beats order).
# Both: 24 sketch runs of 5 s, a 160 s final run, -j ${J:-2}. Started beside exp65 on the user's leave for more CPUs
# while climbing (23 Nov). Usage: TRUSTED=loops/TRUSTNOW/tHHMM.trusted bash abs/exp67.sh
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
cd /project/hintwork
TR=${TRUSTED:?}
for a in CLA67 CLB67; do [ -e loops/$a ] && { echo "loops/$a exists"; exit 1; }; done
python3 /project/twee/hints/exp/heads.py $TR --set sets/all | awk '{print $1}' | grep __goal_ > loops/EXP67.heads
echo "heads $(wc -l < loops/EXP67.heads) from $TR $(date '+%d %T')" > loops/EXP67.pids
for a in CLA67 CLB67; do
  python3 - $TR loops/$a <<'PY'
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
print(d, len(T), 'solved', n, 'hints')
PY
done >> loops/EXP67.pids
CTX="--model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory --lemma-subsets --lemma-after --pool original --twee /project/bin/twee-pg61 --wall-factor 15"
CL="--targets loops/EXP67.heads --m 8 --knn 8 --theories 4 --theory-explore 2 --theory-lemmas 10 --updown --up-single --weaken 4 --chain --fill 3 --min-sketch-steps 30 --runs 24 --sketch-time 5 --final-time 160 -j ${J:-2}"
nohup python3 -u /project/twee/hints/climb.py sets/all loops/CLA67 $CL -- $CTX --lemmas 6 --lemma-knn 30 \
  --args="--abstract-time 2000 --no-eqhint-consider" > loops/CLA67.log 2>&1 &
echo "CLA67 $! $(date '+%d %T')" >> loops/EXP67.pids
nohup python3 -u /project/twee/hints/climb.py sets/all loops/CLB67 $CL -- $CTX --lemmas 30 --lemma-knn 400 \
  --args="--abstract-time 2000 --no-eqhint-consider" > loops/CLB67.log 2>&1 &
echo "CLB67 $! $(date '+%d %T')" >> loops/EXP67.pids
wait
echo "exp67 done $(date '+%d %T')" >> loops/EXP67.pids

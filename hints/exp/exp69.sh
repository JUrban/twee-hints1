#!/bin/bash
# (23 Nov 21:21) exp69: climb the key goals of the climbers' conditional proofs (notes/2026-11-23-climber-restart.md,
# "exp69"). Most heads climbed today have a 5 s sketch proof with a single assumption, nearly always an unsolved goal X
# of another original (assume_knn). exp/keylemmas.py ranks those X by the unsolved targets they unlock; the 9 with 2
# or more (loops/EXP69.targets, exp/sets/key69): Kproperties_1 332 and nil4_19K 394 unlock 4 each. 7 of the 9 are not
# heads, but 1-9 goals behind one; nothing climbed them before. Veroff's sketches: prove the assumption, then the target.
# Set mode (climb.py --targets) from TRUSTED and a copy of production's hints, CLHL4's setting (30 siblings, 400 kNN,
# --weaken 12), 1 climb at a time (-j ${J:-1}). Its real proofs are merged into loops/UL every 10 minutes
# (merge.py under cond/merge.lock), so the heads they unlock get rerun by production and the climbers.
# Usage: TRUSTED=loops/TRUSTNOW/tHHMM.trusted TARGETS=FILE bash abs/exp69.sh
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
cd /project/hintwork
TR=${TRUSTED:?}; TG=${TARGETS:?}
[ -e loops/CLK69 ] && { echo "loops/CLK69 exists"; exit 1; }
cp $TG loops/EXP69.targets
echo "targets $(wc -l < loops/EXP69.targets) context $TR $(date '+%d %T')" > loops/EXP69.pids
python3 - $TR loops/CLK69 <<'PY' >> loops/EXP69.pids
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
CTX="--model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory --lemma-subsets --lemma-after --pool original --twee /project/bin/twee-pg61 --wall-factor 15"
nohup python3 -u /project/twee/hints/climb.py sets/all loops/CLK69 --targets loops/EXP69.targets --m 8 --knn 8 --theories 4 \
  --theory-explore 2 --theory-lemmas 10 --updown --up-single --weaken 12 --chain --fill 3 --min-sketch-steps 30 --runs 24 \
  --sketch-time 5 --final-time 160 -j ${J:-1} -- $CTX --lemmas 30 --lemma-knn 400 \
  --args="--abstract-time 2000 --no-eqhint-consider" > loops/CLK69.log 2>&1 &
P=$!
echo "CLK69 $P $(date '+%d %T')" >> loops/EXP69.pids
while kill -0 $P 2>/dev/null; do
  sleep 600
  flock cond/merge.lock python3 /project/twee/hints/merge.py loops/UL loops/CLK69 2>&1 | tail -1 | sed "s/^/$(date '+%d %T') /" >> loops/EXP69.merge
done
flock cond/merge.lock python3 /project/twee/hints/merge.py loops/UL loops/CLK69 2>&1 | tail -1 | sed "s/^/$(date '+%d %T') final /" >> loops/EXP69.merge
echo "exp69 done $(date '+%d %T')" >> loops/EXP69.pids

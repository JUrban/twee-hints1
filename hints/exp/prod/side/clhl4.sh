#!/bin/bash
# (23 Nov 21:07) exp68: the live head climber with exp67 arm B's lemmas and every weakened goal. abs/clhl3.sh (exp66,
# arm A's setting: 6 siblings, 30 kNN lemmas) made 0 real proofs in 4.1 CPU h; on the frozen heads arm B (CLB67: 30
# siblings, 400 kNN) made 3 and arm A (CLA67) 1 at about 4 CPU h each. In three of those four proofs the sketch hints came
# from proofs of weakened goals (instances of the conjecture: two variables merged, or one set to e), so --weaken 12
# (all of them; clhl3 took the first 4). Otherwise clhl3's setting, a fresh record loops/CLHL4, launched with CPUS=28
# (more CPUs for climbing for a limited time, the user 23 Nov); the default 20 is for later restarts.
# Read per CPU h against CLB67 (weaken 4, frozen context) and plainlive4's H setting.
# notes/2026-11-23-climber-restart.md ("exp68").
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
cd /project/hintwork
mkdir -p loops/CLHL4
python3 /project/twee/hints/climb.py sets/all loops/CLHL4 --live loops/UL --heads-only --reclimb-heads 3 \
  --m 8 --knn 8 --theories 4 --theory-explore 2 --theory-lemmas 10 --updown --up-single --weaken 12 --chain --fill 3 \
  --min-sketch-steps 30 --runs 24 --sketch-time 5 --final-time 160 -j "${J:-2}" --cpus "${CPUS:-20}" -- \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 30 --lemma-knn 400 --lemma-subsets --lemma-after --pool original --twee /project/bin/twee-pg61 --wall-factor 15 \
  --args="--abstract-time 2000 --no-eqhint-consider" >> loops/CLHL4.log 2>&1
echo "CLHL4 ended $(date '+%d %T')" >> loops/CLHL4.log

#!/bin/bash
# (19 Nov 15:39) exp32: the live head climber measured again as a deep member (portfolio rule; the user's message of
# 15:20: dropped on 16 Nov before the rule existed, at 0.47-1.2 per CPU hour, above members still in the portfolio).
# abs/clhl.sh's setting with today's binary (twee-pg61 via TWEE_PG_ARGS), a fresh climb record (loops/CLHL2), 2 climbs at
# a time beside production (ul66 on 17 workers). notes/2026-11-19-climber-member.md.
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
cd /project/hintwork
mkdir -p loops/CLHL2
python3 /project/twee/hints/climb.py sets/all loops/CLHL2 --live loops/UL --heads-only --reclimb-heads 3 \
  --m 8 --knn 8 --theories 4 --theory-explore 2 --theory-lemmas 10 --updown --up-single --weaken 4 --chain --fill 3 \
  --min-sketch-steps 30 --runs 24 --sketch-time 5 --final-time 160 -j "${J:-2}" --cpus "${CPUS:-40}" -- \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 6 --lemma-knn 30 --lemma-subsets --lemma-after --pool original --twee /project/bin/twee-pg61 --wall-factor 15 \
  --args="--abstract-time 2000 --no-eqhint-consider" >> loops/CLHL2.log 2>&1

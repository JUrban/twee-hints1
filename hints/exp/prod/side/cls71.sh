#!/bin/bash
# (23 Nov 23:33) restarted with --exclude sets/localheads71 (exp/sets/localheads71): the 940 unsolved goals right after a
# proved goal (not the 88 first heads) go to a plain 60 s sweep (HLW1, the sweep queue), so the climber takes the other
# holes. The first run (23:22-23:33, 22 targets, 0 real proofs in 0.72 CPU h) climbed nearest-first, mostly those.
# (23 Nov 23:22) exp71: the live climber on stalled goals again (CLU's mode, 16 Nov), beside the head climber (CLHL4).
# Why: of production's sk@1 proofs (the climb hints as hints, 40 s) in its last 8,000 runs, most came from originals
# with many sketch files from CLU (stalled goals: 986 targets, 7,302 sketch files over 108 originals, 22 real proofs
# in 27.9 CPU h, 0.79 per CPU h) and CLHL2; today's head climbers have sketches for about 15 originals each. 2,700 of
# the 3,229 unsolved goals are holes (a later goal of the same original is proved), and stalled mode climbs them,
# nearest to a proven goal first. CLU's cheap climb (20 sketch runs of 5 s, final 20 s, --weaken 4, fill 3 s) with
# today's binary and model and exp67 arm B's lemmas (30 siblings, 400 kNN); no move-model or theory-ts A/B arms.
# -j 6, starting climbs only while fewer than CPUS (default 30) other twee processes run: about 2 now, 6 when
# exp67 ends. Real proofs go into loops/UL; production reads its sketches from ul77 on (--climb-hints).
# notes/2026-11-23-climber-restart.md ("exp71").
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
cd /project/hintwork
mkdir -p loops/CLS71
python3 /project/twee/hints/climb.py sets/all loops/CLS71 --live loops/UL --exclude "${EXCLUDE:-sets/localheads71}" \
  --m 8 --knn 8 --theories 4 --theory-explore 2 --theory-lemmas 10 --updown --up-single --weaken 4 --chain --fill 3 \
  --min-sketch-steps 30 --runs 20 --sketch-time 5 --final-time 20 -j "${J:-6}" --cpus "${CPUS:-30}" -- \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 30 --lemma-knn 400 --lemma-subsets --lemma-after --pool original --twee /project/bin/twee-pg61 --wall-factor 15 \
  --args="--abstract-time 2000 --no-eqhint-consider" >> loops/CLS71.log 2>&1
echo "CLS71 ended $(date '+%d %T')" >> loops/CLS71.log

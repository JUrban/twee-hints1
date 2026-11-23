#!/bin/bash
# (23 Nov 18:44) exp66: the live head climber back beside production. abs/clhl2.sh (exp32) ran 19 Nov 15:39 to 20 Nov 10:04:
# 69 proofs in 66 CPU h (1.04 per CPU h), stopped 3 minutes before the quarantine and never restarted (an oversight; the
# user asked 23 Nov 18:20 whether any climbing runs). Same setting, a fresh record loops/CLHL3 (CLHL2's fill lemmas and
# assumptions predate the quarantine), --cpus 20: a climb starts only while fewer than 20 twee processes run.
# (18:44) Started now on the user's word ("you can start the climber now, taking some more cpus for this limited time is ok"),
# launched with CPUS=28 while exp65 runs (to about 22:55); the default 20 is for later restarts.
# (19:47) Restarted for the per-run proof names (proofs/<goal>.<tag>, twee repo d79c82e); still CPUS=28.
# Measured per CPU h against plainlive4's H setting (plain 60 s runs on the same heads). notes/2026-11-23-climber-restart.md.
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
cd /project/hintwork
mkdir -p loops/CLHL3
python3 /project/twee/hints/climb.py sets/all loops/CLHL3 --live loops/UL --heads-only --reclimb-heads 3 \
  --m 8 --knn 8 --theories 4 --theory-explore 2 --theory-lemmas 10 --updown --up-single --weaken 4 --chain --fill 3 \
  --min-sketch-steps 30 --runs 24 --sketch-time 5 --final-time 160 -j "${J:-2}" --cpus "${CPUS:-20}" -- \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 6 --lemma-knn 30 --lemma-subsets --lemma-after --pool original --twee /project/bin/twee-pg61 --wall-factor 15 \
  --args="--abstract-time 2000 --no-eqhint-consider" >> loops/CLHL3.log 2>&1
echo "CLHL3 ended $(date '+%d %T')" >> loops/CLHL3.log

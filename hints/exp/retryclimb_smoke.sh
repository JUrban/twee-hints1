#!/bin/bash
# smoke test of loop.py.tmp --retry-climb (24 Nov, exp78): 2 climbed targets, rescans every 30 s; at 90 s a new sketch
# file of the first target appears, so the next rescan marks it and the loop gives it a fresh run
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
R=/tmp/claude-1001/-project/06816eaa-f48d-4d65-80b0-498c3b54febf/scratchpad/rc1
cd $R
G1=$(head -n 1 names)
( sleep 90; f=$(ls CL/sketches/$G1 | head -n 1); cp CL/sketches/$G1/$f CL/sketches/$G1/new_$f; echo "touched $G1 $(date +%T)" ) &
LOOP_CLIMB_RESCAN=30 timeout 400 python3 -u /project/twee/hints/loop.py.tmp names L --start 5 --cascade 1,2 --retry-gap 3 \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 6 --lemma-knn 30 --lemma-subsets --lemma-after --twee /project/bin/twee-pg61 --keep-out -j 2 --reserve 0 \
  --pool original --wall-factor 15 --retry-hints 1.25 --fresh-first --chain-level 1 --variants sk@0 --ratio-order \
  --pass-every 1 --sync 10 --climb-hints $R/CL --retry-climb --retry-climb-hours 24 --cascade-hours 0.1 \
  --args="--abstract-time 2000 --no-resume-requeue --no-eqhint-consider"
wait

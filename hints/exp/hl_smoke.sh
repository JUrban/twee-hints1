#!/bin/bash
# smoke test of loop.py.tmp: lemma-set variants kp@0, kd@0, k100@0
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
cd /tmp/claude-1001/-project/06816eaa-f48d-4d65-80b0-498c3b54febf/scratchpad/opt6
LOOP_PRINT_CMD=1 python3 -u /project/twee/hints/loop.py.tmp names L --start 5 --cascade 1,2 "$@" --retry-gap 3 \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 6 --lemma-knn 30 --lemma-subsets --lemma-after --twee /project/bin/twee-pg61 --keep-out -j 2 --reserve 0 \
  --pool original --wall-factor 15 --line-gaps 80,80 --frontier 1000000 --retry-hints 1.25 --fresh-first --far-retry --mix 0.25 --retry-knn --chain-level 1 --variants hl@0 --priors Vhl@0=50 --ratio-order --pass-every 1 --args="--abstract-time 2000 --no-resume-requeue --no-eqhint-consider"

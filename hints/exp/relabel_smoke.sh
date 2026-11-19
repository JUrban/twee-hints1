#!/bin/bash
# smoke test of loop.py.tmp (--variant-budget, --priors, --relabel): CASC=$1, then extra flags
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
cd /tmp/claude-1001/-project/06816eaa-f48d-4d65-80b0-498c3b54febf/scratchpad/opt5
C=$1; shift
LOOP_PRINT_CMD=1 python3 -u /project/twee/hints/loop.py.tmp names L --start 5 --cascade $C "$@" --retry-gap 3 \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 6 --lemma-knn 30 --lemma-subsets --lemma-after --twee /project/bin/twee-pg61 --keep-out -j 2 --reserve 0 \
  --pool original --wall-factor 15 --line-gaps 80,80 --frontier 1000000 --retry-hints 1.25 --fresh-first --far-retry --mix 0.25 --sched-model /project/hintwork/sched/m4.json --sched-max-lgap 320 --sched-retrain 200 --sched-pmin 0.011 --sched-pmin-auto 400 --retry-knn --chain-level 1 --chain-records /project/hintwork/chain_records2.tsv --variants unf@0,k60@0,k60,unf,two --ratio-order --pass-every 1 --args="--abstract-time 2000 --no-resume-requeue --no-eqhint-consider"

#!/bin/bash
# (23 Nov) Smoke test of loop.py's ranked plain variant (--variants plrk400s130@0 --lemma-ranker models/lemmarank/lr1):
# solve_new.sh on PLL1's 3 proved goals (sets/plrsmoke) in the trusted context loops/ULT.ctx, 1 worker, 0.05 h, the
# ranked level first (prior 9); loops/PLR1. LOOP_PRINT_CMD shows the twee commands.
cd /project/hintwork
[ -e loops/PLR1 ] && { echo "loops/PLR1 exists"; exit 1; }
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
LOOPARGS="--lemma-ranker /project/hintwork/models/lemmarank/lr1" \
DEEP="--chain-level 1 --variants plrk400s130@0,unf@0 --variants-after 3 --variant-budget 80 --priors Vplrk400s130@0=9,L1=1.73,L2=1.1 --ratio-order" \
  timeout 900 bash /project/twee/hints/solve_new.sh sets/plrsmoke loops/ULT.ctx loops/PLR1 1 0.05 > loops/PLR1.out 2>&1
echo "PLR1 exit $?"

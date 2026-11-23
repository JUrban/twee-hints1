#!/bin/bash
# (23 Nov) Smoke test of loop.py --lemma-ranker-all (every level's kNN lemmas from models/lemmarank/lr2, pool 1,000):
# solve_new.sh on 6 production-solved goals (sets/rankall_smoke, the first 6 of sets/hintbed600) in the trusted
# context loops/ULT.ctx (the 6 left out by solve_new.sh's snapshot), 1 worker, 0.05 h; loops/PLA1. LOOP_PRINT_CMD
# shows the twee commands.
cd /project/hintwork
[ -e loops/PLA1 ] && { echo "loops/PLA1 exists"; exit 1; }
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
LOOPARGS="--lemma-ranker /project/hintwork/models/lemmarank/lr2 --lemma-ranker-all" LOOP_PRINT_CMD=1 \
DEEP="--chain-level 1 --variants unf@0 --variants-after 3 --variant-budget 80 --priors L1=1.73,L2=1.1 --ratio-order" \
  timeout 900 bash /project/twee/hints/solve_new.sh sets/rankall_smoke loops/ULT.ctx loops/PLA1 1 0.05 > loops/PLA1.out 2>&1
echo "PLA1 exit $?"

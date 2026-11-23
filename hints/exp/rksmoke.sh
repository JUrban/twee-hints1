#!/bin/bash
# (23 Nov) Smoke test of loop.py's hinted ranked lemma-set member (--variants rk30@0 --lemma-ranker models/lemmarank/lr2):
# as abs/rankallsmoke.sh (sets/rankall_smoke in loops/ULT.ctx, 1 worker, 0.05 h) with rk30@0 first (prior 9); loops/PRK1.
cd /project/hintwork
[ -e loops/PRK1 ] && { echo "loops/PRK1 exists"; exit 1; }
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
LOOPARGS="--lemma-ranker /project/hintwork/models/lemmarank/lr2" LOOP_PRINT_CMD=1 \
DEEP="--chain-level 1 --variants rk30@0,unf@0 --variants-after 1 --variant-budget 80 --priors Vrk30@0=9,L1=1.73,L2=1.1 --ratio-order" \
  timeout 900 bash /project/twee/hints/solve_new.sh sets/rankall_smoke loops/ULT.ctx loops/PRK1 1 0.05 > loops/PRK1.out 2>&1
echo "PRK1 exit $?"

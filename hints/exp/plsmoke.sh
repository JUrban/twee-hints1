#!/bin/bash
# (23 Nov) Smoke test of loop.py's plain variant (--variants plk100s40@0): solve_new.sh on 3 goals (sets/plsmoke, one
# that PLN1 proved plainly) in the trusted context (loops/ULT.ctx), 1 worker, 0.05 h; loops/PLS.
cd /project/hintwork
[ -e loops/PLS ] && { echo "loops/PLS exists"; exit 1; }
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
DEEP="--chain-level 1 --variants plk100s40@0,unf@0 --variants-after 3 --variant-budget 80 --priors L1=1.73,L2=1.1 --ratio-order" \
  timeout 900 bash /project/twee/hints/solve_new.sh sets/plsmoke loops/ULT.ctx loops/PLS 1 0.05 > loops/PLS.out 2>&1
echo "PLS exit $?"

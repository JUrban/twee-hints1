#!/bin/bash
# exp27 (19 Nov 07:18): sets/half1 from zero with today's system, 6 workers, 2 hours, against PGA (17 Nov 16:54, the same
# script abs/or_test.sh: 18,987 at 2 hours; identical runs differ by about 185). Today's system = production's deep
# portfolio of 18-19 Nov on top of PGA: twee-pg61 (e61 + PG 0.25 + ground-joining branch limit 100), the cascade
# 5,40,80,160,320 with chain hints from level 1 (records of this loop's own proofs), the variants
# unf@0,k60@0,k60,p9,unf,two,nom (80 s ones after the 160 s level), --ratio-order with production's priors.
# notes/2026-11-19-from-zero-portfolio.md
cd /project/hintwork
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
ARM=PGC TWEE=/project/bin/twee-pg61 PG= CASCADE=5,40,80,160,320 \
  LOOPARGS="--chain-level 1 --variants unf@0,k60@0,k60,p9,unf,two,nom --variants-after 3 --variant-budget 80 --priors L1=1.73,L2=1.1 --ratio-order" \
  bash abs/or_test.sh

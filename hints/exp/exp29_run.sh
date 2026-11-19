#!/bin/bash
# exp29 (19 Nov): sets/half1 from zero, as exp27's PGC (18,917 at 2 hours; PGA 18,987; identical runs differ by about
# 185), plus this morning's 5 s lemma members, k100@0, k200@0, k400@0 and kd@0, and --explore 0.2 for them and for
# L1 (the 40 s chain level, starved in exp27: 4 runs, 4 proved). notes/2026-11-19-from-zero-explore.md
cd /project/hintwork
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
ARM=PGD TWEE=/project/bin/twee-pg61 PG= CASCADE=5,40,80,160,320 \
  LOOPARGS="--chain-level 1 --variants unf@0,k60@0,k100@0,k200@0,k400@0,kd@0,k60,p9,unf,two,nom --variants-after 3 --variant-budget 80 --priors L1=1.73,L2=1.1 --ratio-order --explore 0.2 --explore-labels L1,Vk100@0,Vk200@0,Vk400@0,Vkd@0" \
  bash abs/or_test.sh

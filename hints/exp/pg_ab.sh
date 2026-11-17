#!/bin/bash
# (17 Nov 17:00) Parental-guidance A/B from zero: sets/half1, 6 workers each, 2 hours, solve_new.sh's new defaults
# (twee-e44, 5,20,80,320 s, --no-fresh-states). PGB control; PGA = twee-e48 (same output with the flags off) through
# /project/bin/twee-pg with TWEE_PG_ARGS="--pg-threshold $T": no critical pairs of two rules when sigmoid of the sum
# of their rule-model raw scores is below T; the skipped pairs are the freezer, made when the queue empties.
# 200 late hard goals (5 s): off 29, 0.047 40, 0.119 43, 0.269 52 (+23 -0).
cd /project/hintwork
T=${1:?threshold}
ARM=PGB bash abs/or_test.sh &
sleep 2
ARM=PGA TWEE=/project/bin/twee-pg TWEE_PG_ARGS="--pg-threshold $T" bash abs/or_test.sh &
wait

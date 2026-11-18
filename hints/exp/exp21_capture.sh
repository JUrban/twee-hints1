#!/bin/bash
# exp21/capture.sh: the 300 goals' 5 s fresh-run commands in UL's current context, captured as in exp11/exp17
# (exp3/solve_cap.sh with LOOP_PRINT_CMD) but at 0.01 abstract s, so the capture loop proves nothing and every goal's
# command has the same context; exp6/tbify.py then sets --max-time 5. Production's twee (e61 with PG 0.25 and the
# ground-joining branch limit 100) is given as TWEE + PG, so the flags are in the commands. B: 30 kNN lemmas (as
# production); K60: 60.
cd /project/hintwork
for K in 30 60; do
  N=$([ $K = 30 ] && echo B || echo K60)
  LOOP_PRINT_CMD=1 LOOP_KEEP_TMP=1 TWEE=/project/bin/twee-e61 PG="--pg-threshold 0.25 --ground-joining-branch-limit 100" \
    CASCADE=0.01 KNN=$K XEVERY=100000 bash exp3/solve_cap.sh exp21/goals300 loops/UL exp21/cap/$N 1 0.3 > exp21/cap/$N.out 2>&1 &
done
wait
for N in B K60; do python3 exp6/tbify.py exp21/cap/$N.log exp21/cap/$N exp21/cap/tb$N exp21/${N}_5.cmds 5; done
echo "$(date +%T) captured" >> exp21/stage.log

#!/bin/bash
# The learned scheduler from scratch (16 Nov 18:00): sets/rp3, clean context loops/ALL, 4 workers, 1 hour, transfer
# every 2 minutes; against LVD 942. ARM=LVS: production's scheduler options (abs/ul36.sh) via LOOPARGS.
# Runs a private copy of solve_new.sh (edits to the original must not reach a running bash).
cd /project/hintwork
sed "s|^H=.*|H=/project/twee/hints|" /project/twee/hints/solve_new.sh > loops/$ARM.solve_new.sh
LOOPARGS="${LOOPARGS---sched-model /project/hintwork/sched/m4.json --sched-max-lgap 320 --sched-retrain 200 --sched-pmin 0.011 --sched-pmin-auto 400}" \
  bash loops/$ARM.solve_new.sh sets/rp3 loops/ALL loops/$ARM 4 1 > loops/$ARM.out 2>&1
touch loops/$ARM.done

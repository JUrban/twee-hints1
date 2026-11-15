#!/bin/bash
# after battery 6b: V2p round 3 (7 jobs) and the tiered-pool u3 run (3 jobs), beside u3 (10 jobs)
until grep -q '^rm4t_lem3k10s' /project/hintwork/abs/batt6b.log 2>/dev/null; do sleep 30; done
cd /project/hintwork
bash abs/v2r3.sh &
J=3 bash abs/u3b.sh to &
wait
echo "q6 done $(date +%T)"

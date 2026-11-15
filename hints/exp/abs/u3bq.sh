#!/bin/bash
# after battery 6b: tiered pool (kNN at full boost + rest of the original's pool at factor 0.3), online
until grep -q '^rm4t_lem3k10s' /project/hintwork/abs/batt6b.log 2>/dev/null; do sleep 30; done
cd /project/hintwork
J=9 bash abs/u3b.sh to

#!/bin/bash
# From scratch on the other 8 whole holdout originals (16 Nov 14:00; sets/ho8, 3,400 goals; plain 4 s 2,156,
# production 3,081 after 3 days): hints/solve_new.sh with the clean context loops/ALL (13 Nov, round 0 and 1),
# 4 workers, 1 hour; curve as abs/replaycurvec.sh (ARM=HO8).
cd /project/hintwork
/project/twee/hints/solve_new.sh sets/ho8 loops/ALL loops/HO8 4 1 > loops/HO8.out 2>&1
touch loops/HO8.done

#!/bin/bash
# --mix (17 Nov 03:10): sets/rp3 from zero as PE1 (SCHED= , 4 workers, --pass-every 1), 15 minutes, with
# LOOPARGS="--mix $MIX". PE1 left 438 of its 489 unsolved goals never run: the near retries took every slot.
# H = the scratch copy of the hints modules under test (HM).
cd /project/hintwork
sed "s|^H=.*|H=$HM|" /project/twee/hints/solve_new.sh > loops/$ARM.solve_new.sh
SCHED= LOOPARGS="--mix $MIX" bash loops/$ARM.solve_new.sh sets/rp3 loops/EMPTY loops/$ARM 4 0.25 > loops/$ARM.out 2>&1
touch loops/$ARM.done

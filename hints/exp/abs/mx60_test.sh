#!/bin/bash
# --mix over an hour (17 Nov 04:10): sets/rp3 from zero as LVZ (SCHED= , 4 workers, 1 hour; 890 at 60 min) with
# --pass-every 1 (solve_new.sh default; PE1 = LVZ to within 1 over 15 min) and LOOPARGS="--mix $MIX" (default 0.25:
# one of the 4 workers each for near retries, far goals and deeper levels). Production (ul39) paused meanwhile.
cd /project/hintwork
sed "s|^H=.*|H=/project/twee/hints|" /project/twee/hints/solve_new.sh > loops/$ARM.solve_new.sh
SCHED= LOOPARGS="--mix ${MIX:-0.25}" bash loops/$ARM.solve_new.sh sets/rp3 loops/EMPTY loops/$ARM 4 1 > loops/$ARM.out 2>&1
touch loops/$ARM.done

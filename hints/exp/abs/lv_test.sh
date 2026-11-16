#!/bin/bash
# A 20 s cascade level from scratch (16 Nov 15:10): in the clean replay (2aq) the 80 s level proved half of what it
# ran (48 of 97) but cost 95 s a run, so the 5-80 s gap may hold many goals that 20 s would get 4x cheaper.
# solve_new.sh on sets/rp3 with the clean context loops/ALL, 4 workers, 1 hour, transfer on: ARM=LVA CASCADE=5,80,320
# (control, as RPc: 934), ARM=LVB CASCADE=5,20,80,320.
cd /project/hintwork
CASCADE=$CASCADE /project/twee/hints/solve_new.sh sets/rp3 loops/ALL loops/$ARM 4 1 > loops/$ARM.out 2>&1
touch loops/$ARM.done

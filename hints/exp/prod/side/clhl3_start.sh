#!/bin/bash
# (23 Nov 18:44) exp66's start: after exp65 (loops/Q5A.done and loops/Q5B.done, about 22:55) frees its 8 CPUs, start
# abs/clhl3.sh; its PID into loops/CLHL3.pid. Gives up at 24 Nov 02:00 (epoch) if exp65 has not ended.
cd /project/hintwork
END=$(date -d "2026-11-24 02:00" +%s)
until [ -e loops/Q5A.done -a -e loops/Q5B.done ] || [ $(date +%s) -gt $END ]; do sleep 30; done
[ -e loops/Q5A.done -a -e loops/Q5B.done ] || { echo "exp65 not done by the deadline $(date '+%d %T')" > loops/CLHL3.start; exit 1; }
nohup bash abs/clhl3.sh > /dev/null 2>&1 &
echo $! > loops/CLHL3.pid
echo "started $(date '+%d %T') pid $!" > loops/CLHL3.start

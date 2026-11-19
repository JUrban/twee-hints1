#!/bin/bash
# exp21/stage.sh PID: wait for the capture (PID), build the arms, run them on 2 workers.
cd /project/hintwork/exp21
while kill -0 $1 2>/dev/null; do sleep 30; done
python3 mk.py > mk.out 2>&1 || { echo "$(date +%T) mk.py failed" >> stage.log; exit 1; }
echo "$(date +%T) start A" >> stage.log
python3 run.py A.cmds A 2 > A.out 2>&1
echo "$(date +%T) end A" >> stage.log

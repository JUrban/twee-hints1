#!/bin/bash
# exp17/stage.sh PID: wait for PID (exp16's stage) to end, then the 13 drifted walls at 30 kNN lemmas (control),
# then all 107 walls at 60 kNN lemmas; 80 s, exp11's chain hints, 4 workers.
cd /project/hintwork/exp17
while kill -0 $1 2>/dev/null; do sleep 60; done
echo "$(date +%H:%M) start K30" >> stage.log
python3 run.py K30.cmds K30 4 > K30.run.out 2>&1
echo "$(date +%H:%M) start K60" >> stage.log
python3 run.py K60.cmds K60 4 > K60.run.out 2>&1
echo "$(date +%H:%M) end" >> stage.log

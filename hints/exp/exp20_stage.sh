#!/bin/bash
# exp20/stage.sh PID: wait for PID (exp17's stage) to end, then the 92 failed walls at 160 s on 4 workers.
cd /project/hintwork/exp20
while kill -0 $1 2>/dev/null; do sleep 60; done
echo "$(date +%H:%M) start C160" >> stage.log
python3 run.py C160.cmds C160 4 > C160.out 2>&1
echo "$(date +%H:%M) end C160" >> stage.log

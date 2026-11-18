#!/bin/bash
# exp15/stage.sh PID...: wait for the given processes (exp13's runners) to end, then the unfolded walls at 80 s.
cd /project/hintwork/exp15
for p in "$@"; do while kill -0 $p 2>/dev/null; do sleep 60; done; done
echo "$(date +%H:%M) start U" >> stage.log
python3 run.py U.cmds U 4 > U.out 2>&1
echo "$(date +%H:%M) end U" >> stage.log

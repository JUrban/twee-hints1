#!/bin/bash
# exp22/stage.sh PID: when PID (exp21's twee runner) ends, G80 then N80 on 4 workers.
cd /project/hintwork/exp22
while kill -0 $1 2>/dev/null; do sleep 60; done
for A in G80 N80; do
  echo "$(date +%T) start $A" >> stage.log
  python3 run.py $A.cmds $A 4 > $A.out 2>&1
done
echo "$(date +%T) end" >> stage.log

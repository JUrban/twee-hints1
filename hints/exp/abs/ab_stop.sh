#!/bin/bash
# Stop A/B arms ARM... (their lvl_ab.sh, loop.py and twee children). bash abs/ab_stop.sh UA UB
for d in "$@"; do
  ps -u mptp -o pid=,args= | awk -v d="loops/$d" '$2=="python3" && $4=="/project/twee/hints/loop.py" && $5=="sets/all" && $6==d {print $1}' | xargs -r kill
done
sleep 2
for d in "$@"; do
  ps -u mptp -o pid=,args= | awk -v p="^loops/$d/tmp/" '$2=="/project/bin/twee-e22" && $3 ~ p {print $1}' | xargs -r kill
done
sleep 1
ps -u mptp -o args= | grep -v grep | grep -c "loops/U[AB]/tmp\|loops/U[AB] --start"

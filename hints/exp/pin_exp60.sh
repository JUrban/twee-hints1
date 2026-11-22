#!/bin/bash
# (22 Nov, exp60 at 2 hours; notes/2026-11-22-floor-ratio-until.md "Sockets") Even CPU sets: P3A's processes had
# run mostly on socket 0 and P3B's, P3C's and production's on socket 1, and P3A ran about 10% faster per abstract
# second. Each arm (its or_test2.sh tree) and production (ul75, xfrlive2k, gmlive4, proofq) get 14 physical cores,
# 7 on each socket (socket 0: CPUs 0-27 and their siblings 56-83; socket 1: 28-55 and 84-111). Children inherit
# the set. Three passes, 5 s apart, catch processes started during a pass.
set -u
declare -A SET=([2353987]="0-6,56-62,28-34,84-90" [2353989]="7-13,63-69,35-41,91-97" [2353992]="14-20,70-76,42-48,98-104"
                [1846754]="21-27,77-83,49-55,105-111" [3454187]="21-27,77-83,49-55,105-111"
                [2074658]="21-27,77-83,49-55,105-111" [1177545]="21-27,77-83,49-55,105-111")
tree() { local p=$1; echo $p; for c in $(ps -o pid= --ppid $p 2>/dev/null); do tree $c; done; }
for pass in 1 2 3; do
  n=0
  for r in "${!SET[@]}"; do
    for p in $(tree $r); do taskset -a -p -c "${SET[$r]}" $p > /dev/null 2>&1 && n=$((n+1)); done
  done
  echo "pass $pass: $n processes set $(date +%T)"
  sleep 5
done

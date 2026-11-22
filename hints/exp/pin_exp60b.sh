#!/bin/bash
# (22 Nov, exp60 at 2 hours, after abs/pin_exp60.sh) One logical CPU per physical core: each arm gets 14 whole cores,
# 7 per socket, so its own runs never share a core through a hyperthread sibling (with pin_exp60.sh's sets the kernel
# kept an arm's runs on its loop's socket and paired them on siblings). The siblings (56-111) are left to the
# machine's other users. Three passes, 5 s apart.
set -u
declare -A SET=([2353987]="0-6,28-34" [2353989]="7-13,35-41" [2353992]="14-20,42-48"
                [1846754]="21-27,49-55" [3454187]="21-27,49-55" [2074658]="21-27,49-55" [1177545]="21-27,49-55")
tree() { local p=$1; echo $p; for c in $(ps -o pid= --ppid $p 2>/dev/null); do tree $c; done; }
for pass in 1 2 3; do
  n=0
  for r in "${!SET[@]}"; do
    for p in $(tree $r); do taskset -a -p -c "${SET[$r]}" $p > /dev/null 2>&1 && n=$((n+1)); done
  done
  echo "pass $pass: $n processes set $(date +%T)"
  sleep 5
done

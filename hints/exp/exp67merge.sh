#!/bin/bash
# (23 Nov 23:41) exp67's real proofs into production every 10 minutes (merge.py under cond/merge.lock) until both the
# arms (loops/EXP67.pids "exp67 done") and the controls ("CC67C/CC67D done") have ended, then once more. Before, the
# arms' proofs were merged by hand (CLB67's proofs of 23:00-23:08 waited until 23:40).
cd /project/hintwork
m() { for d in CLA67 CLB67 CC67C CC67D; do flock cond/merge.lock python3 /project/twee/hints/merge.py loops/UL loops/$d 2>&1 | tail -1 | sed "s/^/$(date '+%d %T') $d /" >> loops/EXP67.merge; done; }
until grep -q "^exp67 done" loops/EXP67.pids && grep -q "^CC67C/CC67D done" loops/EXP67.pids; do sleep 600; m; done
m

#!/bin/bash
# (24 Nov) exp76's real proofs into production every 10 minutes (merge.py under cond/merge.lock) until exp76 has ended
# (loops/EXP76.pids "exp76 done"), then once more, as exp/exp67merge.sh did for exp67. exp76's script merges only at
# its end; at 05:0x F76S had 2 new proofs (mbol_com 75, nslm_to_aa1 1080), merged by hand.
cd /project/hintwork
m() { for d in F76S F76C; do flock cond/merge.lock python3 /project/twee/hints/merge.py loops/UL loops/$d 2>&1 | tail -1 | sed "s/^/$(date '+%d %T') $d /" >> loops/EXP76.merge; done; }
until grep -q "^exp76 done" loops/EXP76.pids; do sleep 600; m; done
m

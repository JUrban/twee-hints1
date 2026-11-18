#!/bin/bash
# exp12: after the capture (PID $1) and exp11's stage-1 runner (PID $2) end: merge exp11's proofs, build chain
# commands for the 96 gap heads, stage A (80 s) on all, stage B (320 s) on the rest; merges into UL every 10 min.
cd /project/hintwork/exp12
UL=/project/hintwork/loops/UL
while kill -0 $1 2>/dev/null || kill -0 $2 2>/dev/null; do sleep 30; done
python3 /project/hintwork/exp3/tomerge.py ../exp11/out_s1 ../exp11/xm > /dev/null 2>&1
echo "$(date +%H:%M) exp11 s1: $(python3 /project/twee/hints/merge.py $UL ../exp11/xm 2>&1 | grep 'merged into')" >> merges.log
python3 /project/hintwork/exp6/tbify.py cap/CAP.log cap/CAP cap/tb A_pool.cmds 80
python3 /project/hintwork/exp6/tbify.py cap/CAP.log cap/CAP cap/tb B_pool.cmds 320
python3 mkchain.py A_pool.cmds A.cmds; python3 mkchain.py B_pool.cmds B_all.cmds
echo "$(date +%H:%M) stage A: $(wc -l < A.cmds) heads" >> merges.log
merge() { python3 /project/hintwork/exp3/tomerge.py out_A out_B xm > /dev/null 2>&1; echo "$(date +%H:%M) $(python3 /project/twee/hints/merge.py $UL xm 2>&1 | grep 'merged into')" >> merges.log; }
mkdir -p out_A out_B
( while true; do sleep 600; merge; done ) & ML=$!
python3 run.py A.cmds A 4 > A.out 2>&1
merge
awk -F'\t' '$2==0{print $1}' res_A.tsv | sort > rest
awk -F'\t' 'NR==FNR{r[$1]=1; next} ($1 in r)' rest B_all.cmds > B.cmds
echo "$(date +%H:%M) stage B: $(wc -l < B.cmds) heads" >> merges.log
python3 run.py B.cmds B 4 > B.out 2>&1
merge
kill $ML
echo "$(date +%H:%M) done" >> merges.log

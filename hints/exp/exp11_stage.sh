#!/bin/bash
# exp11: stage 1 (80 s) on all walls, stage 2 (320 s) on the rest; proofs merged into UL every 10 min and at the end.
cd /project/hintwork/exp11
merge() { python3 /project/hintwork/exp3/tomerge.py out_s1 out_s2 xm > /dev/null 2>&1; python3 /project/twee/hints/merge.py /project/hintwork/loops/UL xm 2>&1 | tail -1 | sed "s/^/$(date +%H:%M) /" >> merges.log; }
mkdir -p out_s1 out_s2
( while true; do sleep 600; merge; done ) & ML=$!
python3 run.py s1.cmds s1 4 > s1.out 2>&1
merge
awk -F'\t' '$2==0{print $1}' res_s1.tsv | sort > rest
awk -F'\t' 'NR==FNR{r[$1]=1; next} ($1 in r)' rest s2_all.cmds > s2.cmds
python3 run.py s2.cmds s2 4 > s2.out 2>&1
merge
kill $ML
echo "done $(date +%H:%M)" >> merges.log

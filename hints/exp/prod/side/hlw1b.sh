#!/bin/bash
# (24 Nov) HLW1 (exp72, the plain 60 s sweep on the local heads, cond/HLW1) resumed with 5 threads instead of
# abs/sweepq.sh's 3, and the current production context for the goals not yet run (cond/HLW1.trusted2; the first
# 122 ran in cond/HLW1.trusted, 03:46). Why: at 04:49 it had proved 4 new goals in 122 runs, 1.32 per CPU h, and
# production 0 in its last 1,000 runs. condprove.py resumes (skips the goals in cond/HLW1/results.tsv). The
# stalled-goal climber (CPUS=20) yields the 2 CPUs. Then the import and merge, as abs/sweepq.sh does.
cd /project/hintwork
cut -f1 loops/UL/solved.tsv | sort -u > cond/HLW1.trusted2
echo "HLW1 resumed $(date '+%d %T') context $(wc -l < cond/HLW1.trusted2) -j ${J:-5}" >> cond/SWEEPQ.log
python3 -u /project/twee/hints/exp/condprove.py cond/HLW1 --trusted cond/HLW1.trusted2 -j ${J:-5} --proved \
  --time 60 --sibs 100 --after 30 --knn 400 --only sets/localheads71 >> cond/HLW1.log 2>&1
python3 /project/twee/hints/exp/condimport.py cond/HLW1 loops/CI3 --trusted cond/HLW1.trusted2 --time 60 > cond/HLW1.import 2>&1
flock cond/merge.lock python3 /project/twee/hints/merge.py loops/UL loops/CI3 > cond/HLW1.merge 2>&1
echo "HLW1 done $(date '+%d %T') ran $(grep -c . cond/HLW1/results.tsv) THM $(grep -c -P '\tTHM\t' cond/HLW1/results.tsv) $(tail -1 cond/HLW1.import) | $(tail -1 cond/HLW1.merge)" >> cond/SWEEPQ.log

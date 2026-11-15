#!/bin/bash
# A/B of loop.py --sched-model (15 Nov): D=loop dir (a reflink copy of loops/UL), J=workers,
# extra arguments are passed on (e.g. --sched-model sched/m1.json). Otherwise as abs/ul14.sh,
# without --sync (no side workers).
cd /project/hintwork
python3 -u /project/twee/hints/loop.py sets/all loops/$D --start 5 --cascade 20,80 --cascade-start 0 --cascade-continue --retry-gap 3 \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 6 --lemma-knn 10 --lemma-subsets --lemma-after --twee /project/bin/twee-e22 --keep-out -j ${J:-2} --reserve 0 \
  --pool original --wall-factor 15 --line-gaps 80,13 --retry-hints 1.25 --fresh-first --far-retry \
  --args="--abstract-time 2000 --no-resume-requeue --no-eqhint-consider" "$@" > loops/$D.log 2>&1
echo "$D: $(tail -1 loops/$D.log) $(date +%T)" | tee loops/$D.done

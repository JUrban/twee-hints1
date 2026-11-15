#!/bin/bash
# Tail heads at a long budget (15 Nov 18:15): sets/heads_u (heads30 still unsolved), fresh 160 abstract s, max-cpu 800,
# snapshot ULsW (14:31). ARM=HLU: unfolded (2af; at 20 s 0/28); ARM=HLF: folded control. Heads at 320 s folded
# resumes: 5/62 (8%, UL20).
cd /project/hintwork
D=$ARM
python3 -u /project/twee/hints/loop.py sets/heads_u loops/$D --init loops/ULsW --start 1 --rounds 1 --keep-out -j ${J:-3} \
  --pool original --wall-factor 15 $X \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 6 --lemma-knn 10 --lemma-subsets --lemma-after --twee /project/bin/twee-e22 --timeout 160 \
  --args="--abstract-time 2000 --max-cpu 800 --no-resume-requeue --no-eqhint-consider" > loops/$D.log 2>&1
echo "$D $(grep -c THM loops/$D/r1/results.tsv)/$(wc -l < sets/heads_u) $(date +%T)" | tee loops/$D.done

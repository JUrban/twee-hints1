#!/bin/bash
# Tail heads (15 Nov 11:57): 30 random heads (first goal after an original's last proof; lgap 13-68 lines),
# production context, fresh 20 s, from snapshot ULsV (UL at 11:57). HU: unfolded (J 3); HF: folded control (J 2).
cd /project/hintwork
run() { D=$1; J=$2; shift 2
python3 -u /project/twee/hints/loop.py sets/heads30 loops/$D --init loops/ULsV --start 1 --rounds 1 --keep-out -j $J \
  --pool original --wall-factor 15 "$@" \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 6 --lemma-knn 10 --lemma-subsets --lemma-after --twee /project/bin/twee-e22 --timeout 20 \
  --args="--abstract-time 2000 --max-cpu 200 --no-resume-requeue --no-eqhint-consider" > loops/$D.log 2>&1
echo "$D $(grep -c THM loops/$D/r1/results.tsv)/30 $(date +%T)" | tee loops/$D.done; }
run HU 3 --unfold &
run HF 2 &
wait

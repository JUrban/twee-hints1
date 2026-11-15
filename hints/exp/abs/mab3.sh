#!/bin/bash
# Paired model test, filter strength (15 Nov): as abs/mab.sh, with --model-args (threshold/penalty). A better model
# may afford a stricter filter.   M=rm7t X="--rule-threshold 0.2 --rule-penalty 2" TAG=t2 J=3 bash abs/mab2.sh
cd /project/hintwork
D=MB_${M}_${TAG}
python3 -u /project/twee/hints/loop.py sets/${SET:-ultest} loops/$D --init loops/${SNAP:-ULsT} --start 1 --rounds 1 --keep-out -j ${J:-3} \
  --pool original --wall-factor 15 \
  --model --model-fixed /project/hintwork/models/$M.bin,/project/hintwork/models/$M.vocab --model-theory "--model-args=$X" \
  --lemmas 6 --lemma-knn 10 --lemma-subsets --lemma-after --twee ${TWEE:-/project/bin/twee-e22} --timeout 20 \
  --args="--abstract-time 2000 --max-cpu 200 --no-resume-requeue --no-eqhint-consider" > loops/$D.log 2>&1
echo "$D $(grep -c THM loops/$D/r1/results.tsv)/$(wc -l < sets/${SET:-ultest}) $(date +%T)" | tee loops/$D.done

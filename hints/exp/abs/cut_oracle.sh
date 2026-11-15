#!/bin/bash
# Oracle cuts (15 Nov): abs/cut_test.sh's protocol with the cut candidates taken from the goal's later production
# proof (loops/UL/hints), CUT_ORACLE=spread|last|first, K of them, CT abstract s to prove them.
cd /project/hintwork
D=${ARM}
G="--gen-model none --gen-python /usr/bin/python3 --gen-script /project/twee/hints/cutoracle.py --gen-cuts ${K:-40} --gen-cut-time ${CT:-5} ${SEP:+--gen-cut-sep}"
CUT_ORACLE_DIR=/project/hintwork/loops/UL/hints CUT_ORACLE_K=${K:-40} \
python3 -u /project/twee/hints/loop.py sets/${SET:-cut9} loops/$D --init loops/ULsW --start 1 --rounds 2 --timeout 0,5,${T2:-15} \
  --resume --keep-out -j ${J:-3} --pool original --wall-factor 15 \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 6 --lemma-knn 10 --lemma-subsets --lemma-after --twee ${TWEE:-/project/bin/twee-e39} $G \
  --args="--abstract-time 2000 ${REQ:---no-resume-requeue} --no-eqhint-consider ${X}" > loops/$D.log 2>&1
echo "$D r1 $(grep -c THM loops/$D/r1/results.tsv) r2 $(grep -c THM loops/$D/r2/results.tsv)/$(wc -l < sets/${SET:-cut9}) $(date +%T)" | tee loops/$D.done

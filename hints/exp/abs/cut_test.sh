#!/bin/bash
# Conjecture cuts (15 Nov; user: try the IWIL 2026 conjecture cuts). Same protocol as abs/gen_test.sh (sets/gen200,
# snapshot loops/ULsW, round 1 fresh 5 s, round 2 resume +15 s with the pool hints), and before round 2 the
# generator's K most sampled equations go into one --multi-goal run of CT abstract s; the proved ones become axioms.
#   ARM=CUT M=models/gc1_4000.pt GS=gencopy.py K=40 CT=5 bash abs/cut_test.sh
cd /project/hintwork
D=${ARM}
G="--gen-model /project/hintwork/$M --gen-n ${N:-400} --gen-temp ${TEMP:-1.0} --gen-script ${GS:-gencopy.py} --gen-cuts ${K:-40} --gen-cut-time ${CT:-5} ${SEP:+--gen-cut-sep}"
python3 -u /project/twee/hints/loop.py sets/${SET:-gen200} loops/$D --init loops/ULsW --start 1 --rounds 2 --timeout 0,5,15 \
  --resume --keep-out -j ${J:-2} --pool original --wall-factor 15 \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 6 --lemma-knn 10 --lemma-subsets --lemma-after --twee ${TWEE:-/project/bin/twee-e39} $G \
  --args="--abstract-time 2000 ${REQ:---no-resume-requeue} --no-eqhint-consider ${X}" > loops/$D.log 2>&1
echo "$D r1 $(grep -c THM loops/$D/r1/results.tsv) r2 $(grep -c THM loops/$D/r2/results.tsv)/$(wc -l < sets/${SET:-gen200}) $(date +%T)" | tee loops/$D.done

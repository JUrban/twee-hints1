#!/bin/bash
# Paired model test (15 Nov, user: the later long proofs should train ENIGMA better): the 400 newest round-5 proofs
# (sets/ultest; no model trained on them) are removed from the solved set (snapshot loops/ULsT = UL at 08:10 minus
# ultest) and rerun fresh at T s (default 20) with the production L0 configuration and rule model M.
# Same goals, same context: only the model differs. No --online (an arm's proofs do not change its context).
#   M=rm7t T=20 J=3 bash abs/mab.sh   -> loops/MB_<M>_<T>
cd /project/hintwork
D=MB_${M}_${T:-20}
python3 -u /project/twee/hints/loop.py sets/ultest loops/$D --init loops/ULsT --start 1 --rounds 1 --keep-out -j ${J:-3} \
  --pool original --wall-factor 15 \
  --model --model-fixed /project/hintwork/models/$M.bin,/project/hintwork/models/$M.vocab --model-theory \
  --lemmas 6 --lemma-knn 10 --lemma-subsets --lemma-after --twee /project/bin/twee-e22 --timeout ${T:-20} \
  --args="--abstract-time 2000 --max-cpu 200 --no-resume-requeue --no-eqhint-consider" > loops/$D.log 2>&1
echo "$D $(grep -c THM loops/$D/r1/results.tsv)/$(wc -l < sets/ultest) $(date +%T)" | tee loops/$D.done

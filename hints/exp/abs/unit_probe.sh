#!/bin/bash
# Unit-ized conditional lemmas (15 Nov, lemmas.lemma_form): stalled goals (sets/st79u) fresh 20 s in the production L0
# configuration from snapshot loops/ULsN (UL at 09:30); U=1 with the conversion, U=0 the control.
#   U=1 J=2 bash abs/unit_probe.sh   -> loops/PU_<U>
cd /project/hintwork
D=PU_$U
TWEE_LEMMA_UNITIZE=$U python3 -u /project/twee/hints/loop.py sets/st79u loops/$D --init loops/ULsN --start 1 --rounds 1 --keep-out -j ${J:-2} \
  --pool original --online --wall-factor 15 \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 6 --lemma-knn 10 --lemma-subsets --lemma-after --twee /project/bin/twee-e22 --timeout 20 \
  --args="--abstract-time 2000 --max-cpu 200 --no-resume-requeue --no-eqhint-consider" > loops/$D.log 2>&1
echo "$D $(grep -c THM loops/$D/r1/results.tsv)/$(wc -l < loops/$D/r1/results.tsv) $(date +%T)" | tee loops/$D.done

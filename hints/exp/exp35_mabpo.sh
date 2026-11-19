#!/bin/bash
# (19 Nov 17:15) exp35: the parents' stored rule-model scores ordering the queue (twee-e62 --pg-order F: a new pair's
# score * F ** sigmoid(q1 + q2), two lookups per pair). The user (17:00): the forest can be as small as the weight function,
# a spectrum of speed and precision; 2ao tried only the most expensive point. abs/mabpg.sh's paired test (400 ultest goals,
# snapshot ULsT, fresh 20 s, PG 0.25, rm4t); the control is exp33's rm4t arm (loops/MP_rm4t_20, twee-e61, identical
# settings; e62 at F = 1 is byte-identical to e61). notes/2026-11-19-pg-order.md.
#   F=0.5 J=1 bash abs/mabpo.sh   -> loops/MO_<F>_<T>
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100 --pg-order ${F:-0.5}"
cd /project/hintwork
D=MO_${F:-0.5}_${T:-20}
python3 -u /project/twee/hints/loop.py sets/ultest loops/$D --init loops/ULsT --start 1 --rounds 1 --keep-out -j ${J:-1} \
  --pool original --wall-factor 15 \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 6 --lemma-knn 10 --lemma-subsets --lemma-after --twee /project/bin/twee-pg62 --timeout ${T:-20} \
  --args="--abstract-time 2000 --max-cpu 200 --no-resume-requeue --no-eqhint-consider" > loops/$D.log 2>&1
echo "$D $(grep -c THM loops/$D/r1/results.tsv)/$(wc -l < sets/ultest) $(date +%T)" | tee loops/$D.done

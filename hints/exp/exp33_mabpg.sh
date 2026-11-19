#!/bin/bash
# (19 Nov 16:45) exp33: the near-oracle through parental guidance (user: "yes, run the oracle-through-PG test").
# abs/mab.sh's paired test (15 Nov: the 400 newest round-5 proofs, sets/ultest, removed from the solved set, snapshot
# loops/ULsT; fresh 20 s at the L0 configuration; rmO, trained on these 400 goals' own logs, gained nothing through the
# defer-once filter, 273 against 271) with today's binary and parental guidance at 0.25 in both arms: twee-pg61 with
# TWEE_PG_ARGS. Only the model differs: M=rm4t or M=rmO. notes/2026-11-19-oracle-pg.md.
#   M=rmO T=20 J=1 bash abs/mabpg.sh   -> loops/MP_<M>_<T>
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
cd /project/hintwork
D=MP_${M}_${T:-20}
python3 -u /project/twee/hints/loop.py sets/ultest loops/$D --init loops/ULsT --start 1 --rounds 1 --keep-out -j ${J:-1} \
  --pool original --wall-factor 15 \
  --model --model-fixed /project/hintwork/models/$M.bin,/project/hintwork/models/$M.vocab --model-theory \
  --lemmas 6 --lemma-knn 10 --lemma-subsets --lemma-after --twee /project/bin/twee-pg61 --timeout ${T:-20} \
  --args="--abstract-time 2000 --max-cpu 200 --no-resume-requeue --no-eqhint-consider" > loops/$D.log 2>&1
echo "$D $(grep -c THM loops/$D/r1/results.tsv)/$(wc -l < sets/ultest) $(date +%T)" | tee loops/$D.done

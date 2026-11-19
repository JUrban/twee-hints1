#!/bin/bash
# (19 Nov 19:55) Retrained rule models as production members (user, 19:35: "go ahead with the retrained rule model
# member, subsampling sounds good ... read the enigma and Mizar60 and related papers to see all the tricks tried").
# Test: the 400 newest production logs (sets/ul400n, 08:14-19:27 today), held out of every model's training;
# their context snapshot is loops/ULsN19 (production's solved rows before the first of them).
#   M=rm9a ARGS="given/train_only,given/tr30_g1,loops/UL/given --negmax 150" bash abs/rm9.sh
# notes/2026-11-19-retrained-models.md
cd /project/hintwork
export OMP_NUM_THREADS=${TH:-3} OPENBLAS_NUM_THREADS=${TH:-3}
R="venv/bin/python /project/twee/hints/rulemodel.py"
/usr/bin/time -f "%e s %M KB" $R $ARGS --theory --threads ${TH:-3} --test-names sets/ul400n --test-only --ntest 400 \
  --per models/per_$M.tsv --save models/$M.txt --vocab models/$M.vocab > models/$M.log 2>&1
venv/bin/python /project/twee/hints/lgb2bin.py models/$M.txt models/$M.bin >> models/$M.log 2>&1
echo "$M $(grep AUC models/$M.log) $(tail -1 models/$M.log) $(date +%T)" | tee models/$M.done

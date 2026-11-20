#!/bin/bash
# (20 Nov 02:24) exp37's production models retrained on all data: rm9.sh without the held-out 400 (rulemodel.py --all),
# so the newest proofs (the 400 test logs and every proof since 19 Nov 19:50) are in training.
#   M=rm10f ARGS="..." TH=4 bash abs/rm10.sh
cd /project/hintwork
export OMP_NUM_THREADS=${TH:-3} OPENBLAS_NUM_THREADS=${TH:-3}
R="venv/bin/python /project/twee/hints/rulemodel.py"
/usr/bin/time -f "%e s %M KB" $R $ARGS --theory --all --threads ${TH:-3} --save models/$M.txt --vocab models/$M.vocab \
  > models/$M.log 2>&1
venv/bin/python /project/twee/hints/lgb2bin.py models/$M.txt models/$M.bin >> models/$M.log 2>&1
echo "$M $(grep '^train' models/$M.log) $(tail -1 models/$M.log) $(date +%T)" | tee models/$M.done

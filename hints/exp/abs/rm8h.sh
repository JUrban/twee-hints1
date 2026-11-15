#!/bin/bash
# rm8h (15 Nov, user: the later long proofs are worth more for ENIGMA): rm4t's base data (train_only, tr30_g1) plus the loop's
# given logs of rounds 4-5 (loops/UL/given via given/ul45, 2,875); test = the 400 newest round-5 proofs (given/ultest,
# sets/ultest), on which rm4t and rm7t are evaluated too (--load).
cd /project/hintwork
R="venv/bin/python /project/twee/hints/rulemodel.py"
for m in rm4t rm7t; do
  $R given/ultest --theory --test-names sets/ultest --test-only --ntest 400 --load models/$m.txt,models/$m.vocab > models/eval_$m.log 2>&1
done
/usr/bin/time -f "%e s %M KB" $R given/train_only,given/tr30_g1,given/ul45,given/ultest --theory --negmax 150 --threads 4 \
  --test-names sets/ultest --test-only --ntest 400 --save models/rm8h.txt --vocab models/rm8h.vocab > models/rm8h.log 2>&1
echo "rm8h $(grep AUC models/rm8h.log) $(date +%T)" | tee models/rm8h.done

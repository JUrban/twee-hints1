#!/bin/bash
# Oracle bound for the rule filter (15 Nov): rmO = LightGBM trained on the 400 test goals' own given logs (given/ultest),
# so its scores on them are near-perfect; same paired test as abs/mab.sh (threshold 0.1, then a stricter 0.3).
cd /project/hintwork
until grep -q '^done' models/rmO.log; do sleep 20; done
venv/bin/python /project/twee/hints/rulemodel.py given/ultest --theory --test-names sets/ultest --test-only --ntest 400 --threads 2 \
  --load models/rmO.txt,models/rmO.vocab --per models/per_rmO.tsv > models/eval_rmO.log 2>&1
M=rmO T=20 J=3 bash abs/mab.sh
M=rmO X="--rule-threshold 0.3 --rule-penalty 2" TAG=t3 J=3 bash abs/mab2.sh

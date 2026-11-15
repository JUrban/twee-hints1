#!/bin/bash
# After the rm4t/rm7t arms: rm7t at threshold 0.2 (same proof-rule loss as rm4t at 0.1 on ultest: 91.6% vs 93.2% kept,
# 47.6% vs 35.1% of the others deferred).
cd /project/hintwork
until [ -e loops/MB_rm4t_20.done ] && [ -e loops/MB_rm7t_20.done ]; do sleep 20; done
M=rm7t X="--rule-threshold 0.2 --rule-penalty 2" TAG=t2 J=6 bash abs/mab2.sh

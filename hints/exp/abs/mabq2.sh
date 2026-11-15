#!/bin/bash
# Control for rm7t at threshold 0.2: rm4t at threshold 0.2 (is it the model or the stricter filter?).
cd /project/hintwork
until [ -e loops/MB_rm4t_20.done ] && [ -e loops/MB_rm7t_20.done ]; do sleep 20; done
M=rm4t X="--rule-threshold 0.2 --rule-penalty 2" TAG=t2 J=5 bash abs/mab2.sh

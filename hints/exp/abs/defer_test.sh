#!/bin/bash
# Repeated deferral (15 Nov 10:25): twee-e38 --rule-defer-max K. The oracle rmO with defer-once gained nothing online
# (273 vs 271); does a stronger filter let a better model matter? Fresh baseline (current lemma code) vs oracle d3p5.
cd /project/hintwork
export TWEE=/project/bin/twee-e38 J=2
M=rm4t X="--rule-threshold 0.1 --rule-penalty 2 --rule-defer-max 1" TAG=b38 bash abs/mab2.sh &
M=rmO X="--rule-threshold 0.1 --rule-penalty 5 --rule-defer-max 3" TAG=d3p5 bash abs/mab2.sh &
wait

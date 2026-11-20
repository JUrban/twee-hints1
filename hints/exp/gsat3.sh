#!/bin/bash
# (20 Nov 06:59) exp39d (notes/2026-11-20-base-saturation.md): runs steered to unsolved goals G0 of the stronger theories: the base
# axioms with G0 as conjecture, the 100 base theorems nearest to G0 as lemmas, G0's pool as hints; 8 s, 300 runs, tag d.
cd /project/hintwork
python3 -u /project/twee/hints/exp/gensat.py -j ${J:-3} -T ${T:-8} -K ${K:-100} --target --tag d --jobs ${N:-300} --seed ${SEED:-1} > loops/GSAT3.log 2>&1
echo "GSAT3 $(tail -1 loops/GSAT3.log) $(date +%T)" | tee loops/GSAT3.done

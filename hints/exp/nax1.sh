#!/bin/bash
# (20 Nov 05:45) exp39b (notes/2026-11-20-base-saturation.md): 60 unsolved unit goals of theories with more than the base
# axioms, seed 1, in two arms at 20 s: full (as they are) and nax (the extra axioms dropped); same lemmas (6 siblings + 30
# random proven base goals) and hints (the original's pool). 2 workers.
cd /project/hintwork
python3 -u /project/twee/hints/exp/naxrun.py loops/NAX1 -n ${N:-60} -T ${T:-20} -j ${J:-2} --seed ${SEED:-1} > loops/NAX1.log 2>&1
echo "NAX1 $(tail -1 loops/NAX1.log) $(date +%T)" | tee loops/NAX1.done

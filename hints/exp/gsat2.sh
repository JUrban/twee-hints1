#!/bin/bash
# (20 Nov 06:35) exp39c (notes/2026-11-20-base-saturation.md): as gsat1.sh but production-like: 8 s runs, 6 siblings + the 100
# kNN lemmas of G0 (lemmas.LemmaIndex.select), 300 runs, tag c. gsat1 (30 s, 30 random lemmas): 9 new hits in 2.62 CPU h.
cd /project/hintwork
python3 -u /project/twee/hints/exp/gensat.py -j ${J:-3} -T ${T:-8} -K ${K:-100} --knn --tag c --jobs ${N:-300} --seed ${SEED:-1} > loops/GSAT2.log 2>&1
echo "GSAT2 $(tail -1 loops/GSAT2.log) $(date +%T)" | tee loops/GSAT2.done

#!/bin/bash
# (20 Nov 05:39) exp39 pilot (notes/2026-11-20-base-saturation.md): base-theory runs as rule generators for the
# unsolved goals of the stronger theories. 120 runs of 30 abstract s on unsolved goals of the 13 base originals (6
# siblings + 30 random proven base goals as lemma axioms, the original's pool as hints), 3 workers; hits to
# loops/GSAT, which givenmatch.py live (abs/gmlive2.sh) runs.
cd /project/hintwork
python3 -u /project/twee/hints/exp/gensat.py -j ${J:-3} -T ${T:-30} -K ${K:-30} --jobs ${N:-120} --seed ${SEED:-1} > loops/GSAT1.log 2>&1
echo "GSAT1 $(tail -1 loops/GSAT1.log) $(date +%T)" | tee loops/GSAT1.done

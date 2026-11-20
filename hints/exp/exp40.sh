#!/bin/bash
# exp40 (20 Nov): sets/half1 from zero as exp29's PGD (solve_new.sh's defaults since 19 Nov 12:41; 19,309 at 2 hours,
# identical runs differ by about 185), plus exp38's derived-rule transfer: loop.py --given-scan (every failed run's
# given rules against the loop's unsolved unit goals, hits to loops/PGE_GF) and givenmatch.py live on the loop (every
# 300 s: the new given logs of PGE and PGE.xfer and the hits, ancestry at 20 s then prefix at 40 s, the same-statement
# finder; proofs into loops/PGE). notes/2026-11-20-from-zero-given.md
cd /project/hintwork
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
mkdir -p loops/PGE_GF
ARM=PGE TWEE=/project/bin/twee-pg61 PG= CASCADE=5,40,80,160,320 \
  LOOPARGS="--chain-level 1 --variants unf@0,k60@0,k100@0,k200@0,k400@0,kd@0,k60,p9,unf,two,nom --variants-after 3 --variant-budget 80 --priors L1=1.73,L2=1.1 --ratio-order --explore 0.2 --explore-labels L1,Vk100@0,Vk200@0,Vk400@0,Vkd@0 --given-scan /project/hintwork/loops/PGE_GF" \
  bash abs/or_test.sh &
OT=$!
until [ -f loops/PGE/config.json ] || ! kill -0 $OT 2>/dev/null; do sleep 2; done
python3 -u /project/twee/hints/givenmatch.py live loops/PGE_GML --dst PGE --dirs PGE,PGE.xfer --gfail PGE_GF \
  --set /project/hintwork/sets/half1 --every 300 -j 2 -- \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab \
  --model-theory --lemmas 6 --lemma-knn 30 --lemma-subsets --lemma-after --pool original --twee /project/bin/twee-pg61 \
  --wall-factor 15 --args="--abstract-time 2000 --no-eqhint-consider" > loops/PGE_GML.log 2>&1 &
GM=$!
wait $OT
desc() { for c in $(ps -o pid= --ppid $1); do desc $c; done; echo $1; }
kill $(desc $GM) 2>/dev/null
echo "exp40 done $(date +%T)" > loops/exp40.done

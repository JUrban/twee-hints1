#!/bin/bash
# (20 Nov 07:17) exp40's live loop, restarted with the pending queue (hits wait until the loop has failed on their
# goal; at most 60 run per cycle) and without the instance scan (--no-inst). The first one (abs/exp40.sh) stopped at
# 07:16 in its 2nd cycle, which had 3,975 goals hit. Ends with the arm (loops/PGE.done).
cd /project/hintwork
python3 -u /project/twee/hints/givenmatch.py live loops/PGE_GML --dst PGE --dirs PGE,PGE.xfer --gfail PGE_GF \
  --set /project/hintwork/sets/half1 --every 300 -j 2 --cap 60 --no-inst -- \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab \
  --model-theory --lemmas 6 --lemma-knn 30 --lemma-subsets --lemma-after --pool original --twee /project/bin/twee-pg61 \
  --wall-factor 15 --args="--abstract-time 2000 --no-eqhint-consider" >> loops/PGE_GML.log 2>&1 &
GM=$!
until [ -f loops/PGE.done ] || ! kill -0 $GM 2>/dev/null; do sleep 20; done
desc() { for c in $(ps -o pid= --ppid $1); do desc $c; done; echo $1; }
kill $(desc $GM) 2>/dev/null
echo "exp40 live done $(date +%T)" > loops/exp40live.done

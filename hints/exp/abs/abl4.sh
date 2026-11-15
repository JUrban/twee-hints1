#!/bin/bash
# rm6t (rm4t data + the full loop's 5,303 proofs; u3 originals held out) on u3a189, 20 abstract s, online, from V2base:
# U3zm ENIGMA only (rm4t: U3ym 42), U3zf full with 3 siblings (rm4t: U3xf 58). Starts after abl3.sh (U3k20.done).
until [ -s /project/hintwork/loops/U3k20.done ]; do sleep 60; done
cd /project/hintwork
B="python3 /project/twee/hints/loop.py sets/u3a189"
C="--init loops/V2base --start 1 --rounds 1 --timeout 20 --twee /project/bin/twee-e22 --keep-out -j 5 --pool original --online --wall-factor 15"
M="--model --model-fixed /project/hintwork/models/rm6t.bin,/project/hintwork/models/rm6t.vocab --model-theory"
A="--abstract-time 2000 --max-cpu 200"
$B loops/U3zm $C $M --max-hints 0 --rerun-unhinted --args="$A" > loops/U3zm.log 2>&1
echo "U3zm $(grep -c THM loops/U3zm/r1/results.tsv) $(date +%T)" | tee loops/U3zm.done
$B loops/U3zf $C $M --lemmas 3 --lemma-knn 10 --lemma-subsets --args="$A" > loops/U3zf.log 2>&1
echo "U3zf $(grep -c THM loops/U3zf/r1/results.tsv) $(date +%T)" | tee loops/U3zf.done

#!/bin/bash
# Bigloop test (user's question on Veroff's P9loop/Bigloop, 14 Nov 17:00), equal budget 80 abstract s per goal.
# sets/fr100: 100 goals (88 originals) the full loop failed at 20 s in round 4 (L0) that have a proven neighbour (gap 1);
# init loops/ULsI = snapshot of the full loop's 40,961 proofs (pools, lemmas). Production config (rm4t, 6 lemmas
# either side + 10 subset kNN, whole-original pools), twee-e30, 2 workers per arm. Starts when the u3n73 arms end.
#  BRS: --resume, 4 rounds x 20 s                         (= the cascade's next level, 80 s by resume)
#  BP9: --p9loop --p9-orders 4, 4 rounds x 20 s           (P9loop: fresh runs + matcher lemmas + another ordering)
#  BBL: --p9loop --p9-orders 8 --p9-parallel 2, 2 x 20 s  (Bigloop: 2 orderings at once per round, shared lemmas)
while ps -eo args | grep -q "[l]oop.py sets/u3n73"; do sleep 60; done
cd /project/hintwork
L="python3 /project/twee/hints/loop.py sets/fr100"
C="--init loops/ULsI --start 1 --timeout 20 --twee /project/bin/twee-e30 --keep-out -j 2 --pool original --wall-factor 15"
M="--model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory --lemmas 6 --lemma-knn 10 --lemma-subsets --lemma-after"
A="--abstract-time 2000 --max-cpu 200"
$L loops/BRS $C $M --rounds 4 --resume --args="$A" > loops/BRS.log 2>&1 &
$L loops/BP9 $C $M --rounds 4 --p9loop --p9-orders 4 --args="$A" > loops/BP9.log 2>&1 &
$L loops/BBL $C $M --rounds 2 --p9loop --p9-orders 8 --p9-parallel 2 --args="$A" > loops/BBL.log 2>&1 &
wait
for d in BRS BP9 BBL; do echo "$d $(awk -F'\t' '$2>0' loops/$d/solved.tsv | wc -l) $(date +%T)" | tee loops/$d.done; done

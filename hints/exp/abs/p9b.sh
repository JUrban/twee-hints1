#!/bin/bash
# Veroff P9loop test (user's question, 14 Nov): sets/u3n73 (the 73 nil3_31 goals N3x6 left unsolved), init N3xI
# (all N3x6 proofs as round 0), 4 rounds x 20 abstract s, rm4t + 6 lemmas + 10 subset kNN, whole-original pools.
#  P9a: --p9loop                (fresh runs; hint matchers of earlier failed runs of the goal become axioms)
#  P9o: --p9loop --p9-orders 4  (the same, each round with another KBO precedence, round 1 = default)
#  RSa: --resume                (each round continues the saved state 20 s more; same total budget)
# Then: V2q008 (queue cost), U3n4/U3n7 (rm7t online).
cd /project/hintwork
L="python3 /project/twee/hints/loop.py sets/u3n73"
C="--init loops/N3xI --start 1 --rounds 4 --timeout 20 --twee /project/bin/twee-e30 --keep-out -j 2 --pool original --wall-factor 15"
M="--model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory --lemmas 6 --lemma-knn 10 --lemma-subsets"
A="--abstract-time 2000 --max-cpu 200"
$L loops/P9a $C $M --p9loop --args="$A" > loops/P9a.log 2>&1 &
$L loops/P9o $C $M --p9loop --p9-orders 4 --args="$A" > loops/P9o.log 2>&1 &
$L loops/RSa $C $M --resume --args="$A" > loops/RSa.log 2>&1 &
wait
for d in P9a P9o RSa; do echo "$d $(awk -F'\t' '$2>0' loops/$d/solved.tsv | wc -l) $(date +%T)" | tee loops/$d.done; done
V="python3 /project/twee/hints/loop.py sets/v2_half"
C="--init loops/V2base --start 1 --rounds 1 --timeout 120 --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory --lemmas 6 --lemma-after --lemma-knn 10 --lemma-subsets --twee /project/bin/twee-e27 --keep-out -j 5 --pool original --wall-factor 15"
$V loops/V2q008 $C --args="--abstract-time 2000 --max-cpu 1200 --queue-cost 0.008 --progress 20" > loops/V2q008.log 2>&1
echo "V2q008 $(grep -c THM loops/V2q008/r1/results.tsv) $(date +%T)" | tee loops/V2q008.done
bash abs/rm7.sh

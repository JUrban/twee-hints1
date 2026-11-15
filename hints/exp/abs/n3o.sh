#!/bin/bash
# Consider-emulation for open hints only (14 Nov 20:00): twee-e36 --eqhint-consider-open (fingerprint of a live hint
# no rule has matched yet). One 30 s run: 48.0 s user vs 67.9 (all) vs 46.4 (off), matched 971/973/981.
# N3o = N3x6 (77) / N3c (consider off) + --eqhint-consider-open. Starts when N3c ends.
while [ ! -f /project/hintwork/loops/N3c.done ]; do sleep 30; done
cd /project/hintwork
C="--init loops/V2base --start 1 --rounds 1 --timeout 20 --keep-out -j 3 --pool original --online --wall-factor 15"
M="--model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory"
A="--abstract-time 2000 --max-cpu 200 --eqhint-consider-open"
python3 /project/twee/hints/loop.py sets/u3n150 loops/N3o $C --twee /project/bin/twee-e36 $M --lemmas 6 --lemma-knn 10 --lemma-subsets --args="$A" > loops/N3o.log 2>&1
echo "N3o $(grep -c THM loops/N3o/r1/results.tsv) $(date +%T)" | tee loops/N3o.done

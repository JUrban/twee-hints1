#!/bin/bash
# cascade scheduling vs a plain 80 s round, 2 h each on 5 cores, on sets/u3 from U3po's proofs (U3poI).
until [ -s /project/hintwork/loops/U3lb.done ]; do sleep 30; done
cd /project/hintwork
M="--model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory --lemmas 3 --lemma-knn 10 --lemma-subsets --twee /project/bin/twee-e22 --keep-out -j 5 --pool original --wall-factor 15"
timeout 7200 python3 /project/twee/hints/loop.py sets/u3 loops/U3cas --init loops/U3poI --start 1 --cascade 20,80,320 --cascade-start -1 --reserve 0 $M --args="--abstract-time 2000" > loops/U3cas.log 2>&1
pkill -f "loops/U3cas/tmp"
echo "U3cas $(grep -c THM loops/U3cas/r1/results.tsv) $(date +%T)" | tee loops/U3cas.done
timeout 7200 python3 /project/twee/hints/loop.py sets/u3 loops/U3r80 --init loops/U3poI --start 1 --rounds 1 --timeout 80 --online --give-up 30 $M --args="--abstract-time 2000 --max-cpu 800" > loops/U3r80.log 2>&1
pkill -f "loops/U3r80/tmp"
echo "U3r80 $(grep -c THM loops/U3r80/r1/results.tsv) $(date +%T)" | tee loops/U3r80.done

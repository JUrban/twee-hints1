#!/bin/bash
# ENIGMA / hints ablation on the 189 aK2_eq_aK3_a goals (20 abstract s, online, from V2base; full system = U3po: 60),
# then the cascade-vs-round test (u3c2.sh body).
until [ -s /project/hintwork/loops/U3lb.done ]; do sleep 30; done
cd /project/hintwork
B="python3 /project/twee/hints/loop.py sets/u3a189"
C="--init loops/V2base --start 1 --rounds 1 --timeout 20 --twee /project/bin/twee-e22 --keep-out -j 5 --pool original --online --wall-factor 15"
M="--model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory"
L="--lemmas 3 --lemma-knn 10 --lemma-subsets"
A="--abstract-time 2000 --max-cpu 200"
$B loops/U3xm $C $M $L --max-hints 0 --rerun-unhinted --args="$A" > loops/U3xm.log 2>&1   # ENIGMA + lemmas, no hints
echo "U3xm $(grep -c THM loops/U3xm/r1/results.tsv) $(date +%T)" | tee loops/U3xm.done
$B loops/U3xh $C $L --args="$A" > loops/U3xh.log 2>&1                                       # hints + lemmas, no ENIGMA
echo "U3xh $(grep -c THM loops/U3xh/r1/results.tsv) $(date +%T)" | tee loops/U3xh.done
$B loops/U3xl $C $L --max-hints 0 --rerun-unhinted --args="$A" > loops/U3xl.log 2>&1        # lemmas only
echo "U3xl $(grep -c THM loops/U3xl/r1/results.tsv) $(date +%T)" | tee loops/U3xl.done
$B loops/U3x0 $C --max-hints 0 --rerun-unhinted --args="$A" > loops/U3x0.log 2>&1           # plain twee 20 s
echo "U3x0 $(grep -c THM loops/U3x0/r1/results.tsv) $(date +%T)" | tee loops/U3x0.done
M2="$M $L --twee /project/bin/twee-e22 --keep-out -j 5 --pool original --wall-factor 15"
timeout 7200 python3 /project/twee/hints/loop.py sets/u3 loops/U3cas --init loops/U3poI --start 1 --cascade 20,80,320 --cascade-start -1 --reserve 0 $M2 --args="--abstract-time 2000" > loops/U3cas.log 2>&1
pkill -f "loops/U3cas/tmp"
echo "U3cas $(grep -c THM loops/U3cas/r1/results.tsv) $(date +%T)" | tee loops/U3cas.done
timeout 7200 python3 /project/twee/hints/loop.py sets/u3 loops/U3r80 --init loops/U3poI --start 1 --rounds 1 --timeout 80 --online --give-up 30 $M2 --args="--abstract-time 2000 --max-cpu 800" > loops/U3r80.log 2>&1
pkill -f "loops/U3r80/tmp"
echo "U3r80 $(grep -c THM loops/U3r80/r1/results.tsv) $(date +%T)" | tee loops/U3r80.done

#!/bin/bash
# ENIGMA-style loop vs hint loop on sets/e3 (all 1,934 goals of nil3_31, aK2_eq_aK3_a, R1dist_to_aa1),
# 4 rounds at 5 abstract s, no lemmas, 5 workers; starts after the penalty sweep (N3p20.done).
#  EL : rule model retrained every round on base data (train_only, tr30_g1) + the loop's proofs (shortest per
#       problem); every round reruns ALL goals (--rerun-solved). No hints.
#  HL : hint loop, no model: whole-original pools, rounds rerun the unsolved.
#  EHL: both (retrained model + hints, rerun all).
until [ -s /project/hintwork/loops/N3p20.done ]; do sleep 60; done
cd /project/hintwork
L="python3 /project/twee/hints/loop.py sets/e3"
C="--rounds 4 --timeout 5 --twee /project/bin/twee-e22 -j 5 --pool original --wall-factor 15"
E="--model --model-theory --given-extra given/train_only,given/tr30_g1 --model-negmax 200 --model-threads 5 --rerun-solved"
A="--abstract-time 2000 --max-cpu 100"
$L loops/EL $C $E --max-hints 0 --rerun-unhinted --args="$A" > loops/EL.log 2>&1;  echo "EL $(tail -1 loops/EL.log) $(date +%T)" | tee loops/EL.done
$L loops/HL $C --args="$A" > loops/HL.log 2>&1;                                       echo "HL $(tail -1 loops/HL.log) $(date +%T)" | tee loops/HL.done
$L loops/EHL $C $E --args="$A" > loops/EHL.log 2>&1;                                  echo "EHL $(tail -1 loops/EHL.log) $(date +%T)" | tee loops/EHL.done

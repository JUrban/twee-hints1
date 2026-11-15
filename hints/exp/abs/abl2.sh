#!/bin/bash
# Ablation part 2: guidance WITHOUT lemma import on u3a189 (20 abstract s, online, from V2base).
# U3ym ENIGMA only, U3yh hints only, U3yb ENIGMA + hints. Starts after the cascade test (U3r80.done).
until [ -s /project/hintwork/loops/U3r80.done ]; do sleep 60; done
cd /project/hintwork
B="python3 /project/twee/hints/loop.py sets/u3a189"
C="--init loops/V2base --start 1 --rounds 1 --timeout 20 --twee /project/bin/twee-e22 --keep-out -j 5 --pool original --online --wall-factor 15"
M="--model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory"
A="--abstract-time 2000 --max-cpu 200"
$B loops/U3ym $C $M --max-hints 0 --rerun-unhinted --args="$A" > loops/U3ym.log 2>&1
echo "U3ym $(grep -c THM loops/U3ym/r1/results.tsv) $(date +%T)" | tee loops/U3ym.done
$B loops/U3yh $C --args="$A" > loops/U3yh.log 2>&1
echo "U3yh $(grep -c THM loops/U3yh/r1/results.tsv) $(date +%T)" | tee loops/U3yh.done
$B loops/U3yb $C $M --args="$A" > loops/U3yb.log 2>&1
echo "U3yb $(grep -c THM loops/U3yb/r1/results.tsv) $(date +%T)" | tee loops/U3yb.done

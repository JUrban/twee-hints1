#!/bin/bash
# Ablation control: the full system rerun on u3a189 alone (U3po ran all of sets/u3 interleaved),
# then lemma-count variants (more siblings, more subset-kNN lemmas), all 20 abstract s, online, from V2base.
cd /project/hintwork
B="python3 /project/twee/hints/loop.py sets/u3a189"
C="--init loops/V2base --start 1 --rounds 1 --timeout 20 --twee /project/bin/twee-e22 --keep-out -j 5 --pool original --online --wall-factor 15"
M="--model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory"
A="--abstract-time 2000 --max-cpu 200"
$B loops/U3xf $C $M --lemmas 3 --lemma-knn 10 --lemma-subsets --args="$A" > loops/U3xf.log 2>&1
echo "U3xf $(grep -c THM loops/U3xf/r1/results.tsv) $(date +%T)" | tee loops/U3xf.done
$B loops/U3l6 $C $M --lemmas 6 --lemma-knn 10 --lemma-subsets --args="$A" > loops/U3l6.log 2>&1
echo "U3l6 $(grep -c THM loops/U3l6/r1/results.tsv) $(date +%T)" | tee loops/U3l6.done
$B loops/U3k20 $C $M --lemmas 3 --lemma-knn 20 --lemma-subsets --args="$A" > loops/U3k20.log 2>&1
echo "U3k20 $(grep -c THM loops/U3k20/r1/results.tsv) $(date +%T)" | tee loops/U3k20.done

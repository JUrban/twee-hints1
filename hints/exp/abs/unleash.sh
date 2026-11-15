#!/bin/bash
# unleash.sh [TIMEOUTS] [J]: Veroff-style loop on everything the 4 s benchmark loop left unsolved (ALL_lem r0-2 + G1 = V2base, 33,720):
# online whole-original pools (each proof feeds the runs not yet started), goals in goal order, an original is left for the round
# after 30 consecutive failures; rm4t + 3 sibling lemmas + 10 subset-kNN lemmas; twee-e20
cd /project/hintwork
T=${1:-5,20}; J=${2:-14}
R=$(echo $T | tr ',' '\n' | wc -l)
python3 /project/twee/hints/loop.py sets/all loops/UL --init loops/V2base --start 1 --rounds $R --timeout 0,$T \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 3 --lemma-knn 10 --lemma-subsets --twee /project/bin/twee-e20 --keep-out -j $J --pool original --online \
  --give-up 30 --wall-factor 15 --args="--abstract-time 2000 --max-cpu 400" > loops/UL.log 2>&1
echo "UL: $(tail -1 loops/UL.log) $(date +%T)" | tee loops/UL.done

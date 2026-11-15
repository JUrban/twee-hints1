#!/bin/bash
# Live sketch climber beside the full loop (15 Nov 00:39): climb.py --live loops/UL takes UL's stalled goals (last result
# in round 5 a failed L1+ deepening run, unsolved), nearest proven goal below first, with the CL4/CL5 config (8 nearest
# unproven siblings + 8 kNN unproven goals of other originals, --fill 3; on sg3 CL5 10/64 at 5.3 proofs/CPU-h vs fresh
# (15 Nov 01:06) --cpus 20: start climbs only while fewer than 20 twee processes run (UL11 is often idle), -j 12 caps it.
# 80 s 4.3); real proofs go into loops/UL (hints, then a solved.tsv row) and UL10 (--sync 60) takes them in.
cd /project/hintwork
python3 /project/twee/hints/climb.py sets/all loops/CLV --live loops/UL --exclude sets/sg1,sets/sg3 \
  --m 8 --knn 8 --runs 12 --sketch-time 5 --final-time 20 --fill 3 -j "${J:-12}" --cpus "${CPUS:-20}" -- \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 6 --lemma-knn 10 --lemma-subsets --lemma-after --pool original --twee /project/bin/twee-e37 --wall-factor 15 \
  --args="--abstract-time 2000 --no-eqhint-consider" > loops/CLV.log 2>&1
echo "CLV $(tail -1 loops/CLV.log) $(date +%T)" | tee loops/CLV.done

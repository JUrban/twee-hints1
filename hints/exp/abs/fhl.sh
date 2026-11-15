#!/bin/bash
# Control for EHL (14 Nov 16:25): FHL = hints + the FIXED round-0 model of EHL (base data only, like rm4t), no retraining,
# no reruns of solved goals = the production setting (UL uses fixed rm4t + hints). EHL - FHL = what in-loop retraining adds.
# Rounds 1-3 from EHL's round 0 (identical by construction), 5 abstract s, 5 workers. Starts after EHL.done.
until [ -s /project/hintwork/loops/EHL.done ]; do sleep 60; done
cd /project/hintwork
python3 /project/twee/hints/loop.py sets/e3 loops/FHL --init loops/EHL --start 1 --rounds 3 --timeout 5 \
  --twee /project/bin/twee-e22 -j 5 --pool original --wall-factor 15 \
  --model --model-fixed loops/EHL/models/r0.bin,loops/EHL/models/r0.txt.vocab --model-theory \
  --args="--abstract-time 2000 --max-cpu 100" > loops/FHL.log 2>&1
echo "FHL $(tail -1 loops/FHL.log) $(date +%T)" | tee loops/FHL.done

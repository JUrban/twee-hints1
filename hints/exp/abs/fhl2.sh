#!/bin/bash
# Control for EHL (14 Nov 16:50): FHL = hints + the FIXED round-0 model of EHL (base data only, like rm4t), no retraining,
# no reruns of solved goals = the production setting (UL uses fixed rm4t + hints). EHL - FHL = what in-loop retraining adds.
# Rounds 1-2 from EHL's round 0 (identical by construction), 5 abstract s, 5 workers. EHL is stopped after its round 2
# (round 3 of EL/HL added 4 and 2; CPU budget). Starts when EHL's round 2 is logged.
until grep -q "^round 2" /project/hintwork/loops/EHL/log.txt 2>/dev/null; do sleep 30; done
cd /project/hintwork
pid=$(ps -eo pid,args | awk '$3 ~ /loop.py/ && $5=="loops/EHL" {print $1}')
[ -n "$pid" ] && kill $pid
sleep 5
ps -eo pid,args | grep "[E]HL/tmp" | awk '{print $1}' | xargs -r kill
python3 /project/twee/hints/loop.py sets/e3 loops/FHL --init loops/EHL --start 1 --rounds 2 --timeout 5 \
  --twee /project/bin/twee-e22 -j 5 --pool original --wall-factor 15 \
  --model --model-fixed loops/EHL/models/r0.bin,loops/EHL/models/r0.txt.vocab --model-theory \
  --args="--abstract-time 2000 --max-cpu 100" > loops/FHL.log 2>&1
echo "FHL $(tail -1 loops/FHL.log) $(date +%T)" | tee loops/FHL.done

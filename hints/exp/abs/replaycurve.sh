#!/bin/bash
# Log the replay's curve (16 Nov 12:10): every 60 s, minutes since the start, goals of sets/rp3 proved, and the
# summed run time of loops/RP/r1/results.tsv in CPU hours, to loops/RP.curve.
cd /project/hintwork
t0=$(stat -c %Y loops/RP/config.json)
while [ ! -f loops/RP.done ]; do
  awk -F'\t' -v m=$(( ($(date +%s) - t0) / 60 )) '{t+=$3; if ($2=="THM") p++} END {printf "%d\t%d\t%.2f\n", m, p, t/3600}' loops/RP/r1/results.tsv >> loops/RP.curve
  sleep 60
done

#!/bin/bash
# exp90: the cost of listened goals in a 160 abstract s final (the copied nsmr_to_aa1__goal_893 final of CLS71, 8 listened)
D=/tmp/claude-1001/-project/06816eaa-f48d-4d65-80b0-498c3b54febf/scratchpad/lcost90
cd /project/hintwork
for v in with without; do
  ( /usr/bin/time -f "$v cpu %U+%S wall %e maxrss %M" /project/bin/twee-e61l $D/$v.p --max-time 160.0 --no-colour --quiet --no-proof --print-hints --abstract-time 2000 --no-eqhint-consider --conditional-encoding fresh --max-cpu 1600.0 --rule-model /project/hintwork/models/rm4t.bin --rule-vocab /project/hintwork/models/rm4t.vocab --rule-goal $D/rgoal --rule-threshold 0.1 --rule-penalty 2 --hints-file $D/hints --pg-threshold 0.25 --ground-joining-branch-limit 100 > $D/$v.out 2> $D/$v.time ) &
done
wait
for v in with without; do echo "$v: $(cat $D/$v.time | tail -1) $(grep -c '^SOLVEDGOAL' $D/$v.out) solved, $(grep '^WORK\|^RESULT' $D/$v.out | tr '\n' ' ')"; done

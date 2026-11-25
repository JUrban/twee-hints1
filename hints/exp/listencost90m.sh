#!/bin/bash
# exp90: the cost of 8 listened goals in a 160 abstract s final with twee-e61m (the search unchanged by them)
D=/tmp/claude-1001/-project/06816eaa-f48d-4d65-80b0-498c3b54febf/scratchpad/lcost90
cd /project/hintwork
for v in with without; do
  ( /usr/bin/time -f "$v cpu %U+%S wall %e maxrss %M" /project/bin/twee-e61m $D/$v.p --max-time 160.0 --no-colour --quiet --no-proof --print-hints --abstract-time 2000 --no-eqhint-consider --conditional-encoding fresh --max-cpu 1600.0 --rule-model /project/hintwork/models/rm4t.bin --rule-vocab /project/hintwork/models/rm4t.vocab --rule-goal $D/rgoal --rule-threshold 0.1 --rule-penalty 2 --hints-file $D/hints --pg-threshold 0.25 --ground-joining-branch-limit 100 > $D/m.$v.out 2> $D/m.$v.time ) &
done
wait
for v in with without; do echo "$v: $(tail -1 $D/m.$v.time) listened solved $(grep -c '^SOLVEDGOAL listen' $D/m.$v.out), $(grep '^WORK\|^RESULT' $D/m.$v.out | tr '\n' ' ')"; done

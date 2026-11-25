#!/bin/bash
# exp90: the cost of all the original's unsolved plain goals (120 pass the plain-equation check) listened in a 160 abstract s final, twee-e61m
D=/tmp/claude-1001/-project/06816eaa-f48d-4d65-80b0-498c3b54febf/scratchpad/lcost90
cd /project/hintwork
/usr/bin/time -f "all cpu %U+%S wall %e maxrss %M" /project/bin/twee-e61m $D/all.p --max-time 160.0 --no-colour --quiet --no-proof --print-hints --abstract-time 2000 --no-eqhint-consider --conditional-encoding fresh --max-cpu 1600.0 --rule-model /project/hintwork/models/rm4t.bin --rule-vocab /project/hintwork/models/rm4t.vocab --rule-goal $D/rgoal --rule-threshold 0.1 --rule-penalty 2 --hints-file $D/hints --pg-threshold 0.25 --ground-joining-branch-limit 100 > $D/all.out 2> $D/all.time
echo "all: $(tail -1 $D/all.time) listened $(grep -c '^SOLVEDGOAL listen' $D/all.out) $(grep '^WORK\|^RESULT' $D/all.out | tr '\n' ' ')"
grep '^SOLVEDGOAL listen' $D/all.out

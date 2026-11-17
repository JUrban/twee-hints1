#!/bin/bash
# (17 Nov 18:06) e54 with the PG flags off against e44: identical stdout (proof, hints) and WORK on 24 testbed goals
cd /project/hintwork/pg/eqchk54
for g in $(head -24 ../tb/all.goals); do
  w=$(grep "/$g.p " ../tb/cmds.all | cut -d' ' -f2-)
  for b in e44 e54; do echo "/project/bin/twee-$b $w > $g.$b 2>/dev/null"; done
done | xargs -P 4 -I{} sh -c '{}'
n=0; for g in $(head -24 ../tb/all.goals); do cmp -s $g.e44 $g.e54 || { n=$((n+1)); echo "DIFF $g"; }; done; echo "differ: $n of 24"

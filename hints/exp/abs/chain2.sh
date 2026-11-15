#!/bin/bash
# after the Prover9 long runs: Prover9 SFDF loops, then battery 6, then full round 3
until [ -s /tmp/claude-1001/-project/06816eaa-f48d-4d65-80b0-498c3b54febf/tasks/braglt9vt.output ]; do sleep 20; done
cd /project/hintwork
L="python3 /project/twee/hints/p9loop.py sets/fam2"
$L p9/g_orig --givens 150,150,150,220 -j 6 > p9/g_orig.log 2>&1 &
$L p9/g_expand --givens 150,150,150,220 -j 6 --convert expand > p9/g_expand.log 2>&1 &
$L p9/g_direct --givens 150,150,150,220 -j 6 --convert direct > p9/g_direct.log 2>&1 &
wait
for d in orig expand direct; do echo "p9 $d: $(tail -1 p9/g_$d.log)"; done
sed -i 's|^until .*b1m2z11nk.*$|true|; s|^until .*braglt9vt.*$|true|' abs/batt6.sh abs/q_all3.sh
bash abs/batt6.sh
bash abs/q_all3.sh

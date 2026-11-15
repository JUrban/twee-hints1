#!/bin/bash
# after the twee long eval: P9 SFDF loops; twee extension + P9 long (with/without hints); battery 6; full round 3
F=/tmp/claude-1001/-project/06816eaa-f48d-4d65-80b0-498c3b54febf/tasks/b8wecjqk9.output
until [ "$(grep -c solved $F 2>/dev/null)" -ge 2 ]; do sleep 15; done
cd /project/hintwork
echo "start $(date +%T)"
L="python3 /project/twee/hints/p9loop.py sets/fam2"
$L p9/g_orig --givens 150,150,150,220 -j 6 > p9/g_orig.log 2>&1 &
$L p9/g_expand --givens 150,150,150,220 -j 6 --convert expand > p9/g_expand.log 2>&1 &
$L p9/g_direct --givens 150,150,150,220 -j 6 --convert direct > p9/g_direct.log 2>&1 &
wait
for d in orig expand direct; do echo "p9 $d: $(tail -1 p9/g_$d.log)"; done
echo "sfdf done $(date +%T)"
python3 /project/twee/hints/stallsim.py long/G1 --on-hints 60 > long/extend_names
echo "extending $(wc -l < long/extend_names) twee runs to 600 abstract s"
J=9 long/run_long.sh G1x 600 1 long/extend_names &
J=9 long/p9_long.sh P1 3000 1 sets/fam2_long &
wait
until [ -n "$(grep '^V2p:' /tmp/claude-1001/-project/06816eaa-f48d-4d65-80b0-498c3b54febf/tasks/V2P_TASK.output 2>/dev/null)" ] || [ -n "$(grep '^V2p:' /project/hintwork/loops/V2p.done 2>/dev/null)" ]; do sleep 20; done
J=9 long/p9_long.sh P0 3000 0 sets/fam2_long &
bash abs/v2.sh k &
wait
bash abs/v2.sh n &
wait
echo "long done $(date +%T)"
sed -i 's|^until .*b1m2z11nk.*$|true|; s|^until .*braglt9vt.*$|true|' abs/batt6.sh abs/q_all3.sh
bash abs/batt6.sh
bash abs/q_all3.sh
echo "all done $(date +%T)"

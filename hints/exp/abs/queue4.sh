#!/bin/bash
# P0 (Prover9 no hints) alongside V2p; then V2k + V2n; then battery 6 and the full round 3
cd /project/hintwork
echo "start $(date +%T)"
J=9 long/p9_long.sh P0 3000 0 sets/fam2_long
until grep -q '^V2p:' loops/V2p.done 2>/dev/null; do sleep 20; done
echo "V2p done $(date +%T)"
bash abs/v2.sh k &
bash abs/v2.sh n &
wait
echo "long done $(date +%T)"
sed -i 's|^until .*b1m2z11nk.*$|true|; s|^until .*braglt9vt.*$|true|' abs/batt6.sh abs/q_all3.sh
bash abs/batt6.sh
bash abs/q_all3.sh
echo "all done $(date +%T)"

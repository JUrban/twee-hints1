#!/bin/bash
# when U3k has done all 343 aK2_eq_aK3_a goals: stop it, then u3a variants (ko, to; then p once U3po is done)
cd /project/hintwork
until [ "$(grep -c '^aK2_eq_aK3_a' loops/U3k/r1/results.tsv)" -ge 343 ]; do sleep 30; done
for p in $(pgrep -f 'u3.sh k$') $(pgrep -f 'loop.py sets/u3 loops/U3k '); do kill $p; done
sleep 3
for p in $(pgrep -f 'twee-e19 loops/U3k/'); do kill $p; done
echo "U3k stopped $(date +%T)"
J=5 bash abs/u3c.sh ko &
J=5 bash abs/u3c.sh to &
until [ -s loops/U3po.done ]; do sleep 30; done
J=5 bash abs/u3c.sh p &
wait
echo "q7 done $(date +%T)"

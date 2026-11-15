#!/bin/bash
# u3 queue: po + k now (5 jobs each, beside V2p r2), then ko + p
cd /project/hintwork
J=5 bash abs/u3.sh po &
J=5 bash abs/u3.sh k &
wait
J=5 bash abs/u3.sh ko &
J=5 bash abs/u3.sh p &
wait
echo "u3 done $(date +%T)"

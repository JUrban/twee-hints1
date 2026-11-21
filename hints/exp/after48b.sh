#!/bin/bash
# (21 Nov 06:50) exp50's launcher (notes/2026-11-21-retry-time.md): a third arm beside exp49. Waits for P2R's line in
# loops/AFTER48.pids (abs/after48.sh writes it when it starts P2Q and P2R), then starts P2S on the same base with
# --retry-time 3: half2 from zero, 6 workers, 5 hours. A non-empty loops/P2S.args replaces its options.
cd /project/hintwork
until grep -q "^P2R " loops/AFTER48.pids 2>/dev/null; do sleep 20; done
LA=$(grep "^P2R " loops/AFTER48.pids | tail -n 1 | sed 's/^.*LOOPARGS=//')
LA="$LA --retry-time 3"
[ -s loops/P2S.args ] && LA=$(cat loops/P2S.args)
if [ -e loops/P2S ]; then echo "loops/P2S exists, not started" >> loops/AFTER48.pids; exit 1; fi
HOURS=5 SET=sets/half2 ARM=P2S LOOPARGS="$LA" nohup bash abs/or_test2.sh > /dev/null 2>&1 &
echo "P2S $! $(date +%T) LOOPARGS=$LA" >> loops/AFTER48.pids

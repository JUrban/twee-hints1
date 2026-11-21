#!/bin/bash
# (21 Nov 07:25) notes/2026-11-21-dispatch-profile.md: when exp48 ends (loops/P2N.done, loops/P2O.done), a profile of
# loop.py's threads at 12 workers on all goals from zero (Z7's setting; exp/stacksample.py, 6 minutes, loops/PRB),
# then loops/GO49, so abs/after48.sh starts exp49 (and abs/after48b.sh exp50) at once (it waits up to 20 minutes).
cd /project/hintwork
until [ -e loops/P2N.done ] && [ -e loops/P2O.done ]; do sleep 20; done
echo "prof12 start $(date +%T)" >> loops/AFTER48.pids
if [ ! -e loops/PRB ]; then
  sed -e "s|^H=.*|H=/project/twee/hints|" -e 's|python3 -u "\$H/loop.py"|python3 -u /project/twee/hints/exp/stacksample.py /project/hintwork/loops/PRB.prof.txt "$H/loop.py"|' /project/twee/hints/solve_new.sh > loops/PRB.solve_new.sh
  SCHED= XEVERY=300 LOOPARGS="--retry-class --yield-discount 2000 --reexplore 12:0.25" timeout 900 bash loops/PRB.solve_new.sh sets/all loops/EMPTY loops/PRB 12 0.1 > loops/PRB.out 2>&1
  touch loops/PRB.done
fi
touch loops/GO49
echo "prof12 end, GO49 $(date +%T)" >> loops/AFTER48.pids

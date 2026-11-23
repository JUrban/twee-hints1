#!/bin/bash
# (23 Nov) After PLW1 and its import: stop abs/plainlive.sh (cond/PLNL.stop, after its cycle), then abs/plainlive2.sh
# with PREV_N its last cycle and PREV_W cond/PLW1.
cd /project/hintwork
until grep -q "PLW1 imported" cond/PLW1.pids 2>/dev/null; do sleep 30; done
touch cond/PLNL.stop
while kill -0 3017446 2>/dev/null; do sleep 15; done
rm -f cond/PLNL.stop
last=$(ls -d cond/PLNL/c[0-9]* | grep -v '\.' | sed 's/.*\/c//' | sort -n | tail -1)
PREV_N=cond/PLNL/c$last PREV_W=cond/PLW1 exec bash abs/plainlive2.sh

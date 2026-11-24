#!/bin/bash
# (24 Nov) When the resumed HLW1 sweep has ended (cond/SWEEPQ.log "HLW1 done" after "HLW1 resumed"): stop
# abs/plainlive5.sh after its cycle (cond/PLNL.stop), then start abs/plainlive6.sh (N, H, and W on the local heads)
# with PREV_N, PREV_H plainlive5's last cycle and PREV_W cond/HLW1.
cd /project/hintwork
until awk '/^HLW1 resumed/ {r=1} r && /^HLW1 done/ {f=1} END {exit !f}' cond/SWEEPQ.log; do sleep 60; done
P=$(cat cond/PLNL5.pid)
touch cond/PLNL.stop
while kill -0 $P 2>/dev/null; do sleep 15; done
rm -f cond/PLNL.stop
k=$(ls -d cond/PLNL/c[0-9]*H 2>/dev/null | grep -v '\.' | sed 's/.*\/c//; s/H$//' | sort -n | tail -1)
PREV_N=cond/PLNL/c${k}N PREV_H=cond/PLNL/c${k}H PREV_W=cond/HLW1 nohup bash abs/plainlive6.sh > cond/plainlive6.out 2>&1 &
echo $! > cond/PLNL6.pid
echo "plainlive6 started $(date '+%d %T') pid $(cat cond/PLNL6.pid) prev c${k}, W cond/HLW1" >> cond/PLNL/log

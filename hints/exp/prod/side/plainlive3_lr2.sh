#!/bin/bash
# (23 Nov) Restart abs/plainlive3.sh with MODEL=lr2 after its current cycle (cond/PLNL.stop; it ends after the cycle),
# PREV_N and PREV_L that cycle's dirs.
cd /project/hintwork
P=$(cat cond/PLNL3.pid)
touch cond/PLNL.stop
while kill -0 $P 2>/dev/null; do sleep 15; done
rm -f cond/PLNL.stop
k=$(ls -d cond/PLNL/c[0-9]*L 2>/dev/null | grep -v '\.' | sed 's/.*\/c//; s/L$//' | sort -n | tail -1)
MODEL=lr2 PREV_N=cond/PLNL/c${k}N PREV_L=cond/PLNL/c${k}L nohup bash abs/plainlive3.sh > cond/plainlive3.out 2>&1 &
echo $! > cond/PLNL3.pid
echo "plainlive3 restarted with lr2 $(date '+%d %T') pid $(cat cond/PLNL3.pid) prev c${k}" >> cond/PLNL/log

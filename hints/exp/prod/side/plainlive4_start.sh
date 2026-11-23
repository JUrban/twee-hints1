#!/bin/bash
# (23 Nov, notes/2026-11-23-plain-sizes.md) After the head sweeps (cond/SWEEPQ.log "HDG1 done"): stop abs/plainlive3.sh
# after its cycle (cond/PLNL.stop), then start abs/plainlive4.sh (N, L with lr2, and the 60 s heads setting H) with
# PREV_N and PREV_L plainlive3's last cycle and PREV_H cond/HDW1 (H's settings, so unchanged heads are not rerun).
cd /project/hintwork
until grep -q "^HDG1 done" cond/SWEEPQ.log 2>/dev/null; do sleep 30; done
P=$(cat cond/PLNL3.pid)
touch cond/PLNL.stop
while kill -0 $P 2>/dev/null; do sleep 15; done
rm -f cond/PLNL.stop
k=$(ls -d cond/PLNL/c[0-9]*L 2>/dev/null | grep -v '\.' | sed 's/.*\/c//; s/L$//' | sort -n | tail -1)
MODEL=lr2 PREV_N=cond/PLNL/c${k}N PREV_L=cond/PLNL/c${k}L PREV_H=cond/HDW1 nohup bash abs/plainlive4.sh > cond/plainlive4.out 2>&1 &
echo $! > cond/PLNL4.pid
echo "plainlive4 started $(date '+%d %T') pid $(cat cond/PLNL4.pid) prev c${k}, H cond/HDW1" >> cond/PLNL/log

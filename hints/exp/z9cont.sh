#!/bin/bash
# (23 Nov) Z9C: Z9 continued past its 8 hours to HOURS more (default 16, 24 in all), for the from-zero curve on a
# longer horizon (notes/2026-11-23-z9.md, "Continuation"). Starts 5 minutes after loops/Z9.done unless loops/Z9C.skip.
# The same loop.py command (saved from /proc at 02:47 in loops/Z9.cmd.2737443) without --init, plus
# --cascade-continue (the restarted round replays r1/results.tsv) and --cascade-hours HOURS; the transfer and
# derived-rule side loops again with their saved commands. loop.py rewrites config.json, whose mtime setcurve.py and
# abscurve.py take as the start: it is set back to Z9's start (kept in loops/Z9.t0). New rows' t= count from the
# restart again: loops/Z9.toffset ('ROW<tab>SECONDS') gives abscurve.py and latecpu.py the offset.
# Tested on sets/smoke487 (abs/rst_smoke.sh, 23 Nov 02:53-02:59): 365 -> 400 solved, no solved goal run again.
cd /project/hintwork
until [ -e loops/Z9.done ]; do sleep 30; done
echo "Z9 done seen $(date '+%d %T')" >> loops/Z9C.pids
for i in $(seq 1 10); do [ -e loops/Z9C.skip ] && { echo "Z9C skipped $(date '+%d %T')" >> loops/Z9C.pids; exit 0; }; sleep 30; done
if ps -eo args | grep -q "[l]oops/Z9 \|[l]oops/Z9.xfer\|[l]oops/Z9_GML"; then echo "a Z9 process is still running" >> loops/Z9C.pids; exit 1; fi
touch -r loops/Z9/config.json loops/Z9.t0
cp -p loops/Z9/config.json loops/Z9.config0.json
ROWS=$(wc -l < loops/Z9/r1/results.tsv); T0=$(stat -c %Y loops/Z9.t0)
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
mapfile -t A < loops/Z9.cmd.2737443
C=(); skip=0; for x in "${A[@]}"; do [ $skip = 1 ] && { skip=0; continue; }; [ "$x" = --init ] && { skip=1; continue; }; C+=("$x"); done
mapfile -t X < loops/Z9.cmd.2737562
mapfile -t G < loops/Z9.cmd.2737566
echo "starting Z9C $(date '+%d %T'): $ROWS rows, Z9 start $(date -d @$T0 '+%d %T')" >> loops/Z9C.pids
taskset -c "${CPUSET:-0-20,28-48}" "${C[@]}" --cascade-continue --cascade-hours "${HOURS:-16}" > loops/Z9.log2 2>&1 &
LOOP=$!
echo "Z9C loop $LOOP $(date +%T)" >> loops/Z9C.pids
until [ loops/Z9/config.json -nt loops/Z9.t0 ] || ! kill -0 $LOOP 2>/dev/null; do sleep 2; done
touch -r loops/Z9.t0 loops/Z9/config.json
taskset -c "${CPUSET:-0-20,28-48}" "${X[@]}" >> loops/Z9.xfer.log 2>&1 &
XFER=$!
taskset -c "${CPUSET:-0-20,28-48}" "${G[@]}" >> loops/Z9.gml.log 2>&1 &
GM=$!
echo "Z9C xfer $XFER gml $GM $(date +%T)" >> loops/Z9C.pids
# the offset: the first new row's t= against the clock when it appears (within the 5 s poll)
until [ $(wc -l < loops/Z9/r1/results.tsv) -gt $ROWS ] || ! kill -0 $LOOP 2>/dev/null; do sleep 5; done
T1=$(sed -n "$((ROWS + 1))p" loops/Z9/r1/results.tsv | tr '\t' '\n' | grep '^t=' | cut -c3-)
echo -e "$ROWS\t$(( $(date +%s) - ${T1:-0} - T0 ))" > loops/Z9.toffset
echo "offset $(cat loops/Z9.toffset) $(date +%T)" >> loops/Z9C.pids
wait $LOOP || true
desc() { for c in $(ps -o pid= --ppid $1); do desc $c; done; echo $1; }
kill $(desc $XFER) 2>/dev/null || true
kill $(desc $GM) 2>/dev/null || true
echo "Z9C done $(date '+%d %T'): $(wc -l < loops/Z9/solved.tsv) solved" | tee loops/Z9C.done >> loops/Z9C.pids

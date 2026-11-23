#!/bin/bash
# (23 Nov) Smoke test of continuing a finished from-zero run: solve_new.sh on sets/smoke487 for 0.05 h (2 workers),
# then the same loop.py command again on the same dir with --cascade-continue --cascade-hours 0.05 (no --init: the
# dir has solved.tsv). Checks for a continuation of Z9 past its 8 hours (notes/2026-11-23-z9.md).
cd /project/hintwork
[ -e loops/RST ] && { echo "loops/RST exists"; exit 1; }
sed "s|^H=.*|H=/project/twee/hints|" /project/twee/hints/solve_new.sh > loops/RST.solve_new.sh
SCHED= XEVERY=300 LOOPARGS="--knn-refresh 120" taskset -c 21-27,49-55 bash loops/RST.solve_new.sh sets/smoke487 loops/EMPTY loops/RST 2 0.05 > loops/RST.out 2>&1 &
S=$!
until P=$(ps -eo pid,args | grep "[l]oop.py sets/smoke487 loops/RST " | awk '{print $1}'); [ -n "$P" ]; do sleep 1; done
tr '\0' '\n' < /proc/$P/cmdline > loops/RST.cmd
wait $S
echo "first part done $(date +%T): $(wc -l < loops/RST/solved.tsv) solved, $(wc -l < loops/RST/r1/results.tsv) rows" >> loops/RST.pids
cp loops/RST/config.json loops/RST.config0.json; cp loops/RST.log loops/RST.log0
mapfile -t CMD < loops/RST.cmd
CMD=("${CMD[@]/--init/--init-unused}")
# drop --init and its value: init_dir skips a dir that has solved.tsv anyway, but keep the call plain
C=(); skip=0; for x in "${CMD[@]}"; do [ $skip = 1 ] && { skip=0; continue; }; [ "$x" = --init-unused ] && { skip=1; continue; }; C+=("$x"); done
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
taskset -c 21-27,49-55 "${C[@]}" --cascade-continue --cascade-hours 0.05 > loops/RST.log2 2>&1
echo "second part exit $? $(date +%T): $(wc -l < loops/RST/solved.tsv) solved, $(wc -l < loops/RST/r1/results.tsv) rows" >> loops/RST.pids

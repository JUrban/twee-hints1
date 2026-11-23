#!/bin/bash
# (23 Nov) A queue of full plain sweeps (notes/2026-11-23-conditional.md, "Sweep queue"): each line of cond/SWEEPQ.txt
# is "NAME condprove-args"; a sweep runs once (cond/NAME), on production's unsolved goals with the context
# loops/UL/solved.tsv at its start, --proved, ${J:-3} threads, then its proofs go into loops/CI3 and loops/UL.
# Waits for $AFTER (a file) first. Stops when the queue is done or cond/SWEEPQ.stop exists.
cd /project/hintwork
[ -n "$AFTER" ] && until [ -e "$AFTER" ] && grep -q "${AFTER_PAT:-.}" "$AFTER"; do sleep 30; done
while [ ! -e cond/SWEEPQ.stop ]; do
  line=$(while read n rest; do [ -n "$n" ] && [ "${n:0:1}" != "#" ] && [ ! -e cond/$n ] && { echo "$n $rest"; break; }; done < cond/SWEEPQ.txt)
  [ -z "$line" ] && break
  n=${line%% *}; args=${line#* }
  cut -f1 loops/UL/solved.tsv | sort -u > cond/$n.trusted
  echo "$n start $(date '+%d %T') context $(wc -l < cond/$n.trusted) args $args" >> cond/SWEEPQ.log
  python3 -u /project/twee/hints/exp/condprove.py cond/$n --trusted cond/$n.trusted -j ${J:-3} --proved $args > cond/$n.log 2>&1
  python3 /project/twee/hints/exp/condimport.py cond/$n loops/CI3 --trusted cond/$n.trusted > cond/$n.import 2>&1
  flock cond/merge.lock python3 /project/twee/hints/merge.py loops/UL loops/CI3 > cond/$n.merge 2>&1
  echo "$n done $(date '+%d %T') ran $(grep -c . cond/$n/results.tsv) THM $(grep -c -P '\tTHM\t' cond/$n/results.tsv) $(tail -1 cond/$n.import) | $(tail -1 cond/$n.merge)" >> cond/SWEEPQ.log
done
echo "sweepq end $(date '+%d %T')" >> cond/SWEEPQ.log

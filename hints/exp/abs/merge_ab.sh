#!/bin/bash
# Merge A/B arms (reflink copies of loops/UL taken when UL's r5/results.tsv had K rows) back into UL:
# their proofs (merge.py: solved rows + hints files) and their r5 result rows (so that the
# scheduler's history and --cascade-continue/--fresh-first see their runs).
#   bash abs/merge_ab.sh K ARM...
cd /project/hintwork
K=$1; shift
for d in "$@"; do
  n=$(tail -n +$((K+1)) loops/$d/r5/results.tsv | wc -l)
  echo "$d: $n result rows"
  tail -n +$((K+1)) loops/$d/r5/results.tsv >> loops/UL/r5/results.tsv
done
python3 /project/twee/hints/merge.py loops/UL "${@/#/loops/}" | tail -1
wc -l loops/UL/solved.tsv loops/UL/r5/results.tsv

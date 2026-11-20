#!/bin/bash
# (20 Nov 12:37) The model audit every EVERY seconds (default 21600, 6 hours; notes/2026-11-20-model-audit.md):
# exp/modelcheck.py over production's proofs into loops/AUDIT/<stamp> (the Mace4 models are reused from
# loops/MODELCHECK/models). An ALARM line in loops/AUDIT.log means a false step with the same variables on both
# sides: look at OUTDIR/alarm.tsv.
#   auditlive.sh [EVERY] [FIRST-DELAY]
EVERY=${1:-21600}
cd /project/hintwork || exit 1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
[ -n "$2" ] && sleep "$2"
while :; do
  D=loops/AUDIT/$(date +%d%H%M)
  mkdir -p $D
  [ -e $D/models ] || ln -s /project/hintwork/loops/MODELCHECK/models $D/models
  echo "audit $(date +%T) -> $D"
  python3 /project/twee/hints/exp/modelcheck.py $D -j 3 > $D/log 2>&1
  grep '^modelcheck:\|^ALARM' $D/log
  sleep "$EVERY"
done

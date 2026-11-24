#!/bin/bash
# (23 Nov 23:49) exp74: long plain runs on the first heads of the key-goal cluster (notes/2026-11-23-climber-restart.md,
# "exp74"). exp69/exp70: 9 key goals of 7 originals each follow from another unsolved goal of the cluster in a 5 s
# sketch, and their gaps do not fill (3 s fills 40-42%, 30 s 39%). The way in is each original's first unsolved goal,
# all its earlier goals proved (sets/clusterheads74, exp/sets/clusterheads74). Production gave them at most its 320 s
# cascade (single runs 60-141 s). Plain runs (no hints, no model, no PG) with 100+30 siblings and 400 kNN lemmas are
# the plain live loop's best tail setting (H, 60 s); here 1200 abstract s, 2 threads. Proofs via condimport.py into
# loops/CI3 and merge.py into loops/UL.
# (24 Nov 00:19) rerun: the first run (cond/LCH74.v1) stopped every goal at condprove.py's flat 600 s wall cap (TIMEOUT rows);
# condprove.py now caps at 10 x --time.
cd /project/hintwork
N=LCH74
[ -e cond/$N ] && { echo "cond/$N exists"; exit 1; }
cut -f1 loops/UL/solved.tsv | sort -u > cond/$N.trusted
echo "$N start $(date '+%d %T') context $(wc -l < cond/$N.trusted)" > cond/$N.status
python3 -u /project/twee/hints/exp/condprove.py cond/$N --trusted cond/$N.trusted -j ${J:-2} --proved --time 1200 \
  --sibs 100 --after 30 --knn 400 --only sets/clusterheads74 > cond/$N.log 2>&1
python3 /project/twee/hints/exp/condimport.py cond/$N loops/CI3 --trusted cond/$N.trusted --time 1200 > cond/$N.import 2>&1
flock cond/merge.lock python3 /project/twee/hints/merge.py loops/UL loops/CI3 > cond/$N.merge 2>&1
echo "$N done $(date '+%d %T') ran $(grep -c . cond/$N/results.tsv) THM $(grep -c -P '\tTHM\t' cond/$N/results.tsv) $(tail -1 cond/$N.import) | $(tail -1 cond/$N.merge)" >> cond/$N.status

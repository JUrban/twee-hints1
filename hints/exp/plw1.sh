#!/bin/bash
# (23 Nov) PLW1: a wide plain sweep beside the plain live loop (notes/2026-11-23-conditional.md, "Wide plain sweep"):
# production's unsolved goals with 100 earlier and 30 later trusted siblings and 400 kNN lemmas, plain 5 s twee,
# 3 threads, the context production's solved list at its start; then its proofs into loops/CI3 and loops/UL.
# Starts when PLN2 has ended.
cd /project/hintwork
until grep -q "PLN2 done" cond/PLN2.pids 2>/dev/null; do sleep 30; done
[ -e cond/PLW1 ] && { echo "cond/PLW1 exists"; exit 1; }
cut -f1 loops/UL/solved.tsv | sort -u > cond/PLW1.trusted
echo "PLW1 start $(date '+%d %T') context $(wc -l < cond/PLW1.trusted)" > cond/PLW1.pids
python3 -u /project/twee/hints/exp/condprove.py cond/PLW1 --trusted cond/PLW1.trusted -j 3 --time 5 \
  --sibs 100 --after 30 --knn 400 --proved > cond/PLW1.log 2>&1
echo "PLW1 done $(date '+%d %T') exit $?" >> cond/PLW1.pids
python3 /project/twee/hints/exp/condimport.py cond/PLW1 loops/CI3 --trusted cond/PLW1.trusted > cond/PLW1.import 2>&1
python3 /project/twee/hints/merge.py loops/UL loops/CI3 > cond/PLW1.merge 2>&1
echo "PLW1 imported $(date '+%d %T'): $(tail -1 cond/PLW1.import) | $(tail -1 cond/PLW1.merge)" >> cond/PLW1.pids

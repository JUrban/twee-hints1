#!/bin/bash
# exp82 (24 Nov): Horn sibling lemmas (notes/2026-11-24-horn-lemmas.md). 2,771 proved goals are genuine Horn clauses
# (no unit form); lemma import has always dropped them. Arm H82H: TWEE_LEMMA_HORN=1, the Horn siblings of the same
# window as clause axioms on top of the unit ones (twee's ifeq encoding); H82C: the same problems without them. Plain
# 60 s runs as HLW1 (100+30 siblings, 400 kNN), one thread each, on cond/EXP82.set: 60 unsolved local heads with at least
# 2 proved Horn siblings in their window, not in exp81's set (seed 82). Same context snapshot for both.
cd /project/hintwork
cut -f1 loops/UL/solved.tsv | sort -u > cond/EXP82.trusted
echo "exp82 start $(date '+%d %T') context $(wc -l < cond/EXP82.trusted) set $(wc -l < cond/EXP82.set)" >> cond/EXP82.status
arm() {   # NAME HORN
  n=$1
  TWEE_LEMMA_HORN=$2 python3 -u /project/twee/hints/exp/condprove.py cond/$n --trusted cond/EXP82.trusted -j 1 --proved --time 60 \
    --sibs 100 --after 30 --knn 400 --only cond/EXP82.set > cond/$n.log 2>&1
  python3 /project/twee/hints/exp/condimport.py cond/$n loops/CI3 --trusted cond/EXP82.trusted --time 60 > cond/$n.import 2>&1
  flock cond/merge.lock python3 /project/twee/hints/merge.py loops/UL loops/CI3 > cond/$n.merge 2>&1
  echo "$n done $(date '+%d %T') ran $(grep -c . cond/$n/results.tsv) THM $(grep -c -P '\tTHM\t' cond/$n/results.tsv) | $(tail -1 cond/$n.import) | $(tail -1 cond/$n.merge)" >> cond/EXP82.status
}
arm H82H 1 &
arm H82C 0 &
wait
echo "exp82 done $(date '+%d %T')" >> cond/EXP82.status

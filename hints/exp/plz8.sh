#!/bin/bash
# (23 Nov) PLZ8 (notes/2026-11-23-conditional.md, "From zero: PLZ8"): plain runs as in PLN1 (30 earlier and 10 later
# siblings, 100 kNN lemmas, 5 s, no model, no hints) on 2,000 of Z8's 8,864 unsolved goals (sets/z8un2000, seed 88)
# in Z8's final 6-hour context (sets/z8f.solved = loops/Z8F.ctx/solved.tsv's goals, as the "trusted" list). Against
# Z8's own late 5 s retries (81 proofs per CPU h in hours 4-6). Starts after PLN1; 4 threads; cond/PLZ8.
cd /project/hintwork
until grep -q "PLN1 done" cond/PLN1.pids 2>/dev/null; do sleep 30; done
[ -e cond/PLZ8 ] && { echo "cond/PLZ8 exists"; exit 1; }
echo "PLZ8 start $(date '+%d %T')" > cond/PLZ8.pids
python3 -u /project/twee/hints/exp/condprove.py cond/PLZ8 --trusted sets/z8f.solved --only sets/z8un2000 -j 4 --time 5 \
  --sibs 30 --after 10 --knn 100 --proved > cond/PLZ8.log 2>&1
echo "PLZ8 done $(date '+%d %T') exit $?" >> cond/PLZ8.pids

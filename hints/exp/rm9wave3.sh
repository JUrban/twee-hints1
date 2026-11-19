#!/bin/bash
# (19 Nov 20:58) exp37's queue after rm9b (notes/2026-11-19-retrained-models.md): rm9b (the 3 shortest proofs per goal
# over every loop, 32 negatives per log) got AUC 0.740 on the 400 held-out goals, against rm9a 0.876 and rm4t 0.835.
# The many easy, short proofs hurt. So rm9d (the same data with Suda's weighting) was stopped at its start, and the
# queue is: the long-proof selections first, then the weighting and tree-size tests on rm9a's data.
# One at a time on 4 workers, rm9a's vocab frozen; each followed by its paired arm on 1 worker (abs/mabrm.sh).
cd /project/hintwork
V="--jobs 4 --vocab-from models/rm9a.vocab"
run() {   # model, args
  TH=4 M=$1 ARGS="$2 $V" bash abs/rm9.sh
  [ -f models/$1.bin ] && (M=$1 T=20 J=1 nohup bash abs/mabrm.sh > /dev/null 2>&1 &)
}
B="given/train_only,given/tr30_g1,loops/UL/given --negmax 150"
run rm9e "loops/UL/given --list models/list_long2.tsv --negmax 16 --leaves 255 --min-data 50"
run rm9c "loops/UL/given --list models/list_slm.tsv --negmax 16 --long-exp 0.5 --leaves 255 --min-data 50"
run rm9f "$B --weighting log"
run rm9g "$B --leaves 255 --min-data 50"
echo "wave3 done $(date +%T)" > models/rm9wave3.done

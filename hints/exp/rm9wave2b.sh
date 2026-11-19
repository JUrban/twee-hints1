#!/bin/bash
# (19 Nov 20:23) exp37's second wave, revised from abs/rm9wave2.sh (stopped before it trained anything): rm9a took
# 21.5 GB for about 5 M rows (the theory and goal blocks are about 170 of the 200 nonzeros per row), so every
# multi-proof model is kept at 7 M rows or fewer: fewer negatives per log, and the 2 longest proofs instead of 3.
# One at a time on 4 workers, rm9a's vocab frozen; each followed by its paired arm on 1 worker (abs/mabrm.sh).
# notes/2026-11-19-retrained-models.md
cd /project/hintwork
until [ -f models/rm9a.done ]; do sleep 30; done
(M=rm9a T=20 J=1 nohup bash abs/mabrm.sh > /dev/null 2>&1 &)
V="--jobs 4 --vocab-from models/rm9a.vocab"
run() {   # model, args
  TH=4 M=$1 ARGS="loops/UL/given $2 $V" bash abs/rm9.sh
  [ -f models/$1.bin ] && (M=$1 T=20 J=1 nohup bash abs/mabrm.sh > /dev/null 2>&1 &)
}
run rm9b "--list models/list_short3.tsv --negmax 32"
run rm9d "--list models/list_short3.tsv --negmax 32 --weighting log"
run rm9c "--list models/list_slm.tsv --negmax 16 --long-exp 0.5 --leaves 255 --min-data 50"
run rm9e "--list models/list_long2.tsv --negmax 16 --leaves 255 --min-data 50"
echo "wave2 done $(date +%T)" > models/rm9wave2.done

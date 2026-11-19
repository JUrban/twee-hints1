#!/bin/bash
# (19 Nov 20:11) exp37's second wave (notes/2026-11-19-retrained-models.md): after rm9a, its paired arm; then, one at a
# time on 4 workers (rm9a's vocab frozen), the multi-proof models over every loop's logs (models/given_index.tsv,
# givensel.py, the 400 test goals excluded), each followed by its paired arm on 1 worker (abs/mabrm.sh).
cd /project/hintwork
until [ -f models/rm9a.done ]; do sleep 30; done
(M=rm9a T=20 J=1 nohup bash abs/mabrm.sh > /dev/null 2>&1 &)
V="--jobs 4 --vocab-from models/rm9a.vocab"
run() {   # model, args
  TH=4 M=$1 ARGS="loops/UL/given $2 $V" bash abs/rm9.sh
  [ -f models/$1.bin ] && (M=$1 T=20 J=1 nohup bash abs/mabrm.sh > /dev/null 2>&1 &)
}
run rm9b "--list models/list_short3.tsv --negmax 64"
run rm9d "--list models/list_short3.tsv --negmax 64 --weighting log"
run rm9c "--list models/list_slm.tsv --negmax 32 --negratio 1 --long-exp 0.5 --leaves 255 --min-data 50"
run rm9e "--list models/list_long3.tsv --negmax 64 --leaves 255 --min-data 50"
echo "wave2 done $(date +%T)" > models/rm9wave2.done

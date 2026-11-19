#!/bin/bash
# (19 Nov 22:14) exp37's fourth wave (notes/2026-11-19-retrained-models.md): Suda's per-log weighting was the best change
# offline (rm9f 0.892, rm9a 0.876 on the same rows), so it is combined with the other two levers: rm9h = the 2
# longest proofs per goal over every loop (rm9e's data, 0.854 unweighted) with the weighting; rm9i = rm9a's data with
# the weighting and 255 leaves. After abs/rm9wave3.sh; one at a time on 4 workers, each followed by its paired arm.
cd /project/hintwork
until [ -f models/rm9wave3.done ]; do sleep 30; done
V="--jobs 4 --vocab-from models/rm9a.vocab"
run() {   # model, args
  TH=4 M=$1 ARGS="$2 $V" bash abs/rm9.sh
  [ -f models/$1.bin ] && (M=$1 T=20 J=1 nohup bash abs/mabrm.sh > /dev/null 2>&1 &)
}
run rm9h "loops/UL/given --list models/list_long2.tsv --negmax 16 --leaves 255 --min-data 50 --weighting log"
run rm9i "given/train_only,given/tr30_g1,loops/UL/given --negmax 150 --weighting log --leaves 255 --min-data 50"
echo "wave4 done $(date +%T)" > models/rm9wave4.done

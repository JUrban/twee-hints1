#!/bin/bash
# (22 Nov 16:47) exp63 (notes/2026-11-22-frontier-orderings.md): production's unsolved unit goals (sets/ulu120, seed 63)
# in its context at 16:47 (loops/ULF.ctx), one fresh 20 abstract s run each, production's core options, two arms at once:
# loops/OD (twee's default KBO precedence) and loops/OO1 (ordering 1: --p9-orders 4 --p9-order-offset 1).
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
cd /project/hintwork
for a in OD OO1; do [ -e loops/$a ] && { echo "loops/$a exists"; exit 1; }; done
echo "start $(date '+%d %T')" > loops/ORD.pids
for arm in OD: "OO1:--p9-orders 4 --p9-order-offset 1"; do
  A=${arm%%:*}; X=${arm#*:}
  python3 -u /project/twee/hints/loop.py sets/ulu120 loops/$A --init loops/ULF.ctx --start 1 --rounds 1 --keep-out -j 1 \
    --pool original --wall-factor 15 $X \
    --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
    --lemmas 6 --lemma-knn 30 --lemma-subsets --lemma-after --twee /project/bin/twee-pg61 --timeout 20 \
    --args="--abstract-time 2000 --no-resume-requeue --no-eqhint-consider" > loops/$A.log 2>&1 &
  echo "$A $! $X" >> loops/ORD.pids
done
wait
echo "done $(date '+%d %T') OD $(grep -c THM loops/OD/r1/results.tsv) OO1 $(grep -c THM loops/OO1/r1/results.tsv)" >> loops/ORD.pids

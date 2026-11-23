#!/bin/bash
# (20 Nov 03:42) exp38 live (notes/2026-11-20-given-transfer.md): givenmatch.py live beside production. Every 20 min it
# scans the given logs of loops/UL and loops/XFL written since the last cycle against production's unsolved unit
# goals (variants; instances within the own original). New hits run as in exp38: ancestry at 20 s, then the log
# prefix with its axioms at 40 s. Proofs go into production. The first watermark is the newest log in
# models/given_index.tsv (19 Nov 19:51), so the first cycle covers the 783 logs written since.
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
cd /project/hintwork
mkdir -p loops/GML
[ -f loops/GML/watermark ] || echo 1795117899 > loops/GML/watermark
python3 -u /project/twee/hints/givenmatch.py live loops/GML --dirs UL,XFL --every 1200 -j 2 -- \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab \
  --model-theory --lemmas 6 --lemma-knn 30 --lemma-subsets --lemma-after --pool original --twee /project/bin/twee-pg61 \
  --wall-factor 15 --args="--abstract-time 2000 --no-eqhint-consider" > loops/GML.log 2>&1

#!/bin/bash
# (22 Nov 12:02) gmlive3: gmlive2k.sh plus --retry-tried 3 and (12:06) --lemma-ax (exp56, notes/2026-11-22-gm-retry.md): a tried goal runs again on the
# hits that came after its last try, at most once every 3 hours, newest hits first (GMR: 5 of the 30 given-up goals
# proved by the prefix pass on their newest hits). Log loops/GML3.log.
# (20 Nov 10:35) gmlive2.sh / xfrlive2.sh with --keep-out: kept outputs (USEDAXIOMS) are the lemma records exp/trust.py needs (notes/2026-11-20-p9-negation-bug.md)
# (20 Nov 04:32) gmlive2: gmlive.sh every 5 minutes instead of 20 (as the transfer loop): its first cycles proved 9 of 14,
# 5 of 5 from production's failed-run hits (loop.py --given-scan) at 04:30. Each cycle also runs the same-statement finder.
# (20 Nov 03:42) exp38 live (notes/2026-11-20-given-transfer.md): givenmatch.py live beside production. Every 20 min it
# scans the given logs of loops/UL and loops/XFL written since the last cycle against production's unsolved unit
# goals (variants; instances within the own original). New hits run as in exp38: ancestry at 20 s, then the log
# prefix with its axioms at 40 s. Proofs go into production. The first watermark is the newest log in
# models/given_index.tsv (19 Nov 19:51), so the first cycle covers the 783 logs written since.
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
cd /project/hintwork
mkdir -p loops/GML
[ -f loops/GML/watermark ] || echo 1795117899 > loops/GML/watermark
python3 -u /project/twee/hints/givenmatch.py live loops/GML --dirs UL,XFL --every 300 -j 2 --retry-tried 3 --lemma-ax -- \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab \
  --model-theory --lemmas 6 --lemma-knn 30 --lemma-subsets --lemma-after --pool original --twee /project/bin/twee-pg61 \
  --wall-factor 15 --keep-out --args="--abstract-time 2000 --no-eqhint-consider" > loops/GML3.log 2>&1

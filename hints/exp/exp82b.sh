#!/bin/bash
# (24 Nov 08:10) exp82b: arm H82F replaces H82H (notes/2026-11-24-horn-lemmas.md, "Encoding"). With twee's default Horn
# encoding (Jukebox --conditional-encoding if-then-else) the Horn lemma problems cost 8 times the CPU per abstract second
# (aa3_45 486: 91 against 11.6 CPU s for 10 abstract s) and H82H's first 2 runs hit condprove's 600 s wall limit; it was
# stopped at 07:53. `--conditional-encoding fresh` costs what the problem without Horn axioms does (9.8 CPU s) and proves
# aa3_45 486 in 29.8 CPU s (the control 42.5); without Horn axioms it changes nothing (byte-identical outputs, with and
# without a Horn goal). H82F: TWEE_LEMMA_HORN=1 with that flag, for the runs and condimport's reruns; the same set, snapshot
# cond/EXP82.trusted and settings as the control H82C (still running in abs/exp82.sh), one thread.
cd /project/hintwork
n=H82F
echo "$n start $(date '+%d %T')" >> cond/EXP82.status
TWEE_LEMMA_HORN=1 python3 -u /project/twee/hints/exp/condprove.py cond/$n --trusted cond/EXP82.trusted -j 1 --proved --time 60 \
  --sibs 100 --after 30 --knn 400 --only cond/EXP82.set --args "--conditional-encoding fresh" > cond/$n.log 2>&1
python3 /project/twee/hints/exp/condimport.py cond/$n loops/CI3 --trusted cond/EXP82.trusted --time 60 --args "--conditional-encoding fresh" > cond/$n.import 2>&1
flock cond/merge.lock python3 /project/twee/hints/merge.py loops/UL loops/CI3 > cond/$n.merge 2>&1
echo "$n done $(date '+%d %T') ran $(grep -c . cond/$n/results.tsv) THM $(grep -c -P '\tTHM\t' cond/$n/results.tsv) | $(tail -1 cond/$n.import) | $(tail -1 cond/$n.merge)" >> cond/EXP82.status

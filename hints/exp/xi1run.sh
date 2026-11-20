#!/bin/bash
# (20 Nov 03:47) transfer.py find --instances (unit-goal proof steps; last run 16 Nov) on production now: 11 candidates, the 2
# not tried by the transfer loop or exp38, 20 s; notes/2026-11-20-given-transfer.md.
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
cd /project/hintwork
D=loops/XI1run
mkdir -p $D
[ -e $D/hints ] || ln -s /project/hintwork/loops/UL/hints $D/hints
awk -F'\t' 'NF>=3 {print $1 "\t0\t" $3}' loops/UL/solved.tsv > $D/solved.tsv
python3 -u /project/twee/hints/transfer.py run loops/XI1/goals.tsv $D -j ${J:-2} --time ${TIME:-20} --src-lemmas 6 \
  --live-dst loops/UL -- --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab \
  --model-theory --lemmas 6 --lemma-knn 30 --lemma-subsets --lemma-after --pool original --twee /project/bin/twee-pg61 \
  --wall-factor 15 --args="--abstract-time 2000 --no-eqhint-consider" > loops/XI1run.log 2>&1
echo "XI1run $(tail -1 loops/XI1run.log) $(date +%T)" | tee loops/XI1run.done

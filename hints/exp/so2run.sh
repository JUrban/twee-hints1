#!/bin/bash
# (20 Nov 04:18) REPORT 2ar redone on production now (exp/sofree.py): unsolved goals that are proven goals of originals
# with more axioms, whose first source proof has none of the missing axioms as a step, minus the 16 Nov tries: 46.
# Source proof steps first as hints, 20 s (as 16 Nov's SOF/SOR); proofs into production.
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
cd /project/hintwork
D=loops/SO2run
mkdir -p $D
[ -e $D/hints ] || ln -s /project/hintwork/loops/UL/hints $D/hints
awk -F'\t' 'NF>=3 {print $1 "\t0\t" $3}' loops/UL/solved.tsv > $D/solved.tsv
python3 -u /project/twee/hints/transfer.py run loops/SO2/goals.tsv $D -j ${J:-2} --time ${TIME:-20} --src-lemmas 6 \
  --live-dst loops/UL -- --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab \
  --model-theory --lemmas 6 --lemma-knn 30 --lemma-subsets --lemma-after --pool original --twee /project/bin/twee-pg61 \
  --wall-factor 15 --args="--abstract-time 2000 --no-eqhint-consider" > loops/SO2run.log 2>&1
echo "SO2run $(tail -1 loops/SO2run.log) $(date +%T)" | tee loops/SO2run.done

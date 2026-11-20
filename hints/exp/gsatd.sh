#!/bin/bash
# (20 Nov 06:35) exp39: the base pilot's direct proofs (loops/GSAT/direct.tsv) through transfer.py run into production.
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
cd /project/hintwork
D=loops/GSATdrun
mkdir -p $D
[ -e $D/hints ] || ln -s /project/hintwork/loops/UL/hints $D/hints
awk -F'\t' 'NF>=3 {print $1 "\t0\t" $3}' loops/UL/solved.tsv > $D/solved.tsv
python3 -u /project/twee/hints/transfer.py run loops/GSATd/goals.tsv $D -j ${J:-2} --time ${TIME:-20} --src-lemmas 6 \
  --live-dst loops/UL -- --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab \
  --model-theory --lemmas 6 --lemma-knn 30 --lemma-subsets --lemma-after --pool original --twee /project/bin/twee-pg61 \
  --wall-factor 15 --args="--abstract-time 2000 --no-eqhint-consider" > loops/GSATdrun.log 2>&1
echo "GSATdrun $(tail -1 loops/GSATdrun.log) $(date +%T)" | tee loops/GSATdrun.done

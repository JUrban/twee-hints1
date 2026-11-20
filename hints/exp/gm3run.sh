#!/bin/bash
# (20 Nov 03:18) exp38b (notes/2026-11-20-given-transfer.md): 40 seeded unsolved goals, each with the newest production
# given log of its original as lemma axioms (every rule of that run; exp/gm3prep.py) and its proof steps as hints,
# 20 s. Otherwise as gm1run.sh: transfer.py run, production's binary and PG, proofs into production.
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
cd /project/hintwork
D=loops/GM3run
mkdir -p $D
[ -e $D/hints ] || ln -s /project/hintwork/loops/UL/hints $D/hints
awk -F'\t' 'NF>=3 {print $1 "\t0\t" $3}' loops/UL/solved.tsv > $D/solved.tsv
python3 -u /project/twee/hints/transfer.py run loops/GM3/goals.tsv $D -j ${J:-1} --time ${TIME:-20} --src-lemmas 6 \
  --live-dst loops/UL -- --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab \
  --model-theory --lemmas 6 --lemma-knn 30 --lemma-subsets --lemma-after --pool original --twee /project/bin/twee-pg61 \
  --wall-factor 15 --args="--abstract-time 2000 --no-eqhint-consider" > loops/GM3run.log 2>&1
echo "GM3run $(tail -1 loops/GM3run.log) $(date +%T)" | tee loops/GM3run.done

#!/bin/bash
# (20 Nov 02:22) exp38 (notes/2026-11-20-given-transfer.md): one run per unsolved goal that is a variant of a rule
# derived in another run's given log. The rule's ancestry goes first as hints (givenmatch.py sketch), then the pool.
# transfer.py run with the transfer loop's options, but production's binary and PG. Proofs go into production
# (--live-dst loops/UL), as the transfer loop's do. Context: production's solved list now, as transfer.py live
# sets it up.
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
cd /project/hintwork
D=loops/GM1run
mkdir -p $D
[ -e $D/hints ] || ln -s /project/hintwork/loops/UL/hints $D/hints
awk -F'\t' 'NF>=3 {print $1 "\t0\t" $3}' loops/UL/solved.tsv > $D/solved.tsv
python3 /project/twee/hints/givenmatch.py sketch loops/GM1/hits.tsv loops/GM1/sketch loops/GM1/goals.tsv --per 3
python3 -u /project/twee/hints/transfer.py run loops/GM1/goals.tsv $D -j ${J:-2} --time ${TIME:-20} --src-lemmas 6 \
  --live-dst loops/UL -- --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab \
  --model-theory --lemmas 6 --lemma-knn 30 --lemma-subsets --lemma-after --pool original --twee /project/bin/twee-pg61 \
  --wall-factor 15 --args="--abstract-time 2000 --no-eqhint-consider" > loops/GM1run.log 2>&1
echo "GM1run $(tail -1 loops/GM1run.log) $(date +%T)" | tee loops/GM1run.done

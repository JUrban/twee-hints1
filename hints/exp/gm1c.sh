#!/bin/bash
# (20 Nov 03:11) exp38, third pass: the goals still unsolved after gm1b.sh, with the source log's whole prefix up to the
# matched rule as hints (givenmatch.py sketch --prefix; the log's parents miss the rewriting steps) and the prefix's
# axioms as lemma axioms, 40 s.
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
cd /project/hintwork
D=loops/GM1c
mkdir -p $D
[ -e $D/hints ] || ln -s /project/hintwork/loops/UL/hints $D/hints
awk -F'\t' 'NF>=3 {print $1 "\t0\t" $3}' loops/UL/solved.tsv > $D/solved.tsv
python3 /project/twee/hints/givenmatch.py sketch loops/GM1/hits.tsv loops/GM1/sketchp loops/GM1/goalsp.tsv --per 3 --prefix
awk -F'\t' 'NR==FNR {if ($2=="NO") f[$1]=1; next} f[$1]' loops/GM1b/transfer.tsv loops/GM1/goalsp.tsv > loops/GM1/goals_c.tsv
python3 -u /project/twee/hints/transfer.py run loops/GM1/goals_c.tsv $D -j ${J:-2} --time ${TIME:-40} --src-lemmas 6 \
  --live-dst loops/UL -- --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab \
  --model-theory --lemmas 6 --lemma-knn 30 --lemma-subsets --lemma-after --pool original --twee /project/bin/twee-pg61 \
  --wall-factor 15 --args="--abstract-time 2000 --no-eqhint-consider" > loops/GM1c.log 2>&1
echo "GM1c $(tail -1 loops/GM1c.log) $(date +%T)" | tee loops/GM1c.done

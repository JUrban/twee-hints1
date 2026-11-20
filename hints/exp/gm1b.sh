#!/bin/bash
# (20 Nov 03:05) exp38, second pass: the goals that failed gm1run.sh (8 of 19 proved at 20 s), again at 40 s, now with
# the source run's axioms behind each sketch as lemma axioms (the .ax files; transfer.py run adds them).
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
cd /project/hintwork
D=loops/GM1b
mkdir -p $D
[ -e $D/hints ] || ln -s /project/hintwork/loops/UL/hints $D/hints
awk -F'\t' 'NF>=3 {print $1 "\t0\t" $3}' loops/UL/solved.tsv > $D/solved.tsv
python3 /project/twee/hints/givenmatch.py sketch loops/GM1/hits.tsv loops/GM1/sketch loops/GM1/goals.tsv --per 3
awk -F'\t' 'NR==FNR {if ($2=="NO") f[$1]=1; next} f[$1]' loops/GM1run/transfer.tsv loops/GM1/goals.tsv > loops/GM1/goals_b.tsv
python3 -u /project/twee/hints/transfer.py run loops/GM1/goals_b.tsv $D -j ${J:-2} --time ${TIME:-40} --src-lemmas 6 \
  --live-dst loops/UL -- --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab \
  --model-theory --lemmas 6 --lemma-knn 30 --lemma-subsets --lemma-after --pool original --twee /project/bin/twee-pg61 \
  --wall-factor 15 --args="--abstract-time 2000 --no-eqhint-consider" > loops/GM1b.log 2>&1
echo "GM1b $(tail -1 loops/GM1b.log) $(date +%T)" | tee loops/GM1b.done

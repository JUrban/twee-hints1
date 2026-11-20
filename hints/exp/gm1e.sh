#!/bin/bash
# (20 Nov 04:10) exp38, fifth pass: the 8 variant hits still open, with the ancestry fixed (givenmatch.py read the given
# log's parents as positions; they are rule numbers, position + 1) and the source run's axioms in it, 40 s, in the
# target's usual context (as gm1b.sh).
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
cd /project/hintwork
D=loops/GM1erun
mkdir -p $D
[ -e $D/hints ] || ln -s /project/hintwork/loops/UL/hints $D/hints
awk -F'\t' 'NF>=3 {print $1 "\t0\t" $3}' loops/UL/solved.tsv > $D/solved.tsv
python3 /project/twee/hints/givenmatch.py sketch loops/GM1e/hits_all.tsv loops/GM1e/sketch loops/GM1e/goals_all.tsv --per 3
awk -F'\t' 'NR==FNR {s[$1]=1; next} !($1 in s)' loops/UL/solved.tsv loops/GM1e/goals_all.tsv > loops/GM1e/goals.tsv
python3 -u /project/twee/hints/transfer.py run loops/GM1e/goals.tsv $D -j ${J:-2} --time ${TIME:-40} --src-lemmas 6 \
  --live-dst loops/UL -- --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab \
  --model-theory --lemmas 6 --lemma-knn 30 --lemma-subsets --lemma-after --pool original --twee /project/bin/twee-pg61 \
  --wall-factor 15 --args="--abstract-time 2000 --no-eqhint-consider" > loops/GM1e.log 2>&1
echo "GM1e $(tail -1 loops/GM1e.log) $(date +%T)" | tee loops/GM1e.done

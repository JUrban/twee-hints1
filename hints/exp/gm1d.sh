#!/bin/bash
# (20 Nov 03:51) exp38, fourth pass (notes/2026-11-20-given-transfer.md): the 8 variant hits still open after three passes
# (6 of exp38's 19, 2 of the live loop's cycle 1), replayed as close to the source run as transfer.py run allows: the
# source run's axioms up to the matched rule as the only lemma axioms (.ax), the log's prefix as the only hints
# (--max-hints 0: no pool), no target lemmas, no rule model, no PG, 80 s.
cd /project/hintwork
D=loops/GM1drun
mkdir -p $D
[ -e $D/hints ] || ln -s /project/hintwork/loops/UL/hints $D/hints
awk -F'\t' 'NF>=3 {print $1 "\t0\t" $3}' loops/UL/solved.tsv > $D/solved.tsv
python3 -u /project/twee/hints/transfer.py run loops/GM1d/goals.tsv $D -j ${J:-2} --time ${TIME:-80} --src-lemmas 0 \
  --live-dst loops/UL -- --pool original --max-hints 0 --twee /project/bin/twee-pg61 \
  --wall-factor 15 --args="--abstract-time 2000 --no-eqhint-consider" > loops/GM1d.log 2>&1
echo "GM1d $(tail -1 loops/GM1d.log) $(date +%T)" | tee loops/GM1d.done

#!/bin/bash
# exp1/run.sh ARM... (17 Nov 19:05): re-prove 200 random lemma-based production proofs (exp1/s200, seed 1, from
# UL's recorded proofs with mapped lemmas) from the axioms alone, no lemma axioms. Production's twee settings:
# twee-e48, rm4t, PG 0.25, 20 abstract s. Arms by hints:
#   N none; O the goal's own (lemma-based) proof steps; X the expansion (expand.py: own steps + the steps of
#   every lemma used, recursively); P the original's whole pool as production gives it (exp1/mkpool.py).
cd /project/hintwork
T=${T:-20}; J=${J:-6}
A="--abstract-time 2000 --no-resume-requeue --no-eqhint-consider --pg-threshold 0.25 --max-cpu $((T*10)) --print-hints --rule-model /project/hintwork/models/rm4t.bin --rule-vocab /project/hintwork/models/rm4t.vocab --rule-threshold 0.1 --rule-penalty 2"
for v in "$@"; do
  case $v in
    N) H="" ;;
    O) H="--hints-dir loops/UL/hints" ;;
    X) H="--hints-dir exp1/xh" ;;
    P) H="--hints-dir exp1/ph" ;;
  esac
  python3 /project/twee/hints/run.py exp1/s200 exp1/r_${v}_$T --twee /project/bin/twee-e48 --timeout $T --wall-factor 15 -j $J \
    --keep-all --args="$A" --per rule-goal:exp1/goals $H > exp1/r_${v}_$T.log 2>&1
  echo "$v T=$T: $(awk -F'\t' '$2=="THM"' exp1/r_${v}_$T/results.tsv | wc -l) proved, CPs $(awk -F'\t' '{split($4,w,"[= ]"); s+=w[2]} END{print s}' exp1/r_${v}_$T/results.tsv)"
done

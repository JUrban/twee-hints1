#!/bin/bash
# (24 Nov) revf2.sh TRUSTRUN DIR: revf.sh with the run's time, sibling and kNN lemma counts settable (TIME, LEM, KNN; revf.sh's
# 60, 6, 30 by default). For aK2_eq_aK3_s 489, 494, 515 (untrusted since 23 Nov: fill lemma m(X,k(X2,X3)) = rd(X,k(X3,X2)) is
# recorded only through 494, whose proof uses 515), with the climber's lemma lists and final time
# (notes/2026-11-24-quick-finals.md, "Untrusted aK2_eq_aK3_s").
cd /project/hintwork
TP=${1:?}; D=${2:?}
[ -e $D ] && { echo "$D exists"; exit 1; }
mkdir -p $D; ln -s /project/hintwork/loops/UL/hints $D/hints
python3 - $TP $D <<'PY'
import sys
tp, d = sys.argv[1:3]
tr = {l.strip() for l in open(tp + '.trusted') if l.strip()}
roots = [l.strip() for l in open(tp + '.roots') if l.strip()]
with open(f'{d}/solved.tsv', 'w') as f:
    for l in open('/project/hintwork/loops/UL/solved.tsv'):
        if l.split('\t')[0] in tr:
            f.write(l)
with open(f'{d}/goals.tsv', 'w') as f:
    for g in roots:
        f.write(f'{g}\t/project/hintwork/loops/UL/hints/{g}\t0\n')
print(d, len(tr), 'trusted', len(roots), 'roots')
PY
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100" OMP_NUM_THREADS=1
python3 /project/twee/hints/transfer.py run $D/goals.tsv $D -j ${J:-1} --time ${TIME:-60} --src-lemmas 0 --live-dst loops/UL -- \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas ${LEM:-6} --lemma-knn ${KNN:-30} --lemma-subsets --lemma-after --pool original --twee /project/bin/twee-pg61 --wall-factor 15 \
  --keep-out "--args=--abstract-time 2000 --no-eqhint-consider" > $D/run.log 2>&1
echo "revf done $(date '+%d %T'): $(grep -c -P '\tTHM\t' $D/transfer.tsv 2>/dev/null) of $(wc -l < $D/goals.tsv) proved" | tee -a $D/run.log

#!/bin/bash
# (23 Nov 21:30) revf.sh TRUSTRUN DIR: re-prove a trust run's roots (production's proofs that exp/trust.py leaves untrusted
# for want of a resolvable record) with trusted lemmas only: one pass of exp/rever2.py's recipe. Today the roots are
# production proofs that used climber fill lemmas (lemma_fill_N, member sk@1:0 with --climb-hints): fill lemmas are
# proved from the original's axioms and proven lemmas only, but their premises are not recorded, so trust.py cannot
# check them. The rerun: rever2's options (no --climb-hints, so no fill lemmas), the goal's own last proof as its hints
# (DIR/hints is production's), the context = TRUSTRUN's trusted goals, 60 s, -j ${J:-1}; a proof replaces production's
# hints and its kept output is the new record (notes/2026-11-23-climber-restart.md, "Fill lemmas and trust").
# Usage: bash abs/revf.sh loops/TRUSTNOW/tHHMM loops/REVFn
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
python3 /project/twee/hints/transfer.py run $D/goals.tsv $D -j ${J:-1} --time 60 --src-lemmas 0 --live-dst loops/UL -- \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 6 --lemma-knn 30 --lemma-subsets --lemma-after --pool original --twee /project/bin/twee-pg61 --wall-factor 15 \
  --keep-out "--args=--abstract-time 2000 --no-eqhint-consider" > $D/run.log 2>&1
echo "revf done $(date '+%d %T'): $(grep -c -P '\tTHM\t' $D/transfer.tsv 2>/dev/null) of $(wc -l < $D/goals.tsv) proved" | tee -a $D/run.log

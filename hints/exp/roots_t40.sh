#!/bin/bash
# (21 Nov 00:47) The 190 roots (production's proofs whose recorded lemmas Z6 all proved) at 40 s in Z6's final
# lemma context (notes/2026-11-21-roots.md). Production's transfer options (exp/stepjoin.py OPTS), no hints.
cd /project/hintwork
D=loops/ROOTS/t40
[ -e $D ] && { echo "$D exists"; exit 1; }
mkdir -p $D
cp loops/Z6/solved.tsv $D/solved.tsv
ln -s /project/hintwork/loops/Z6/hints $D/hints
: > $D/empty
cut -f1 loops/ROOTS/roots_z6.tsv | awk -v e=/project/hintwork/$D/empty '{print $1 "\t" e "\t0"}' > $D/goals.tsv
OPTS=$(python3 -c "import sys; sys.path.insert(0,'/project/twee/hints/exp'); from stepjoin import OPTS; print('\n'.join(OPTS))")
mapfile -t O <<< "$OPTS"
TWEE_PG_ARGS='--pg-threshold 0.25 --ground-joining-branch-limit 100' OMP_NUM_THREADS=1 \
  python3 /project/twee/hints/transfer.py run $D/goals.tsv $D -j ${J:-1} --time 40 --src-lemmas 0 -- "${O[@]}" > $D.log 2>&1
echo "roots t40 done $(date +%T)" > $D.done

#!/bin/bash
# (23 Nov) The hint bed (notes/2026-11-23-conditional.md, "Hint bed"): 600 goals plain runs failed in PLN2 (seed 64,
# sets/hintbed600), PLN2's problems exactly (t0641, 30+10 siblings, 100 kNN), 5 s, 3 threads; arms:
#   HB2000, HB200: --hints-lemmas 2000 / 200 (the lemma goals' proof steps, siblings nearest first, then kNN by rank)
#   HBC: a perturbation control, plain with --abstract-time 1990 instead of 2000 (twee's limit is set by --max-time 5
#        abstract seconds, so this changes the CP count per second a little)
cd /project/hintwork
C="--trusted loops/TRUSTNOW/t0641.trusted --only sets/hintbed600 -j 3 --time 5 --sibs 30 --after 10 --knn 100 --proved"
echo "start $(date '+%d %T')" > cond/HINTBED.done
for arm in HBC HB200 HB2000; do
  [ -e cond/$arm ] && { echo "cond/$arm exists"; exit 1; }
  case $arm in HBC) X=(--args "--abstract-time 1990");; HB200) X=(--hints-lemmas 200);; HB2000) X=(--hints-lemmas 2000);; esac
  python3 -u /project/twee/hints/exp/condprove.py cond/$arm $C "${X[@]}" > cond/$arm.log 2>&1
  echo "$arm $(date '+%T') $(grep -c -P '\tTHM\t' cond/$arm/results.tsv) of $(grep -c . cond/$arm/results.tsv)" >> cond/HINTBED.done
done

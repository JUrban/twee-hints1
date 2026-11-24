#!/bin/bash
# (24 Nov) clq83 (exp83): a second live climber with no climbs and a 40 CPU s final, ahead of CLS71 on the same stalled
# queue. Of CLS71's 124 final proofs since 08:59, 62 took under 40 CPU s, while a failed final costs a median 408 s; and
# production gave those goals only 5 s runs (a median of 57 each). The question: proofs per CPU h of a 40 s final in
# the climber's order (nearest a proved goal first), against CLS71's. cls71e.sh's options, plus --runs 0 (the final
# only), --final-cpu 40, -j 3 (J), --cpus 23 (it took HLS2's 3); no --reclimb, --final-only-ab is moot. The record
# dir starts with a copy of CLS71's true.tsv, fillhints/ and sketches/, so its finals have the sketch hints CLS71's
# final-only finals have. Excluded: sets/localheads71 and CLS71's finished targets since 08:59 (they had the full final).
# notes/2026-11-24-quick-finals.md.
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
cd /project/hintwork
python3 /project/twee/hints/climb.py sets/all loops/CLQ83 --live loops/UL --exclude "${EXCLUDE:-sets/clq83.excl}" \
  --m 8 --knn 8 --theories 4 --theory-explore 2 --theory-lemmas 10 --updown --up-single --weaken 4 --chain --fill 3 \
  --min-sketch-steps 30 --runs 0 --sketch-time 5 --final-time 160 --final-cpu "${FCPU:-40}" -j "${J:-3}" --cpus "${CPUS:-23}" -- \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 30 --lemma-knn 400 --lemma-subsets --lemma-after --pool original --twee /project/bin/twee-pg61 --wall-factor 15 \
  --args="--abstract-time 2000 --no-eqhint-consider --conditional-encoding fresh" >> loops/CLQ83.log 2>&1
echo "CLQ83 ended $(date '+%d %T')" >> loops/CLQ83.log

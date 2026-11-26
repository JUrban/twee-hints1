#!/bin/bash
# (26 Nov 15:09) clq87g: clq87f plus TWEE_LEMMA_EQN=1:
# a conditional goal whose hypothesis has a variable side runs as its equivalent equation (TWEE_LEMMA_EQN=1,
# lemmas.equation_problem in lemma_problem; lemmas 6234ec7). exp94 (the 134 unsolved such goals, plainlive's settings):
# 60 s equation 2 proved, the original 0, original only 0; 5 s 1 against 0.
# Launch: CPUS=23 bash abs/clq87g.sh.
# (26 Nov 11:12) clq87f: clq87e plus --listen-class "${LCLASS:-150}" (as cls71k and production), restarted after its
# longest final, also for hintsel.listen_equation (conditional goals with a variable-side hypothesis listened as
# their equation). Launch: CPUS=23 bash abs/clq87f.sh.
# (25 Nov 22:03) clq87e: clq87d.sh with --listen 300 --listen-dist 100000: each final listens to all its original's unsolved plain
# goals (up to 300), not the nearest 8 within 10; with twee-e61m the search is unchanged and 120 listened goals cost
# +4.6% CPU in a 160 s final (exp90, notes/2026-11-25-time-ladder.md).
# (25 Nov) clq87d: clq87c.sh plus --listen 8 and --twee /project/bin/twee-pg61l (twee-e61l), as cls71i.sh: each 640 s final
# carries up to 8 of its original's unsolved plain-equation goals within 10 as listened goals (exp89).
# (25 Nov 15:29) the time ladder's 640 abstract s rung with climbs and CLS71's sketch and fill hints too (--share; the user:
# keep the strengthened-theory hints in the global hint db). Otherwise abs/clq87b.sh; same loops/CLQ83 and log.
# (24 Nov) clq83 (exp83): a second live climber with no climbs and a 40 CPU s final, ahead of CLS71 on the same stalled
# queue. Of CLS71's 124 final proofs since 08:59, 62 took under 40 CPU s, while a failed final costs a median 408 s; and
# production gave those goals only 5 s runs (a median of 57 each). The question: proofs per CPU h of a 40 s final in
# the climber's order (nearest a proved goal first), against CLS71's. cls71e.sh's options, plus --runs 0 (the final
# only), --final-cpu 40, -j 3 (J), --cpus 23 (it took HLS2's 3); no --reclimb, --final-only-ab is moot. The record
# dir starts with a copy of CLS71's true.tsv, fillhints/ and sketches/, so its finals have the sketch hints CLS71's
# final-only finals have. Excluded: sets/localheads71 and CLS71's finished targets since 08:59 (they had the full final).
# notes/2026-11-24-quick-finals.md.
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
export TWEE_LEMMA_EQN=1
cd /project/hintwork
python3 /project/twee/hints/climb.py sets/all loops/CLQ83 --live loops/UL --exclude "${EXCLUDE:-sets/none}" --reclimb "${RECLIMB:-sets/ladder640.re}" --reclimb-max 3 --listen "${LISTEN:-300}" --listen-dist "${LDIST:-100000}" --listen-class "${LCLASS:-150}" --share "${SHARE:-/project/hintwork/loops/CLS71}" \
  --m 8 --knn 8 --theories 4 --theory-explore 2 --theory-lemmas 10 --updown --up-single --weaken 4 --chain --fill 3 \
  --min-sketch-steps 30 --runs "${RUNS:-20}" --sketch-time "${STIME:-5}" --final-time "${FINAL:-640}" --final-cpu "${FCPU:-0}" -j "${J:-5}" --cpus "${CPUS:-20}" -- \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 30 --lemma-knn 400 --lemma-subsets --lemma-after --pool original --twee /project/bin/twee-pg61l --wall-factor 15 \
  --args="--abstract-time 2000 --no-eqhint-consider --conditional-encoding fresh" >> loops/CLQ83.log 2>&1
echo "CLQ83 ended $(date '+%d %T')" >> loops/CLQ83.log

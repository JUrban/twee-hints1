#!/bin/bash
# (26 Nov 19:20) cls71m: cls71l as the ladder's next rung: 640 s finals (FINAL 640) on its own list only (--list-only,
# climb.py; not production's new stalled goals, which CLQ83 takes at 640 s), a third final each (--reclimb-max 3): at
# 19:18 all 1,222 unsolved goals of sets/cls71all.re outside sets/cls71f.excl had two failed CLS71 finals (160 s) and
# CLS71 ran no twee. -j 5 (640 s runs grow to 2-4 GB). Launch: RECLIMB=sets/cls71all.re
# EXCLUDE=sets/cls71f.excl,sets/ladder640.re bash abs/cls71m.sh (ladder640.re is CLQ83's list).
# (26 Nov 15:09) cls71l: cls71k plus TWEE_LEMMA_EQN=1:
# a conditional goal whose hypothesis has a variable side runs as its equivalent equation (TWEE_LEMMA_EQN=1,
# lemmas.equation_problem in lemma_problem; lemmas 6234ec7). exp94 (the 134 unsolved such goals, plainlive's settings):
# 60 s equation 2 proved, the original 0, original only 0; 5 s 1 against 0.
# Launch: RECLIMB=sets/cls71all.re EXCLUDE=sets/cls71f.excl bash abs/cls71l.sh.
# (26 Nov 02:19) cls71k: cls71j plus --listen-class "${LCLASS:-150}" (climb.py 0edb5ad, as production's ul88): each
# final also listens to up to 150 unsolved plain goals of the other originals with the same axioms; lp.listen_credit
# checks such a proof's premises and names its lemma_goal_N for trust.py. ul88's first 1.5 h: 28 listened credits,
# 15 of them across originals. Launch: RECLIMB=sets/cls71all.re EXCLUDE=sets/cls71f.excl bash abs/cls71k.sh.
# (25 Nov 22:03) cls71j: cls71i.sh with --listen 300 --listen-dist 100000: each final listens to all its original's unsolved plain
# goals (up to 300), not the nearest 8 within 10; with twee-e61m the search is unchanged and 120 listened goals cost
# +4.6% CPU in a 160 s final (exp90, notes/2026-11-25-time-ladder.md).
# (25 Nov) cls71i: cls71h.sh plus --listen 8 and --twee /project/bin/twee-pg61l (twee-e61l): each final carries up to 8 of
# its original's unsolved plain-equation goals within 10 as listened goals; one proved is rerun with its proof printed
# and recorded as a real proof (exp89: 2 of 117 at 320,000 pairs; notes/2026-11-25-time-ladder.md, "exp89").
# (25 Nov) cls71h: cls71g.sh with --final-hints-ab in place of --final-nopool-ab: three arms of the finals by (crc32 >> 3) % 3,
# the pool hints, the sketch hints only, the sketch hints and the 10 nearest solved siblings' proof steps (exp88b:
# 11, 10 and 12 of 22 stalled goals at 160,000 pairs, 16 together).
# (25 Nov) cls71g: cls71f.sh plus --share loops/CLQ83 (SHARE): the 640 s rung's sketch and fill hints too (as clq87c.sh
# shares CLS71's; notes/2026-11-25-time-ladder.md, "hint sharing").
# (25 Nov) cls71f: cls71e.sh plus --final-nopool-ab: the finals of targets with bit 3 of crc32 set get the sketch hints only,
# no pool hints (without production's hints 22 stalled goals at 160,000 pairs: 10 proofs against 11, 14 together, fewer
# pairs on 6 of the 7 both proved; notes/2026-11-25-time-ladder.md, exp88).
# (24 Nov) cls71e: cls71d.sh with -j 10 (J): exp82c ended at 12:59, and the climber, at 2.2-3.5 proofs per CPU h the best
# producer, used all 8 threads; the cap (a climb starts only while fewer than 20 other twee processes run) still holds.
# (24 Nov) cls71d: cls71c.sh plus (1) --final-only-ab: targets with bit 2 of crc32 set get only the 160 s final, the others
# the full climb, to measure what a climb adds to its final (notes/2026-11-23-climber-restart.md, "final-only A/B");
# (2) twee --conditional-encoding fresh: Horn assumptions cost 8x the CPU with the default encoding (exp82), no change
# without them; (3) -j 8 (J): HLW1 ended at 08:48, and the cap (fewer than 20 other twee processes) still holds.
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
export TWEE_LEMMA_EQN=1
cd /project/hintwork
mkdir -p loops/CLS71
python3 /project/twee/hints/climb.py sets/all loops/CLS71 --live loops/UL --exclude "${EXCLUDE:-sets/localheads71}" --reclimb "${RECLIMB:-sets/cls71re}" --reclimb-max 3 --list-only --final-only-ab --final-hints-ab --listen "${LISTEN:-300}" --listen-dist "${LDIST:-100000}" --listen-class "${LCLASS:-150}" --share "${SHARE:-/project/hintwork/loops/CLQ83}" \
  --m 8 --knn 8 --theories 4 --theory-explore 2 --theory-lemmas 10 --updown --up-single --weaken 4 --chain --fill 3 \
  --min-sketch-steps 30 --runs 20 --sketch-time 5 --final-time "${FINAL:-640}" -j "${J:-5}" --cpus "${CPUS:-20}" -- \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 30 --lemma-knn 400 --lemma-subsets --lemma-after --pool original --twee /project/bin/twee-pg61l --wall-factor 15 \
  --args="--abstract-time 2000 --no-eqhint-consider --conditional-encoding fresh" >> loops/CLS71.log 2>&1
echo "CLS71 ended $(date '+%d %T')" >> loops/CLS71.log

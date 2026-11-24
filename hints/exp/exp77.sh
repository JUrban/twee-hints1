#!/bin/bash
# (24 Nov 00:51) exp77: twee's own CASC strategies on local heads (notes/2026-11-24-cond-replay.md, "exp77"). Every production
# run uses twee's default queue (lhs-weight 4, depth-weight 2, default KBO); twee's parallel portfolio
# (executable/ParallelMain.hs) varies it. Four of its UEQ strategies, as plain 60 s runs with H's lemma lists (100+30
# siblings, 400 kNN; condprove.py --proved), on 120 of the 937 unsolved local heads (sets/exp77, exp/sets/exp77,
# seed 77). The control is HLW1 (the sweep queue, the same setting with twee's defaults on all local heads).
# --complete-subsets and --depth-weight 60 are left out: with 529 lemma axioms they spend 5-10 times the CPU per
# critical pair, so at equal abstract time they would get that much more CPU (smoke test, the notes).
#   A1: --lhs-weight 1 --flip-ordering --normalise-queue-percent 10 --cp-renormalise-threshold 10 --ground-joining-incomplete-limit 15
#   A2: --no-flatten-goal --ground-joining-incomplete-limit 15 --ground-connectedness --normalise-queue-percent 10 --cp-renormalise-threshold 10
#   A4: --lhs-weight 9 --flip-ordering --normalise-queue-percent 10 --cp-renormalise-threshold 10
#   A8: --no-kbo-weight0-unary --kbo-weight0 --no-flatten-goal
# Two arms at a time, 2 threads each, after exp67's controls end. Proofs: condimport.py --args (the rerun under the
# arm's strategy) into loops/CI77, merge.py into loops/UL.
cd /project/hintwork
END=$(date -d "2026-11-24 10:00" +%s)
until grep -q "^CC67C/CC67D done" loops/EXP67.pids || [ $(date +%s) -gt $END ]; do sleep 60; done
cut -f1 loops/UL/solved.tsv | sort -u > cond/STR77.trusted
echo "exp77 start $(date '+%d %T') context $(wc -l < cond/STR77.trusted)" > cond/STR77.status
arm() {
  N=STR77_$1; shift
  [ -e cond/$N ] && { echo "cond/$N exists" >> cond/STR77.status; return; }
  python3 -u /project/twee/hints/exp/condprove.py cond/$N --trusted cond/STR77.trusted -j 2 --proved --time 60 \
    --sibs 100 --after 30 --knn 400 --only sets/exp77 --args "$*" > cond/$N.log 2>&1
  flock cond/merge.lock python3 /project/twee/hints/exp/condimport.py cond/$N loops/CI77 --trusted cond/STR77.trusted --time 60 --args "$*" > cond/$N.import 2>&1
  flock cond/merge.lock python3 /project/twee/hints/merge.py loops/UL loops/CI77 > cond/$N.merge 2>&1
  echo "$N done $(date '+%d %T') ran $(grep -c . cond/$N/results.tsv) THM $(grep -c -P '\tTHM\t' cond/$N/results.tsv) | $(tail -n 1 cond/$N.merge)" >> cond/STR77.status
}
arm A1 --lhs-weight 1 --flip-ordering --normalise-queue-percent 10 --cp-renormalise-threshold 10 --ground-joining-incomplete-limit 15 &
arm A2 --no-flatten-goal --ground-joining-incomplete-limit 15 --ground-connectedness --normalise-queue-percent 10 --cp-renormalise-threshold 10 &
wait
arm A4 --lhs-weight 9 --flip-ordering --normalise-queue-percent 10 --cp-renormalise-threshold 10 &
arm A8 --no-kbo-weight0-unary --kbo-weight0 --no-flatten-goal &
wait
echo "exp77 done $(date '+%d %T')" >> cond/STR77.status

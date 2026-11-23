#!/bin/bash
# (18 Nov 17:13) ul47: ul46 plus --variants k60,two,unf,sub (the portfolio, notes/2026-11-18-portfolio-review.md): a goal
# whose 80 s chain run failed gets four more 80 s runs in the same context, each with one change, before the 320 s level:
# 60 kNN lemmas, the two-sided chain, definitions unfolded, subsumption matching. On the 92 walls exp11's chain run
# failed, each proved 3-6 of them at 0.4-1.3 proofs per CPU hour (exp17, exp14, exp15, exp18); production's own L1 makes
# 1.16 per CPU hour since 12:02, and its L2 never ran. Results rows of the variants are labelled Vk60, Vtwo, Vunf, Vsub.
# (18 Nov 14:50) ul45 on 4 workers instead of 8, with chain_records2.tsv (chain_records.tsv plus the records of the
# merged experiment proofs: sibchain.py --build --extra exp3, exp8-exp12, exp14 out dirs). From 13:20 to 14:40 ul45 proved
# nothing: its 5 s classes had no candidates and all 8 workers ran 80 s chain runs (about 130, none proved). The 4
# freed workers run exp18 (subsumption matching at 80 s on the walls).
# (18 Nov 12:02) ul44 with loop.py running the chain level (80 s) fresh, plus --chain-since-row 47530 (the first row of
# ul43, 08:28). ul43/ul44 resumed the 5 s pool state at 80 s, so with --no-resume-requeue the chain reached only
# pairs made after 5 s. exp3/exp8 tested fresh chain runs (12 vs 9 at 320 s, 9 vs 5 at 80 s). --chain-since-row
# reopens the 1,032 unsolved goals whose deep runs all predate the chain (exp11: 15 of 107 such walls at 80 s).
export TWEE_PG_ARGS="--pg-threshold 0.25 --ground-joining-branch-limit 100"
cd /project/hintwork
python3 -u /project/twee/hints/loop.py sets/all loops/UL --start 5 --cascade 5,80,320 --cascade-start 0 --cascade-continue --retry-gap 3 \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 6 --lemma-knn 30 --lemma-subsets --lemma-after --twee /project/bin/twee-pg61 --keep-out -j 4 --reserve 0 \
  --pool original --wall-factor 15 "$@" --line-gaps 80,80 --retry-hints 1.25 --sync 60 --fresh-first --far-retry --mix 0.25 --sched-model /project/hintwork/sched/m4.json --sched-max-lgap 320 --sched-retrain 200 --sched-pmin 0.011 --sched-pmin-auto 400 --retry-knn --chain-level 1 --chain-records /project/hintwork/chain_records2.tsv --chain-since-row 47530 --variants k60,two,unf,sub --args="--abstract-time 2000 --no-resume-requeue --no-eqhint-consider" > loops/UL47.log 2>&1
echo "UL47: $(tail -1 loops/UL47.log) $(date +%T)" | tee loops/UL47.done

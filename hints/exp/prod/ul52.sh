#!/bin/bash
# (18 Nov 20:26) ul52: ul51 unchanged, restarted for loop.py's memoised hint unfolding (ul51 ran 1-3 twee processes on
# its 16 workers: the threads unfolded 20-30k hints a run, 5-6 s each, under the GIL).
# (18 Nov 20:15) ul51: ul50 on 16 workers (exp20's 4 and 2 spare), the 80 s variants after the 160 s level ordered k60,
# unf, two and without sub and nopg: exp20 (complete) gave the chain to 160 s 12 of the 92 failed walls at 1.77 per CPU
# hour on the increment, and after it k60 adds 5 (1.19), unf 6 (0.47), two 1 (0.23), sub and nopg 0 of 68 each.
# Priors in loop.py set to these conditional yields (fc74100).
# (18 Nov 19:38) ul50: ul49 on 10 workers (P9C's 4 move here: 1 proof in 217 runs on 4 workers since 18:26, 0.28 per CPU
# hour) with nopg (no parental guidance, 80 s) as the last variant before 320 s. exp22 G80: 2 new of the 92 failed walls
# at 0.43 per CPU hour, 1 after k60/two/unf/sub (about 0.22). Memory at 19:20: 8.4 GB for all my processes.
# (18 Nov 18:53) ul49: ul48 with an 80 -> 160 s resume level right after the 80 s chain run (--cascade 5,80,160,320,
# --variants-after 2: the 80 s variants follow the 160 s level), --pass-every 1, and priors set to the variants' yields
# conditional on the earlier members (Vtwo 0.60, Vunf 0.48, Vsub 0.16). exp20 (exp11's chain at 160 s on the 92 failed
# walls): 6 new on the first 44 at 1.52 per CPU hour on the increment, overlapping 60 kNN lemmas' 4 in 1. ul48's full
# pass took 0.51 s a run with every failed-fresh goal a deep candidate.
# (18 Nov 18:30) ul48: ul47 on 6 workers with --variants unf@0,k60@0,k60,two,unf,sub and --ratio-order. exp21 (300 goals
# whose 5 s fresh run failed, 9 arms at 5 s): only unfolding (4, 3.8 new proofs per CPU hour) and 60 kNN lemmas (1) proved
# any; the control and six search changes none. So every goal whose fresh run failed (5,869 at 17:17, near the frontier
# or not) gets an unfolded and a 60-lemma 5 s run. --ratio-order orders the deep queue by the next level's estimated
# yield (priors: notes/2026-11-18-portfolio-review.md, updated from this round's results), heads first. The 2 extra
# workers come from exp19 (--set-join on the walls, paused at 37 of 107: 1 new, 0.31 per CPU hour).
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
python3 -u /project/twee/hints/loop.py sets/all loops/UL --start 5 --cascade 5,80,160,320 --cascade-start 0 --cascade-continue --retry-gap 3 \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 6 --lemma-knn 30 --lemma-subsets --lemma-after --twee /project/bin/twee-pg61 --keep-out -j 16 --reserve 0 \
  --pool original --wall-factor 15 "$@" --line-gaps 80,80 --retry-hints 1.25 --sync 60 --fresh-first --far-retry --mix 0.25 --sched-model /project/hintwork/sched/m4.json --sched-max-lgap 320 --sched-retrain 200 --sched-pmin 0.011 --sched-pmin-auto 400 --retry-knn --chain-level 1 --chain-records /project/hintwork/chain_records2.tsv --chain-since-row 47530 --variants unf@0,k60@0,k60,unf,two --variants-after 2 --ratio-order --pass-every 1 --args="--abstract-time 2000 --no-resume-requeue --no-eqhint-consider" > loops/UL52.log 2>&1
echo "UL52: $(tail -1 loops/UL52.log) $(date +%T)" | tee loops/UL52.done

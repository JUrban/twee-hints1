#!/bin/bash
# (19 Nov 10:14) ul63: ul62 plus hl@0 (loop.py 5fc6b48): the pool plus the proof steps of the goal's 30 kNN lemmas at
# factor 0.1, a 5 s run. In UL it adds 60-585 hints (median about 270) to pools of 2,600-21,000 (hints/exp/hl_count.py).
# Under --explore 1 with the other lemma-set variants.
# Also five search-setting variants at 5 s, each dropped on count before (loop.py 4d3baca): m7t@0 (rule model rm7t,
# retrained with the loop's proofs, 2u), m4b@0 (rm4b, 4 times the trees, +9 -7 at 8 s, 2f), r2@0 (rule threshold 0.2),
# nopg@0 (no parental guidance) and nom@0 (no rule model). Each under --explore 1.
# And k400@0 and k200s12@0: in ul62's first 10 minutes Vk200@0 proved 14 in 1.01 CPU h, all after Vk100@0 had failed in
# the same context (hints/exp/condvar.py).
# (19 Nov 10:06) ul62: ul61 with two more lemma-set variants at 5 s, k200@0 (200 kNN lemmas) and s12@0
# (12 sibling lemmas; loop.py e2986e3), and --explore 1 for the lemma-set variants (loop.py 3f95f59) instead of priors
# set by hand: each is estimated at no less than the best measured member until it has 1 CPU hour of runs. In ul60
# Vk100@0 proved 42 in 2.95 CPU hours (14 per CPU hour), 32 of them after Vk60@0 failed in the same context.
# (19 Nov 09:19) ul61: ul60 on 19 workers, with the lemma-set variants' priors at 9 (was 3). In ul60's first 45
# minutes they ran 7-9 times each: the deep queue is sorted by each goal's best option, and Vk60@0 options (8.5 per CPU
# hour live) keep coming, so a variant below that never comes up. At 9 each gets measured over about 2 CPU hours; if it
# yields about 1, its estimate falls below Vk60@0's within 2-4 CPU hours.
# (19 Nov 08:05) ul60: ul59 (J workers, default 19; 12 while exp27 runs, to about 09:20), with three lemma-set variants at 5 s (loop.py 92d60c4): kp@0 (kNN
# lemmas by similarity x use counts), kd@0 (MaSh-style proof dependencies), k100@0 (100 kNN lemmas). The 16 Nov tests
# dropped them as not better on count, though each proved goals plain similarity did not (+3, +1, +1 of 150); at 5 s
# only problem-changing variants pay (exp21), and k60@0 makes 8.4 per CPU hour live. Priors 3 each (about Vunf@0's live
# yield), so each is measured over ~2 CPU hours before its own yield decides (notes/2026-11-18-portfolio-review.md).
# Also --knn-refresh 600 (was 1800): of the 401 proofs since ul58's start, 392 used a kNN lemma of another original,
# and for 171 the youngest of these was proved within the last 30 minutes (64 within 10). A rebuild takes about 1 s.
# (19 Nov 07:18) ul59: ul58 on 12 workers for about 2 h, while exp27 (half1 from zero with today's system, 6 workers +
# its transfer's 2; notes/2026-11-19-from-zero-portfolio.md) runs. --relabel-until is ul58's first row (103427) fixed:
# computed at start as in ul58.sh, it would relabel ul58's own 40 s rows. ul58 made 83 new in its first hour (07:05).
# (19 Nov 06:02) ul58: ul57 with a 40 s chain level, --cascade 5,40,80,160,320 (loop.py 1bb0a0f). ul56's 81 L1 proofs
# (80 s chain runs) came at abstract times with median 29 s; 50 within 40 s, 28 within 20 s. Twee is deterministic in
# abstract time, so a 40 s run proves exactly those 50, at about half the CPU: 1.73 per CPU hour against 1.45 for the
# 80 s run. The 40 -> 80 s resume then makes about 1.1, and the ratio rule places it among the variants. The variants
# stay at 80 s (--variant-budget 80) after the 160 s level (--variants-after 3). Rows before the restart are relabelled
# by budget (L1=L2, L2=L3, L3=L4), so an 80 s run counts as the new 80 s level and its state resumes to 160 s; the old
# fresh 80 s rows do not count in the new L2's yield (--relabel-nostat L2). The A/B test exp26 goes on (--ab-args).
# (19 Nov 05:52) ul57: ul56 restarted for loop.py 516f416 and an A/B test (exp26). The deep runs (above 5 s, not p9) of
# half the goals, by a hash of the name, run without queue renormalisation (--cp-renormalise-threshold 1000); their rows
# carry ab=1. exp25: on 6 walls at 80 s that cost 25% less CPU (613 against 823 s) with no higher peak memory, but it
# changes the search (2 of the 3 proofs kept). Measure L1, L2 and the 80 s variants per CPU hour by arm
# (levyield.py ROW: L1 against L1/B). Also in: chain-hint levels wait for the chain records (2b5d7d8), and the restart's
# pool-growth check uses fresh rows only (5f8fd4a; the old check would have rerun ~2,553 unchanged goals now).
# ul56 made 274 new in 5 h 30 min (05:30).
# (18 Nov 23:59) ul56: ul55 restarted for loop.py 119c3d1. Variant levels are optional attempts: a goal's next attempt
# is its eligible option of highest live yield, the next cascade level or an untried variant after a level it ran, so a
# variant that stopped paying no longer holds back the goal's next level. Results rows record their context (c=), and
# the replay restarts a goal's attempts at each fresh run (it kept the round's highest level: 892 unsolved goals reopened
# by new proofs had lost their deeper levels). ul55 made 146 new in its first hour (23:40).
# (18 Nov 22:39) ul55: ul54 restarted for variant tiers (loop.py a0a4486): the variants after one cascade level are tried
# in order of their current yield, each once per context. ul54's fixed order made every goal run the unfolded 5 s level
# (0.39 per CPU hour by 22:35, used up) before the 60-lemma 5 s level (5.5).
# (18 Nov 21:22) ul54: ul53 on 19 workers (exp22 done; transfer.py live and the loop's own thread take the rest of 20)
# with nom (no rule model, 80 s) as the last variant before 320 s: exp22 N80 gave 4 new of the 92 failed walls alone
# and 1 after the 160 s run, k60, p9, unf, two and nopg (0.23 per CPU hour, as two's 0.25).
# (18 Nov 20:34) ul53: ul52 with Prover9 + chain as a cascade level (--variants p9) after the 60-lemma variant. Stopping
# the P9C side worker at 19:38 dropped a complementary member: live it proved 4 in 350 runs (about 0.7 per CPU hour) on
# goals that had failed the 160 or 320 s level, above unf (0.47) and two (0.23) there. In the cascade it gets each goal
# once per context, after k60, instead of a nearest-first list it had exhausted.
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
python3 -u /project/twee/hints/loop.py sets/all loops/UL --start 5 --cascade 5,40,80,160,320 --cascade-start 0 --cascade-continue --retry-gap 3 \
  --model --model-fixed /project/hintwork/models/rm4t.bin,/project/hintwork/models/rm4t.vocab --model-theory \
  --lemmas 6 --lemma-knn 30 --lemma-subsets --lemma-after --twee /project/bin/twee-pg61 --keep-out -j ${J:-19} --reserve 0 \
  --pool original --wall-factor 15 "$@" --line-gaps 80,80 --retry-hints 1.25 --sync 60 --fresh-first --far-retry --mix 0.25 --sched-model /project/hintwork/sched/m4.json --sched-max-lgap 320 --sched-retrain 200 --sched-pmin 0.011 --sched-pmin-auto 400 --retry-knn --knn-refresh 600 --chain-level 1 --chain-records /project/hintwork/chain_records2.tsv --chain-since-row 47530 --variants unf@0,k60@0,k100@0,k200@0,k400@0,kp@0,kd@0,s12@0,k200s12@0,hl@0,m7t@0,m4b@0,r2@0,nopg@0,nom@0,k60,p9,unf,two,nom --variants-after 3 --variant-budget 80 --priors L1=1.73,L2=1.1 --explore 1 --explore-labels Vk100@0,Vk200@0,Vk400@0,Vk200s12@0,Vkp@0,Vkd@0,Vs12@0,Vhl@0,Vm7t@0,Vm4b@0,Vr2@0,Vnopg@0,Vnom@0 --relabel L1=L2,L2=L3,L3=L4 --relabel-until 103427 --relabel-nostat L2 --ratio-order --pass-every 1 --ab-args="--cp-renormalise-threshold 1000" --args="--abstract-time 2000 --no-resume-requeue --no-eqhint-consider" > loops/UL63.log 2>&1
echo "UL63: $(tail -1 loops/UL63.log) $(date +%T)" | tee loops/UL63.done

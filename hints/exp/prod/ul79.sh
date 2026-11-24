#!/bin/bash
# (24 Nov 01:14) ul79: ul78 plus --retry-climb --retry-climb-hours 6 (exp78): a goal whose climb sketches (any
# --climb-hints dir) are newer than its last fresh run, or than 6 hours before the start, counts as grown and gets one
# fresh run, so the sk members try its new climb hints. 127 of CLS71's first 149 climbed targets had no production run
# after their climb; 193 unsolved targets have sketches from the last 6 hours. Each such retry is logged in
# loops/UL/climbretry.tsv (notes/2026-11-24-cond-replay.md, "exp78"). One change; J=6.
# (23 Nov 23:42) ul78: ul77 plus member skk400s30@1:0: sk@1:0 (40 s fresh after L0, the climb hints and fill lemmas) with
# 30 sibling and 400 kNN lemmas in place of 6 and 30 (exp73, loop.py's new skkNsM members). exp67's arms on the same
# frozen heads: 30+400 lemmas proved 7, 6+30 proved 2, at the same CPU; the plain head runs (H: 100+30, 400, 60 s)
# are the plain live loop's best setting; sk@1:0 is production's top member (2 of ul76's 5 proofs, 60% of its CPU).
# Explored and ordered by live yield like every member. One change; J=6 (notes/2026-11-23-tail-allocation.md, "exp73").
# (23 Nov 23:23) ul77: ul76 plus four climb dirs in --climb-hints: loops/CLS71 (exp71, the live climber on stalled goals,
# started 23:22; CLU's mode, whose 7,302 sketch files over 108 originals lie behind most of sk@1's recent proofs) and
# the key-goal climbs loops/CLK69, K70F, K70R (exp69/exp70: sketches of the cluster of 7 originals). The dirs are
# re-scanned every 10 minutes, so CLS71's sketches reach sk@0 and sk@1:0 as they come. One change; J=6 as ul76
# (notes/2026-11-23-climber-restart.md, "exp71").
# (23 Nov 21:14) ul76: ul75 plus today's climbers in --climb-hints (loops/CLHL3, CLHL4, CLA67, CLB67: their sketches
# and fill steps). In ul75's last 6,000 runs member sk@1:0 (40 s fresh runs with the climb hints) made 8 of the 19
# proofs, the most of any member; its dirs were all from 15-20 Nov, so the sketches of today's heads never reached it
# (notes/2026-11-23-climber-restart.md, "ul76"). One change; J=6 as ul75.
# (22 Nov 07:13) ul75: ul74 plus --head-class (exp47/exp48, notes/2026-11-21-head-class.md): heads whose next own level is
# L1 are a mix class of their own (h), dispatched at L1 nearest first. Since ul74 started (21 Nov 16:50, 14.3 h) L1 proved
# 17 in 23.8 CPU h (0.71/h), the 5 s variants 8 in 52.7, and 253 of the 1,026 heads had no L1 run: with --ratio-order
# the deep list puts L1 behind the variants (notes/2026-11-22-ul75.md).
# (20 Nov 04:14) ul74: ul73 with (1) member m10f@0 in place of m9f@0: rm10f is rm9f's recipe on all data (abs/rm10.sh; the
# 400 test logs and every proof since 19 Nov 19:50 included), and (2) --given-scan loops/GFAIL: every failed run's
# given rules (twee --print-given-unsolved, about 6% more time) checked against the unsolved unit goals. Hits go to
# loops/GFAIL/hits.tsv with the run's log; givenmatch.py live (abs/gmlive.sh) runs them (exp38,
# notes/2026-11-20-given-transfer.md).
# (20 Nov 02:16) ul73: ul72 with member m9e@0 (rm9e: 2 longest proofs per goal over all loops; third in exp37's greedy
# cover, 2 unique proofs) in place of m9i@0 (no proof beyond rm9f's in the replay, 0 in its 1.0 CPU h exploration).
# notes/2026-11-19-retrained-models.md, "Final paired result".
# (19 Nov 23:30) ul72: ul71 plus the weighted retrained rule models as members m9f@0, m9h@0, m9i@0 (exp37,
# notes/2026-11-19-retrained-models.md): Suda's per-log weighting (CADE 2021) on production's logs (rm9f, AUC 0.892;
# rm9i with 255 leaves, 0.900) and on the 2 longest proofs per goal over every loop (rm9h, 0.891), against rm4t's 0.835
# on the 400 newest held-out proofs. Replayed as of each proof at 20 s: rm9f +9 -5 on 246, rm9h +5 -1 on 106, while the
# unweighted ones lose (rm9a +11 -27). Explored like every member. J=8 while exp37's arms run.
# (19 Nov 20:30) ul71: ul70 plus the retrained rule model m9a@0 (exp37, user 19:35: "go ahead with the retrained rule model
# member"): models/rm9a = rm7t's recipe on today's data (base + production's 21,125 logs, 150 negatives per log, the 400
# newest held out; AUC 0.876 on them against rm4t 0.835). Explored like every member. J=10 while exp37 trains and runs
# its paired arms (notes/2026-11-19-retrained-models.md).
# (19 Nov 17:58) ul70: ul69 plus the climbs' hints as members (user: "why not collect the climb hints anyway?"):
# sk@0 (5 s) and sk@1:0 (40 s fresh, after L0) take the pool plus the original's steps from every climb directory's
# sketches/ and fillhints/ (loop.py --climb-hints; 65,021 steps of 108 originals at 17:58, re-scanned every 10 minutes).
# Explored like the other members. Run with J=15 while exp36 runs (notes/2026-11-19-climb-ablation.md).
# (19 Nov 16:33) ul69: ul68 plus --reexplore 150:0.25 --climb-hints /project/hintwork/loops/CLH,/project/hintwork/loops/CLHL,/project/hintwork/loops/CLU,/project/hintwork/loops/CLHL2,/project/hintwork/loops/FUD2p,/project/hintwork/loops/FUDs (user: "go ahead with the periodic re-exploration"): a label that had
# its explore hour but got under 0.25 CPU h among the last 150 CPU h of all runs (about 9 hours on 17 workers) is explored
# again until it has 0.25 in the window. About 38 labels x 0.25 = at most about 6% of the CPU. The window is in CPU, in
# row order, so restarts rebuild it exactly.
# (19 Nov 16:26) ul68: ul67 with every label explored (no --explore-labels): since 06:00 the 80 s variants k60, p9, unf, two
# and nom never ran, nor L2-L4 (last row 90626), because their hand-set priors sat below the live 5 s members and a label
# that never runs is never re-measured. Each label with under 1 CPU h in round 5 now gets measured: L2, L3, L4 and the
# 80 s variants (about 8 CPU h in all).
# (19 Nov 16:22) ul67: ul66 (17 workers, beside exp32's climber) plus fresh pool runs at 40 s and 80 s right after the
# 5 s level (pool@1:0, pool@2:0; loop.py 902f904), and L2 (the 80 s resume of the 40 s chain run) explored too.
# Since 06:00 (row 103428) L2, L3 and L4 never ran: the ratio order always found a 5 s member at 1-3 per CPU hour above
# L2's prior of 1.1, so the 80-320 s tail and its variants starved. exp32's climber proved 4 heads by 16:19, and its
# plain 160 s control runs proved 3 of them, in 19.6, 40.5 and 75 s, with the pool hints. Production had run 22-24
# fresh 5 s pool runs, 1-4 40 s chain runs and dozens of 5 s members on each, but no pool run beyond 5 s.
# exp30: P2A's 20 s pool level made 35.8 per CPU hour from zero. Each new member gets 1 CPU h under --explore 1.
# (19 Nov 15:39) ul66: ul65 on 17 workers by default, beside exp32's live head climber (abs/clhl2.sh, 2 climbs at a time).
# (19 Nov 13:46) ul65: ul64 on J workers (default 19) plus pw@0, ProofWatch (Goertzel et al. ITP 2018; ENIGMAWatch
# section 2.3, the user's paper of 13:30): each pool hint lists the solved siblings whose proofs contain it, and twee
# --eqhint-watch 0.05 boosts a hint more as its best source proof completes (loop.py 3362943). The 13 Nov test (F = 0.3,
# 345 goals at 8 s) was +2 -4: complementary, never measured as a member. Explored (1 CPU h) like the other 5 s members.
# notes/2026-11-19-enigmawatch.md.
# (19 Nov 12:40) ul64: ul63 plus three more lemma-set members at 5 s, k1000@0 (about 1.2 times a run's cost),
# s40@0 and s200@0 (40 and 200 proven siblings as lemmas, beside the 30 kNN ones), all under --explore 1, and
# --prior-weight 0.5 (hints/exp/estcmp.py: lighter prior weights rank members a little better).
# Also k2000@0 (2-3 times a 5 s run's CPU) and k400 at 80 s, both explored: at 11:10 in ul63 Vk400@0 made 11.5 proofs
# per CPU hour, the best member, after 60, 100 and 200 lemmas had failed.
# (19 Nov 10:17) ul63: ul62 plus hl@0 (loop.py 5fc6b48): the pool plus the proof steps of the goal's 30 kNN lemmas at
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
  --lemmas 6 --lemma-knn 30 --lemma-subsets --lemma-after --twee /project/bin/twee-pg61 --keep-out -j ${J:-17} --reserve 0 \
  --pool original --wall-factor 15 --given-scan /project/hintwork/loops/GFAIL "$@" --line-gaps 80,80 --retry-hints 1.25 --retry-climb --retry-climb-hours 6 --sync 60 --fresh-first --far-retry --mix 0.25 --sched-model /project/hintwork/sched/m4.json --sched-max-lgap 320 --sched-retrain 200 --sched-pmin 0.011 --sched-pmin-auto 400 --retry-knn --knn-refresh 600 --chain-level 1 --chain-records /project/hintwork/chain_records2.tsv --chain-since-row 47530 --variants unf@0,k60@0,k100@0,k200@0,k400@0,k1000@0,k2000@0,kp@0,kd@0,s12@0,s40@0,s200@0,k200s12@0,hl@0,pw@0,m7t@0,m4b@0,m9a@0,m10f@0,m9h@0,m9e@0,r2@0,nopg@0,nom@0,pool@1:0,pool@2:0,sk@0,sk@1:0,skk400s30@1:0,k60,k400,p9,unf,two,nom --variants-after 3 --variant-budget 80 --priors L1=1.73,L2=1.1 --explore 1 --reexplore 150:0.25 --climb-hints /project/hintwork/loops/CLH,/project/hintwork/loops/CLHL,/project/hintwork/loops/CLU,/project/hintwork/loops/CLHL2,/project/hintwork/loops/FUD2p,/project/hintwork/loops/FUDs,/project/hintwork/loops/CLHL3,/project/hintwork/loops/CLHL4,/project/hintwork/loops/CLA67,/project/hintwork/loops/CLB67,/project/hintwork/loops/CLK69,/project/hintwork/loops/K70F,/project/hintwork/loops/K70R,/project/hintwork/loops/CLS71 --prior-weight 0.5 --relabel L1=L2,L2=L3,L3=L4 --relabel-until 103427 --relabel-nostat L2 --ratio-order --head-class --pass-every 1 --ab-args="--cp-renormalise-threshold 1000" --args="--abstract-time 2000 --no-resume-requeue --no-eqhint-consider" > loops/UL79.log 2>&1
echo "UL79: $(tail -1 loops/UL79.log) $(date +%T)" | tee loops/UL79.done

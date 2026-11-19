# Complementary methods: a review of what I dropped, and portfolio approaches (research task)

Started 18 Nov 2026, 17:05 UTC.

## The user's point (17:00)

> "I have a bit of a problem with throwing out complementary methods like you routinely do (now for subsumption
> matching): if one method loses 2 on the best method but adds 3 solutions overall, it's typically better to run
> the two methods in a portfolio for some share of the overall time, than to run just the best method for the whole
> time; could you go over your previous decisions (notes/record) and see where you threw useful complementary things
> out and think about good portfolio approaches? you can make this into another research task"

The user is right. Since 12 Nov I decided almost every A/B by the count of the better arm. The record mostly kept the
+/− numbers, but I read them as noise ("within noise", "neutral", "left off") instead of as the size of the second
method's own share.

The right question for a portfolio is different. For the CPU a second method costs, does it add more new proofs
than the best method would add with that same CPU? The best method could spend it on a deeper level, a repeat,
or more goals.

## Why this matters more for twee than usual

* In abstract time twee is deterministic: identical inputs give identical runs (exp14 reproduced 7 walls
  exactly).
* But the search is chaotic. Any change of setting, hint set, lemma set or prover re-randomises which hard goals
  fall (JOURNAL 5). So nearly every variant has unique solutions, partly from its own merit and partly as a
  perturbation.
* A portfolio gets both. Its value is greatest where the context has stopped changing: stalled goals and the
  tail. There production's retries no longer perturb anything, and the best method run longer does very little:
  * exp5: 0 of 15 at 640 s that had failed at 320 s;
  * ul36's header (16 Nov): the 320 s level made 0.3 proofs per CPU hour.

## Review: decisions with a measured complementary share

Each row gives the best arm's count, the dropped arm's count, its unique gains (+) and losses (−) against the
best, and the union where known.

| where | setting | kept | dropped | dropped arm | +/− | union | decision then |
|---|---|---:|---|---:|---|---:|---|
| 2b | rule-model thresholds and penalties, 345 goals, 8 s | 69 | the other settings | 65-67 | | **93** (of all variants) | best setting only |
| 2b | ProofWatch (F = 0.3), 345 at 8 s | 69 | ProofWatch | 67 | +2 −4 | 71 | dropped |
| 2f | rm4b, 4 times the model, 345 at 8 s | 61-63 | rm4b | 65 | +9 −7 | about 72 | not worth the load time |
| 2f | rm5, retrained on hard proofs | 61-63 | rm5 | 58 | +2 −7 | about 65 | rm4 stays |
| 2g | chained sketches, 20 s | 28 | sketches | 29 | +2 −1 | 30 | "within noise" |
| 2s | frequent hints as axioms, nil3_31 at 20 s | 76 | 10 / 45 axioms | 72 / 73 | +1 −5 / +3 −6 | 77 / 79 | dropped |
| 2u | ENIGMA retrained online (EHL) against fixed (FHL) | 987 | EHL | 971 | 3 only in EHL, 19 only in FHL | 990 | fixed model |
| 2ab | sketch-climb arms against fresh runs, 32 stalled | 8 | CL2-CL4 | 4-6 | | **9** of 32 | climbing as a filler |
| 2ac | learned scheduler A/B 1 (two arms) | | | | only 30 proofs common at 29 min | 255 | the winner only |
| 2af | unfolded definitions (stalled goals, 20 s) | 2 of 9 | unfolded | 7 of 9 | | | side worker; stopped 15 Nov 15:17 at 0-1 per 24-goal cycle |
| 2ad/2af | Prover9 side worker with the pool | | Prover9 | 9 of 283 | goals twee failed | | replaced by the unfolded worker |
| 2am | kNN lemma selection, 150 goals at 20 s | 6 | use counts / MaSh | 7 / 5 | +3 −2 / +1 −2 | **10** distinct | plain similarity |
| 2am | 60 kNN lemmas against 30 (two tests) | 19 of 450 | 60 | 17 | +4 −1, +1 −3 | 24 | 30 |
| 2ap | hints from kNN lemmas' proofs, 150 at 20 s | 6 | F = 0.1 / 0.01 | 5 / 5 | +1 −2 each | 7-8 | dropped |
| 2an | live head climber | | | 4 of 55, 0.47 per CPU h | | | stopped: production then made about 4 per CPU h; now it makes about 1 |
| 2au | --orig-rate, 2 h on half of the benchmark | 18,319 | ORB | 18,228 | its 80 s runs proved 58 against 37 | | off |
| 2aw | expansion hints in production's setting, 20 s | 86 | expansion | 90 | +7 −3 | 93 | "not adopted" (it was ahead) |
| 2ax / exp7 | subsumption matching, 200 hard goals at 20 s | 87 | --eqhint-subsume | 87 | +2 −2 | 89 | off |
| exp3 | deep arms at 320 s, 47 late goals | K 12 | C, E, V | 9, 10, 4 | V: aK2_eq_aK3_q 211 only | 13 | K |
| exp8 | chain against pool at 80 s, 78 stalled | chain 9 | pool | 5 | pool +2 | 11 | chain |
| exp10 | transfer-filled chain, same 78 | 9 | X | 7 | +1 −3 | 10 | off |
| exp13 | 5-sibling chain / no expansion, same 78 | 9 | S5 / D | 7 / 4 | +1 −3 / +1 −6 | 10 / 10 | full chain |
| exp14 | two-sided chain, 107 walls at 80 s | 15 | T | 16 | +4 −3 | 19 | "no production change" |
| exp16 | Prover9 + chain / + pool, 107 walls at 60 s | twee 15 | Q / P | 4 / 2 | 3 / 1 not twee's | 19 | P9C side worker (kept) |
| exp18 | subsumption matching, 107 walls at 80 s | 15 | SU | 13 | +3 −5 | 18 | "not in production" |
| exp15 | unfolded + chain, 107 walls at 80 s | 15 | U | 5 of the first 51 failed walls | +5 so far | | running |

Genuine negatives, where the variant added nothing new:
* the 20 s portfolio of orderings, rule settings and lemma counts on stalled goals (2ac: every variant proved the
  same single goal);
* the tail-head probes (2ag: 0 of 30);
* `--hint-goal` (2aj: the same 3 proofs);
* chain hints at 5 s (exp9: 0 against 0).

These are the only cases where dropping was clearly right.

## The comparison that was missing

* **The walls so far.** Ordered greedily by new proofs per CPU hour:
  * exp11 (twee chain): 15 at 4.8 CPU h;
  * then Prover9 + chain: 18 at 6.6 h;
  * then Prover9 + pool: 19 at 8.3 h;
  * then the two-sided chain: 22 at 14.0 h;
  * then subsumption: 24 at 21.9 h;
  * unfolded's 5 or more come on top.
* **What I don't have:** the control given the same extra CPU. For that, exp20 runs exp11's commands at 160 s
  on the 92 failed walls. Twee is deterministic in abstract time, so exp11's 15 are proved again and only the 92
  need running.
* **Weak comparisons I do have:**
  * exp5: 320 → 640 s, 0 of 15;
  * exp12 B: 80 → 320 s on gap heads, 2 of 30 by 17:01.

## Portfolio approaches to test

1. **Variant levels instead of a longer run.** Production's cascade is 5 s pool, then 80 s chain, then 320 s.
   Replace or share the 320 s level with a rotation of 80 s variants, each tried once per goal and context:
   * Prover9 + chain (60 s);
   * unfolded + chain;
   * the two-sided chain;
   * subsumption matching;
   * 60 kNN lemmas;
   * the pool at 80 s.
   The order comes from their measured new-proof yields on goals that every earlier member failed.
2. **Shares by online yield.** The mix scheduler already estimates proofs per worker hour for its classes (r, f,
   d). Variants become classes too, so each gets workers in proportion to its recent yield of new proofs: a
   bandit over methods, not only over goals.
3. **Side workers for the different provers.** Prover9 + chain (running since 16:46) and unfolded twee, each on
   2 CPUs, on twee's stalled goals. Proofs go into UL, where they become context for everything else.
4. **Short-level portfolios:** the rule-model settings (2b's union of 93 against 69) and kNN selections (10
   against 7). At short budgets production already perturbs through changing contexts, so these probably matter
   less. To check on a replay (rp3, 2aq).

## Plan

1. exp20: the control at 160 s on the 92 failed walls (after exp17, when 4 CPUs are free).
2. When exp15, exp17 and exp19 end: the full union curve on the walls, greedy against exp20's time-matched control.
   Also the per-variant yield of new proofs on goals all earlier members failed.
3. loop.py: variant levels (approach 1) with per-variant yields in the mix scheduler (approach 2). Then
   production, watched against ul46's rates.
4. Correct the record: JOURNAL section 5 ("Neutral or negative") and REPORT 2d's "What did not help" list
   complementary methods as such, with their unique share.

## Production yields at the time (17:12)

From UL r5's results since row 47530 (ul44's start, 12:02):

| level | runs | proofs | CPU h | proofs per CPU h |
|---|---:|---:|---:|---:|
| L0 (5 s) | 7,928 | 192 | 17.0 | 11.3 |
| L1 (80 s chain, fresh) | 655 | 40 | 34.5 | 1.16 |
| L2 (320 s) | 0 | | | |

* ul46 (14:46 to 17:13, 4 workers) proved 12 in 2.4 hours. Its mix line ended "r 1250 6/h f 1402 1/h d 51 1/h", so the
  deep class ran on about one worker, and the 320 s level never ran.
* So a variant level competes with the far retries (1 per worker-hour) and the chain level, not with the 320 s level.

## Variant yields on the failed walls (17:10)

New proofs among the 92 walls exp11's chain run failed:

| variant | runs on failed walls | new | CPU h | new per CPU h |
|---|---:|---:|---:|---:|
| k60: 60 kNN lemmas (exp17) | 90 | 6 | 4.7 | **1.27** |
| two: two-sided chain (exp14) | 92 | 4 | 5.2 | 0.76 |
| unf: definitions unfolded (exp15, running) | 58 | 6 | 9.8 | 0.61 |
| sub: subsumption matching (exp18) | 92 | 3 | 7.2 | 0.42 |
| sj: --set-join (exp19, running) | 10 | 0 | 0.6 | |

All four are near production's own L1 yield (1.16), and each proves walls the others do not.

## Deployed: variant levels (17:13)

**loop.py `--variants LIST`** (commit 551f563):
* Levels of the chain level's budget (80 s) are inserted after it, one per variant.
* Each is a fresh run in the same context, keeping no state. So the 320 s level still resumes the chain run's state.
* Results rows are labelled `V<name>`. The cascade's own levels keep `L<k>`, so earlier results map onto the same
  levels on restart. schedfeats reads V rows as deep rows.
* The deep queue sorts by level. So every waiting goal gets its first variant before any goal gets its second:
  breadth first over the variants, in the order given.
* Variants available:
  * `k60`: 60 kNN lemmas;
  * `two`: two-sided chain;
  * `unf`: all definitions unfolded, the hints too;
  * `sub`: `--eqhint-subsume`;
  * `sj`: `--set-join`;
  * `pool`: the original's pool at 80 s.

**Smoke test** (cascade 2,4,8 on 3 unsolved walls):
* The levels ran in order: L0, L1, Vtwo, Vunf, Vsub, Vsj, Vk60, Vpool, L2.
* The commands differ as intended: the .u.p problem for unf, the flag for sub and sj, no state for the variants,
  and L2 with `--load-state` and the 4 s increment.

**Production ul47** = ul46 + `--variants k60,two,unf,sub`, in the order of the wall yields (abs/ul47.sh,
hints/exp/portfolio_ul47.sh). Started 17:13:49. Startup: 364 level updates against ul46's 372.

**Measure:** the V rows' proofs per CPU hour, against L1 and f in the same period, and how many proofs each
variant adds that the chain run had missed (all of them, by construction).

## Design principle: the ratio rule (17:49)

For one goal, independent attempts with success chances p_i and costs c_i are best tried in decreasing order of
p_i/c_i. This is the classic rule for optimal sequential search: it minimises the expected cost to the first
success. Over many goals and a fixed CPU budget, the same greedy order maximises expected proofs.

Here p_i is the chance that member i proves a goal **that every earlier member failed in the same context**. So
p_i/c_i is that member's yield of new proofs per CPU hour on that population. That is the number to rank by, not
its count against the best method.

Measured at 17:49 (walls: the 92 that exp11's 80 s chain failed; production: UL r5 12:02-17:13):

| member | population | n | proved | p | CPU s a run | new per CPU h |
|---|---|---:|---:|---:|---:|---:|
| L0, 5 s fresh run in a new context | production | 7,939 | 192 | 2.4% | 7.7 | **11.3** |
| Prover9 + chain, 60 s (exp16) | failed walls | 92 | 3 | 3.3% | 59 | **1.98** |
| Vk60 (exp17) | failed walls | 92 | 6 | 6.5% | 189 | 1.24 |
| L1, 80 s chain, fresh | production, after L0 failed | 656 | 40 | 6.1% | 190 | 1.16 |
| chain to 160 s (exp20, 12 so far) | failed walls | 12 | 2 | 17% | 546 (fresh) | 1.10 (on the full cost) |
| Vtwo (exp14) | failed walls | 92 | 4 | 4.3% | 205 | 0.76 |
| Vunf (exp15, 71 so far) | failed walls | 71 | 6 | 8.5% | 621 | 0.49 |
| Vsub (exp18) | failed walls | 92 | 3 | 3.3% | 282 | 0.42 |
| L2, 320 s chain on gap heads (exp12 B) | heads | 34 | 3 | 8.8% | 1,540 | 0.21 |

* The 5 s fresh run in a changed context is ten times the rest. That is why the mix scheduler's r class takes
  most of production's workers, rightly.
* Among the deep members, the ratio order is:
  * Prover9 + chain (a side worker);
  * then 60 kNN lemmas, about level with the chain level itself;
  * then the two-sided chain, unfolded, subsumption;
  * and the 320 s level last.
  ul47's variant order (k60, two, unf, sub, then L2) is this order.
* **Extending to 160 s** may rank near the top. In production it would resume the 80 s state, so its cost is the
  increment, about 546 − 190 = 356 s a run. With 2 of 12 that gives about 1.7 per CPU hour (early).
  * exp20 decides this. If it holds, the portfolio gets an 80 → 160 s resume level before the variants, in place
    of jumping to 320 s.
* Unfolding has the highest p (8.5%) but costs three times as much a run. Unfolded problems are larger and
  slower.
* **Next in the loop:** order the deep queue by estimated p/c per (goal state, member), not by level. Estimate p
  online per member from production's own V rows (a Beta-Binomial over the member's runs on goals that failed
  everything before it). The mix classes are a coarse version of this.

## Conditional yields (18:50, an independent check of the priors)

In production the 80 s members run in sequence. So each later member only gets credit for walls every earlier
member failed: its yield conditional on the earlier failures, not alone. On the 92 walls exp11 failed, in ul48's
order:

| member | new alone | new after the earlier members | runs | CPU h | conditional per CPU h |
|---|---:|---:|---:|---:|---:|
| k60 | 6 | 6 | 92 | 4.83 | 1.24 |
| two | 4 | 3 | 86 | 4.98 | 0.60 |
| unf | 7 | 7 | 83 | 14.55 | 0.48 |
| sub | 3 | **1** | 76 | 6.19 | **0.16** |

All four together prove 17 new walls. With Prover9 + chain first, 18 (k60 then adds 5, at 1.06).
* **Subsumption matching is nearly covered by the others.** After them it adds 1 at 0.16 per CPU hour, below the
  320 s level (0.21). Its standalone 0.42 overstated it.
* The two-sided chain falls to 0.60. 60 kNN lemmas and unfolding are hardly covered.
* So **a member's prior must be its conditional yield in its position**, and every new member should be measured
  after the members before it. loop.py's priors are corrected (YP: Vtwo 0.60, Vunf 0.48, Vsub 0.16; at the next
  restart).
* sub stays in the list, but `--ratio-order` ranks it last. Most of its runs will wait while anything better is
  queued.

## Results and actions (running record)

* **17:13: production ul47**, variant levels k60, two, unf, sub after the 80 s chain level (above).
* **17:16: exp17 final.** 60 kNN lemmas at 80 s on the walls: 17 against the control's 14 (+7 −4), union 21. It
  is the best twee variant per CPU. 4 new proofs merged.
* **17:24: exp12 stage B paused** at 34 of 95 heads. It made 3 proofs at 0.21 per CPU hour, the weakest member
  per CPU. Its 4 workers went to exp21.
* **exp21** (5 s variants on 300 goals that failed their 5 s fresh run): **one proof in 1,521 runs** at 169 goals
  (unfolded, aK2_eq_aK3_t 374). At the cheap level, on goals whose context has not changed, no variant pays. The
  portfolio's value is at the deep level, where the walls show 3-7 unique proofs a variant. Final numbers:
  notes/2026-11-18-l0-portfolio.md.
* **Queued:**
  * exp22: no PG / no rule model at 80 s on the walls, after exp21;
  * P9C to 4 workers when exp21 ends (abs/p9c4.sh: the best deep member live, 1.44 per CPU hour).
* **18:30: ul48** (6 workers): `--variants unf@0,k60@0,k60,two,unf,sub --ratio-order`. Every goal whose fresh run
  failed gets the unfolded and the 60-lemma 5 s runs. Over its 22 minutes the deep class made 6 proofs per
  worker-hour (5 new in all).
* **18:47: exp15 stopped** after the 92 failed walls: 7 new at 0.43 per CPU hour.
* **18:50: the conditional yields** (above). The priors were corrected.
* **18:53: ul49**: an 80 -> 160 s resume level right after the chain run, from exp20's interim (6 new on 44 failed
  walls at 1.52 per CPU hour on the increment; 1 overlap with 60 kNN lemmas' 4). Also `--pass-every 1`.
* **19:09: P9C's yield has fallen.** Its first 126 runs (from 16:46) proved 3. On 4 workers since 18:26 it made 0 in 172
  runs (2.9 CPU h). It takes the nearest goals first, so the best candidates came early; its conditional yield is
  now near 0. Its 4 CPUs go to production at the next restart.
* **Unfolded 5 s level in production:** ul48 3 of 190, ul49 0 of 160 in its first 13 minutes. That is 3 in 350
  (0.9%) at 2.5 per CPU hour, still above L1 (1.16), and `--ratio-order` follows it online.
* **19:20 check:**
  * P9C on 4 workers since 18:26: 1 proof (aK2_eq_aK3_j 425) in 217 runs, 0.28 per CPU hour.
  * The unfolded 5 s level since 18:30: 3 in 390 runs, 2.15 per CPU hour. All 3 were in its first 142 runs.
    Within a level the queue takes the goals nearest a proof first, so its rate falls as it moves to harder goals
    (exp21 sampled all such goals, so its 1.3% is the average). The online estimate follows.
* **19:37: exp22 G80** (no PG): 2 new of 92, 0.43 alone, about 0.22 after the 80 s variants. Added last as `nopg`.
* **19:39: ul50**, 10 workers. P9C stopped and its 4 CPUs moved to production. ul49 made 8 new in 43 minutes on
  6 workers.
* Merged at 19:38: exp22 1, exp20 5 (the 160 s proofs so far).
* **20:13: exp20 complete.** 12 of 92 at 1.77 per CPU hour on the increment. After it: k60 1.19, unf 0.47, two 0.23,
  sub and nopg 0 (notes/2026-11-18-time-matched-control.md).
* **20:15: ul51**, 16 workers, variants k60, unf, two after the 160 s level.
* **20:25: the unfolded level was prep-bound.** ul51 had 15 runs in flight but only 1-3 twee processes. 13 of its 16
  threads waited on the GIL, and the loop process used 104% CPU in user mode.
  * Each unfolded run unfolded its hints in Python: 19-29k pool hints at 0.25 ms each, 5-6 s a run, serial
    across the threads.
  * ul51 managed 58 unfolded 5 s runs in 7 minutes (0.14 a second). ul48-ul50 were limited the same way, by less
    because they had fewer workers.
  * The level's yield per twee CPU hour is still right. Its real cost was higher by the loop's prep, about as much
    again.
  * Fix (loop.py a5949d1): unfolded hints are memoised per definition set. A second goal of the same original
    takes 0.02 s instead of 3.5 s, with identical output.
* **20:27: ul52** = ul51 with the fix.
* **20:34: ul52's throughput** was 400 runs, 5 new, in 6.6 min (ul51: 50 runs in the same time).
* **20:38: stopping P9C was a mistake of the kind under review.** I judged it on its last 217 runs (1 proof). Split by
  what the goals had failed in production, its 487 live runs since 16:46 were:
  * 4 proofs in 350 runs on goals that had failed the 160 or 320 s level, about 0.7 per CPU hour;
  * 6 proofs in 121 on goals that had failed only the 80 s level.
  * After the 160 s level that is above unf (0.47) and two (0.23). The decline came from its nearest-first list,
    which it had exhausted, not from the method.
  * So Prover9 + chain is now a cascade level: `--variants p9` (loop.py bc450f8, p9twee.P9 with the level's chain
    hints, 60 s, 6 siblings either side, prior 0.7). It gets each goal once per context, after k60.
* **20:35: ul53** = ul52 with `--variants unf@0,k60@0,k60,p9,unf,two`.
* **21:20: exp22 N80** (no model): 4 new of 92 alone (0.72), 1 after the others (0.23). It goes in as `nom`, last.
  With Prover9 + chain in the order, its conditional yield on the walls is 1.62, second only to the 160 s run.
* **21:21: ul53 after 46 min:** 3500 runs, **new=53** on 16 workers (about 69 an hour; ul49-ul51 made 10-14).
  With the unfolding bottleneck gone, the queue is still on the 5 s levels:
  * L0: 24 in 1476 runs, 6.1 per CPU hour;
  * unfolded 5 s: 29 in 2057 runs, 4.0 per CPU hour.
  * The 80 s levels wait until these fall below their yields.
* **21:35: ul53 ended at new=56 in 60 min.** Only 3 came after 21:21, so the 5 s levels were close to exhausted.
* **21:36: ul54**: 19 workers, `nom` last before 320 s.
* **22:35: ul54 after an hour:** new=28. By level:
  * L0: 10 in 1799 runs, 2.2 per CPU hour;
  * **60 kNN lemmas at 5 s: 14 in 1588 runs, 5.5** (prior 1.9);
  * unfolded 5 s: 4 in 3064 runs, 0.39, used up.
* **The ordering problem:** the ratio rule chose which goal ran next, but each goal's levels were in a fixed order.
  So every goal had to run the used-up unfolded level before the 60-lemma one.
  * A restart with the order swapped would not help. Replay keeps only a goal's highest tried level, so about 3,500
    goals that had run unfolded would skip the 60-lemma run.
* **Fix: tiers** (loop.py a0a4486).
  * The variants after one cascade level form a tier, and a goal tries them in any order. With `--ratio-order`, the
    next is the untried one of highest current yield.
  * The goal passes the tier when it has tried all of them. Replay records tried variants per goal.
  * Smoke tests: the 80 s tier ran k60 (1.19) before two (0.23) although the list names two first. A restart after
    L0 and Vunf@0 continued with Vk60@0, then the rest.
  * This is the Simon-Kadane order (decreasing p/c) per goal as well as across goals.
* **22:39: ul54 ended at new=37 in 63 min. ul55** = ul54 with tiers.
* **23:40: ul55's first hour: new=146 in 61 min**, four times ul54 (37) and the best production hour so far
  (ul53 56). By level since its restart (levyield.py from results row 70875):
  * L0: 108 in 2799 runs, **17.5 per CPU hour**. Most of these came from goals reopened by new sibling proofs (the
    mix's r column ran at 15-67 an hour). Each new proof gives its neighbours a new context and a fresh 5 s run.
  * 60 kNN lemmas at 5 s: 8 in 3910 runs, 1.29 (5.5 in ul54's hour). The tier took it first, while it was the best
    5 s variant, and it is now near the 80 s level's prior (1.16).
  * Unfolded 5 s: 30 in 1667 runs, **6.2** (0.39 in ul54). Not checked yet, but probably because its runs now
    come on reopened goals and after the 60-lemma run: a different, conditional population.
  * No 80 s or deeper level ran yet: the 5 s levels still pay more.
  * The proofs are spread over many originals: aK2_eq_aK3_s 22, aK2_eq_aK3_gen 15, nil3_30 12, then nil3_* by 4-7.
  * Solved at 23:41: 45,901 distinct goals, holdout 5043. Memory 1.4 GB.
* **Reading:** with the order per goal set by yield, a cheap level is tried again when it pays, and is not
  pushed through when it doesn't. The per-level numbers change within the hour, so fixed priors would have ordered
  them wrongly twice already. Online conditional yields do the work.

## Optional attempts and the replay (18 Nov 23:45 - 19 Nov 00:00)

**What is still unexplored.** At 23:45, 3,514 of the 5,882 unsolved goals had never had a run longer than 30 CPU s.
Only goals near the frontier may deepen (`may_deepen`). The others get only the 5 s level and its variants. Recent
80 s chain windows paid 0.8-1.5 per CPU hour, which matches the 1.16 prior, while reopened 5 s runs paid about 17. So
the ratio rule rightly keeps the deep levels waiting for now.

**Which 5 s variants to add?** None of the search settings. exp21 measured them on 300 goals whose context had not
changed since a failed 5 s run:
* subsumption, rule threshold 0.2, no model, no PG, chain hints and Prover9 at 8 s: 0 each;
* only the variants that change the problem paid: unfolding 4, 60 lemmas 1.
So these are genuine negatives by the portfolio rule, since they prove nothing new.

**Two defects in loop.py, fixed in 119c3d1:**
1. **Tiers blocked.** A goal had to try every variant after a level before its next level. A variant that had stopped
   paying (60 lemmas at 5 s: 5.5 in ul54's hour, 1.3 in ul55's, against 1.16 for the 80 s level) would hold back the
   goal's 80 s run.
   * Now variant levels are optional attempts. A goal's next attempt is its eligible option of highest live yield: the
     next cascade level, or any untried variant after a level it ran. Only the cascade's own levels stay ordered,
     because a resume needs the state of the level before it.
   * A goal far from the frontier chooses among the fresh level's variants only. My first version filtered on the
     chosen level alone, which would have dropped such goals entirely when their 80 s level ranked first. I caught
     that while designing the smoke test.
2. **Replay forgot reopened goals.** After a restart a goal counted as tried up to the highest level it reached in the
   whole round. Context was ignored, and later fresh runs did not reset it. At 23:45, 892 unsolved goals had deeper
   runs only before their latest fresh run, so after each restart they had lost their deeper levels in the new
   context.
   * Now every results row records its context (`c=`, a hash of the goal's proven-sibling context at dispatch).
   * Replay skips rows of another context and starts a goal's attempts over at each fresh run.
   * Rows before 23:59 have no `c=`; for them the reset at fresh runs applies.

**Smoke test** (hints/exp/optvar_smoke.sh; 3 nil3_15 goals, cascade 1,2,4,8, scratchpad opt1):
* Order by yield: L0, unf@0 (3.8), k60@0 (1.9), L1, L2, then k60 (1.19) before L3 (1.0 at these budgets), then unf
  (0.47) and two (0.23).
* Restart with all rows current: 0 runs.
* Rows of an older context: a fresh run, then every level again.
* A fresh row after deep rows: every level after L0 again.
* One variant row removed: only that variant ran.
* Far goals (`--frontier 0`, line gap above F): L0 and the two 5 s variants only.

**00:00: ul56** = ul55 with these fixes. ul55 ended at 10,350 runs, **new=184 in 80 minutes**.

**01:05: ul56's first hour: new=90** (ul55's first hour 146). By level since its first row (81268):
* L0: 63 in 2393 runs, 11.4 per CPU hour;
* 60 kNN lemmas at 5 s: 19 in 3737 runs, **3.2** (1.3 in ul55's hour);
* unfolded 5 s: 8 in 2177 runs, **1.2** (6.2 in ul55's hour);
* L2: 5 runs, 0.
* ul55 and ul56 ran about the same number of reopened 5 s runs (1148 against 1177), but ul56's proved fewer. The
  supply varies: ul55's burst was in a few nil3 and aK2 originals.
* By 01:03 the 5 s classes paid little (r 5 an hour, d 0), and the 80 s chain runs began on all workers. Memory rose
  to 22.8 GB, about 2 GB per 80 s run. memwatch caps the total at 45 GB.
* The fresh-run predictor overpredicts in ul56: 63 proved against 103 predicted (ul55: 108 against 113).
* Solved at 01:06: 46,050 rows in solved.tsv.

**03:50: ul56 at 3 h 50 min: new=233** (about 60 an hour). By level since row 81268:

| level | runs | proofs | CPU h | per CPU h |
|---|---:|---:|---:|---:|
| L0 (5 s) | 6,195 | 145 | 14.3 | 10.1 |
| L1 (80 s chain) | 380 | 40 | 24.9 | **1.61** |
| L2 (160 s resume) | 30 | 0 | 1.7 | 0 |
| Vk60 (80 s) | 30 | 1 | 1.2 | 0.82 |
| Vk60@0 (5 s) | 7,073 | 29 | 11.2 | 2.59 |
| Vunf@0 (5 s) | 5,236 | 20 | 16.2 | 1.24 |

* A burst at about 03:15 (new 168 to 199 in a few minutes, the r class at 59 an hour): one deep proof reopens its
  neighbours, and their fresh 5 s runs prove more.
* Memory 8 GB, no memwatch kills. Solved: 46,207 rows.

## Far goals and two loop.py fixes (19 Nov 03:50 - 04:08)

**Far goals, the unmeasured member.** 4,176 of the 5,588 unsolved goals are far from the frontier, and 3,683 of them never
had a run over 30 CPU s, because production never deepens them. exp24 (notes/2026-11-19-far-goals-deep.md) runs
production's L1 on 40 of them. exp23 (Veroff's Prover9 settings) is paused to free its CPU: max_weight 5 proved 0 of 107,
a genuine negative, and max_weight 40 had 0 of 39.

**`--far-deep K`** (loop.py 5f8fd4a, off in production): far goals may also take the cascade's own levels 1..K. Their
yield is counted apart as `L<k>f` (rows get a column `f=1`; levyield.py shows them), so the ratio rule ranks a far goal's
80 s run by far goals' own record, from a prior `--far-deep-prior` (default 0.5). Smoke test (hints/exp/fardeep_smoke.sh):
far goals ran L0, Vunf@0, Vk60@0, then L1 marked f=1, and nothing deeper. A restart made 0 runs. Without the flag, far
goals got the 5 s levels only, as before. exp24's result sets the prior, or keeps the flag off.

**Bug 1: chain records race at the start.** The chain records load in a background thread. Deep runs dispatched before
they were in got the original's pool instead of the chain (exp24's first launch: 3,113 and 10,573 hints against chains
of 7,738 and 3,631). Now such a level waits for the records, for up to 2 minutes (2b5d7d8). At production restarts most
early runs are 5 s fresh runs, so few deep runs were hit.

**Bug 2: spurious pool growth at a restart (the larger one).** At a restart `--retry-hints` estimates each goal's pool size
at its last fresh run from the hints= of that run and of the original's latest run. The latest run could be a deep or
variant run, whose hints= counts its chain, 60 lemmas' or unfolded hints, not the pool. The pool then looked grown by
1.25x, and the goal got a fresh 5 s run in an unchanged context. That run resets the goal's attempts, so all its 5 s
variants and deep levels ran again, and twee is deterministic, so they failed again identically.
* Past restarts: ul45 flagged 970 goals, ul46 3,142, ul47 265, ul48 527; ul49 to ul56 0 (their originals' latest rows were
  fresh runs). A restart now would have flagged about 2,553 of the 5,583 unsolved goals, since the deep phase wrote
  most originals' latest rows.
* So part of ul45-ul48's runs repeated themselves, and their yields per CPU hour are understated by that.
* Fix: both sizes from fresh (L0) rows only (5f8fd4a). The smoke test's restart went from 12 repeated runs to 0, and
  production's current results would flag 1 goal.

## A 40 s chain level: splitting the 80 s run (19 Nov 05:45 - 06:03)

**The data.** ul56's 833 L1 runs (80 s chain, fresh) from row 81268: 81 proofs, 752 failures at 259 CPU s each. The
proofs' abstract times (considered pairs / 2,000, from their kept outputs) have quartiles 13, 29 and 46 s:

| within | 20 s | 40 s | 60 s | 80 s |
|---|---:|---:|---:|---:|
| proofs | 28 | 50 | 73 | 81 |

**Why this is exact.** Twee is deterministic in abstract time, so a 40 s run is the first half of the 80 s run: it
proves exactly the 50, and a resume to 80 s proves the other 31. The CPU of a failing run grows about in proportion to
its abstract time (36 s at 20 s against 135 s at 80 s on one wall).

| first deep level | proofs | CPU h (est.) | per CPU h |
|---|---:|---:|---:|
| 80 s (ul56) | 81 | 55.8 | 1.45 |
| 40 s | 50 | 28.9 | **1.73** |
| 20 s | 28 | 15.8 | 1.77 |
| then 40 -> 80 s resume | 31 | 28 | 1.1 |
| or 20 -> 80 s resume | 53 | 42.6 | 1.24 |

* A shorter first level pays about 20% more per CPU hour, and the second half becomes a member of its own at about
  1.1, level with the 80 s variants (k60 1.19, p9 0.7). The ratio rule can then run another goal's first half before
  finishing this one's.
* 40 s rather than 20 s: the same rate, half the resume overhead per proof, and states stay small. 20 s would add a
  third resume (20 -> 40 -> 80) for about the same rate.
* That is the cascade's own portfolio question: a level's members are "the first half" and "the second half", and
  the second half competes with the variants.

**Deployed as ul58** (06:02, loop.py 1bb0a0f): `--cascade 5,40,80,160,320 --variants-after 3 --variant-budget 80
--priors L1=1.73,L2=1.1 --relabel L1=L2,L2=L3,L3=L4 --relabel-until 103427 --relabel-nostat L2`.
* Old rows count as the levels of the same budget (an old 80 s run is the new L2, and its state resumes to 160 s).
* The old fresh 80 s rows do not count in the new L2's yield, since that is now a resume.
* Smoke test (hints/exp/relabel_smoke.sh, cascade 1,1.5,2,4,8 after 1,2,4,8): goals with old deep rows went on from the
  right level with the right increments, and a goal without one ran the new first level fresh.

## Lemma-set variants at 5 s: the dropped selections back as members (19 Nov 07:35-07:56)

**Which dropped methods qualify.** exp21 (18 Nov) found that at 5 s only the variants that change the problem pay:
unfolding (4 of 300) and 60 kNN lemmas (1). Live in ul58/ul59 the 60-lemma 5 s variant makes 8.4 proofs per CPU hour.
The review table above lists three other lemma selections that 16 Nov dropped as "not better on count"
(notes/2026-11-16-knn-lemma-count.md, 150 unsolved goals at 20 s):

| selection | proved | against plain similarity (6) |
|---|---:|---|
| use counts (`--lemma-pop 0.3`) | 7 | +3 −2 |
| proof dependencies, MaSh-style (`--lemma-deps 1`) | 5 | +1 −2 |
| 100 kNN lemmas | 5 | +1 −2 |
| (60, already a variant) | 9 | +4 −1 |

All three change the lemma set, so they fit the class that pays at 5 s.

**loop.py 92d60c4.**
* `--variants kN` takes N kNN lemmas (k60 as before).
* `kp` weights similarity by lemma use counts. `kd` adds proof dependencies.
* kp's and kd's indexes are shallow copies of the base index, with their own scoring. A background thread builds
  them at each index rebuild: on UL the use-count grep takes about 100 s and the dependencies about 20 s, too long
  for the main loop. They are eligible only once built.
* On three UL goals, kd changes 2-10 of the 30 lemmas and kp 3-12. Smoke test: hints/exp/lemmavar_smoke.sh.

**To deploy** with production's restart back to 19 workers after exp27 (about 09:18):
* `--variants unf@0,k60@0,kp@0,kd@0,k100@0,...` with priors Vkp@0 = Vkd@0 = Vk100@0 = 3. That is about Vunf@0's live
  yield, so each gets about 2 CPU hours of runs before its own yield decides.
* At a lower prior they would never run: some goal always has a k60@0 option at 8.4.
* Cost if they are worthless: about 6 CPU hours of 5 s runs.

## Are restart bursts a scheduler defect? No (19 Nov 07:56-08:03)

**The worry.** ul58 made 177 new in 74 minutes, and ul59 198 in its first 33 minutes on 12 workers. Fresh runs proved
8.8% in ul59 against 5.1% in ul58 and 2.3% over ul56. 67 of the goals ul59 proved at the 5 s level had been last run in
ul56, and had their current sibling context already at ul58's start. So ul58 had them as candidates and did not run
them in 74 minutes. A restart that does better than the running loop would point to a defect.

**Checked and ruled out:**
* *Stale scores.* The scheduler's features (`orate`, `nfail`) change with every run in an original. The score cache
  is keyed by `over[o]`, but loop.py increments that after every observed run, not only after proofs.
* *Proofs synced from other processes.* They go through `add_proof`, which clears the context cache.
* *The threshold.* `--sched-pmin-auto` counts every non-fresh run as a "resume", the cheap 5 s variants too, which
  inflates it (0.12-0.17 at the starts of ul58 and ul59). But in ul58 it had fallen to 0.003-0.02 from t = 1,500 s,
  and new proofs stayed flat (20-30) until t = 3,000 s.

**What happened.** ul58's proofs came late, not early:
* 40 new by t = 3,413 s;
* then 129 in its last 16 minutes (from about 06:59), and ul59 went on with it.

The cascade was spread over many originals (aK2_eq_aK3_d 21, aK2_eq_aK3_1243b 20, aK2_eq_aK3_c 18, nil4_19K 16, ...):
* 299 of its 361 proofs were 5 s fresh runs and 47 were Vk60@0.
* It began about two minutes before a kNN index rebuild (t = 3,556 s).

So the bursts are cascades of real proofs, not restart artefacts. "A restart's first hour" is not a fair window for
comparing settings. **Cross-original lemmas spread cascades.**
* Of the 401 proofs from ul58's start to 08:05, 392 used a kNN lemma of another original. Their kept outputs name
  the lemmas: `lemma_knn_<i>_<source goal>`.
* For 171 of them, the youngest such lemma was proved within the last 30 minutes, and for 64 within 10 minutes. The
  median is 48 minutes. These ages come from the hints files' mtimes, which proofs rewritten later make younger.
* The index is rebuilt every 30 minutes or 300 proofs, so a new lemma waits about 15 minutes on average before
  another original's goals can see it. A rebuild takes about 1 s.
* So ul60 gets `--knn-refresh 600`. It is not measured separately: production's cascades are too noisy for that, and
  a clean test would be a from-zero pair.

**ul60's first 45 minutes (08:05-08:50): the new variants hardly ran.** Vkp@0 7 runs, Vkd@0 8, Vk100@0 9, no proofs;
Vk60@0 2,201 runs (8.5 per CPU hour).
* The deep queue is one sort by each goal's best option. New Vk60@0 options appear with every failed fresh run, so a
  variant whose estimate is below Vk60@0's live yield never comes up.
* A prior is then a decision to measure, not only a belief. ul61 (the restart on 19 workers after exp27) sets their
  priors to 9.
* If one of them yields about 1, its estimate falls below Vk60@0's within 2-4 CPU hours, about 3 CPU hours of 5 s
  runs for all three.
* The general form of this is exploration in the ratio rule. With one global sort and optimistic-free estimates, a
  member is measured only if its prior beats the best live member. A candidate mechanism is `--explore H`: a label
  with less than H CPU hours of runs in the round is estimated at max(its estimate, the best label's). Every member
  then gets H CPU hours before its own yield decides. exp27's from-zero run shows the same starvation: its 40 s
  chain level ran 4 times in an hour behind Vunf@0 (50 per CPU hour there).
* **Built (loop.py 3f95f59, 09:24): `--explore H [--explore-labels L,...]`.** A label with less than H CPU hours
  of runs in the round is estimated at max(its own estimate, the best estimate among labels with H or more). The best
  is recomputed only when the stats change. Ties go to the lower internal level.
  * Smoke test: hints/exp/explore_smoke.sh.
  * ul62 uses it for the lemma-set variants (`--explore 1 --explore-labels Vk100@0,Vk200@0,Vkp@0,Vkd@0,Vs12@0`),
    with two more of them: k200@0 and s12@0 (12 sibling lemmas; loop.py e2986e3, variants `kNsM`).
  * Measured-prior members (the 80 s variants, L3, L4) are left to their priors.

**ul60 08:50-09:19: 100 kNN lemmas became the best 5 s member (measured 09:21).** Once goals had used up their Vk60@0 option
in the current context, Vk100@0 (prior 3) was their best remaining option, so it ran. Its live yield then put it
first:

| member (from row 117,865 on) | runs | proved | conditional on |
|---|---:|---:|---|
| Vk100@0 | 1,354 | 32 (2.4%) | Vk60@0 failed before, same context |
| Vk100@0 | 372 | 10 (2.7%) | no Vk60@0 before |
| Vk60@0 | 697 | 6 (0.9%) | no Vk100@0 before |

* Vk100@0 overall: 42 proofs in 2.95 CPU hours, 14 per CPU hour, the highest of any deep member.
* On 16 Nov, 100 lemmas were dropped on count, at 5 of 150 against 30 lemmas' 6 (+1 −2). As a member after k60 it
  proves goals k60 does not.
* Next: k200@0, once kp@0 and kd@0 (prior 9 in ul61) are measured. Each lemma count is a different problem, cheap
  at 5 s.

**ul61 (09:19-10:05, priors 9), after the cascade:**

| member | runs | proved | CPU h | per CPU h |
|---|---:|---:|---:|---:|
| Vkd@0 (proof dependencies) | 1,050 | 9 | 1.83 | 4.9 |
| Vk100@0 | 4,297 | 28 | 7.73 | 3.6 |
| L0 (fresh) | 1,382 | 12 | 3.49 | 3.4 |
| Vkp@0 (use counts) | 307 | 0 | 0.54 | 0 |

* Vk60@0 did not run, since the priors at 9 put the three ahead of it. So these yields are not conditional on
  k60@0 having failed.
* The proof-dependency selection, also dropped on 16 Nov (+1 −2), pays. So far the use-count selection does not.
* Fresh runs proved 12 against 89 predicted: the scheduler overpredicts after a cascade.

**ul62 (10:05):** k200@0 and s12@0 added; `--explore 1` on the five lemma-set labels. In its first minute the deep
class ran Vk200@0 (99) and Vs12@0 (75), the unmeasured ones, first.
* **Complementary, measured (10:10):**
  * All 10 Vkd@0 proofs (ul61 to ul62's start) came after Vk100@0 had failed in the same context, 6 of them after
    Vk60@0 too.
  * ul62's first Vk200@0 and Vs12@0 proofs came after k100, kd and kp (and k60) had failed.
  * Each lemma selection is a different problem, and a 5 s run on it proves goals that the others' runs did not.
* **Input order is not a source of diversity (10:09).** A 5 s run of nil3_1K_e 502, with its 66 lemma axioms in the
  original, reversed or shuffled order, gives byte-identical output: twee normalises the input. Random restarts by
  permuting the problem do not exist for twee, so diversity has to come from changing the problem: other lemma sets,
  unfolding.

**hl@0: the kNN lemmas' proof steps as hints, back as a 5 s member (loop.py 5fc6b48, 10:11).**
* 2ap (16 Nov) dropped `--hint-lemma-proofs` on count: +1 −2 at factor 0.1 and at 0.01, union 7-8 of 150 against 6.
* Now it is `--variants hl`: the usual hints plus up to 300 proof steps of each of the goal's 30 kNN lemmas, at
  `--hl-factor` (0.1).
* On 30 random unsolved UL goals it adds 60-585 new hints (median about 270) to pools of 2,600-21,000. 20-30 of
  the 30 picks are of other originals. R1dist_to_aa1 674 gets none, since its picks are all siblings
  (hints/exp/hl_count.py).
* ul63.sh (prepared): ul62 plus hl@0 under `--explore 1`. It starts once ul62 has measured k200@0 and s12@0, about
  an hour.

**ul62's first 10 minutes (10:05-10:15): exploration measured both new members at once.**

| member | runs | proved | CPU h | per CPU h |
|---|---:|---:|---:|---:|
| Vk200@0 | 463 | 14 | 1.01 | 13.8 |
| Vs12@0 | 539 | 5 | 1.02 | 4.9 |

* All 14 Vk200@0 proofs came after Vk100@0 had failed on the goal in the same context, 12 after Vk60@0 too, and 13
  after Vkd@0 (hints/exp/condvar.py).
* All 5 Vs12@0 proofs came after Vk100@0 and Vkd@0.
* So each lemma count is its own problem: 60, 100 and 200 kNN lemmas each prove goals the smaller sets did not. On
  16 Nov "more than 30 kNN lemmas did not help" was a count comparison of single settings. As members after one
  another, they keep paying.
* ul63 (prepared) adds k400@0 and k200s12@0, and the search-setting members (m7t@0, m4b@0, r2@0, nopg@0, nom@0) and
  hl@0, all under `--explore 1`.

**What a 5 s run costs with 60, 200 and 400 kNN lemmas (10:17).** 4 random unsolved UL goals, twee-pg61 with rm4t,
no hints, 5 abstract s (hints/exp/k400_mk.py):
* CPU s a run: 4.8-6.3 at 60, 4.5-5.9 at 200, 1.2-6.4 at 400. The lemma count does not raise the cost.
* The 400-lemma run proved nil3_23_32_to_25 509 (unsolved in UL) in 1.2 s; the 60 and 200 runs did not.

**ul63 (10:16:50):** 13 members explored. In its first 2 minutes every one of them ran. Vhl@0's rows carry 114-591
hints more than the pool (none on R1dist_to_aa1, as the offline count predicted).
* **1,000 and 2,000 kNN lemmas (10:23), 4 other random unsolved goals** (hints/exp/k1000_mk.py):
  * CPU s a 5 s run: 5.6-7.9 at 1,000 lemmas, 5.4-18.4 at 2,000. Peak RSS rises to 90-220 MB.
  * aK2_eq_aK3_d 609 has only 487 candidates in its theory and weaker ones.
  * So k1000@0 is the next cheap member, at about 1.2 times the cost of a run. k2000 costs 2-3 times as much.

**Is the ratio rule's estimate fooled by non-stationarity? No (10:41).**
* The rates swing widely. In windows of 2,000 results rows since ul58 (hints/exp/winyield.py), the overall yield
  goes from 1.0 to 44 proofs per CPU hour, and L0 from 1.2 to 55.6. Members measured in a cascade or a restart burst
  carry that into their cumulative estimates (Vk100@0: 15.0 in the cascade's tail, 1.6-2.4 since).
* But the ratio to L0 in the same window is steadier: Vk60@0 is at 0.30-0.51 in 7 of 8 windows. So the swings are
  mostly a common factor.
* Offline test (hints/exp/estcmp.py, rows 47,531 on, priors as production's). For each window, how well does each
  estimator, from the rows before it, predict how the window's proofs split among the members that ran in it
  (multinomial log-likelihood, scale-free)?

| estimator | windows of 1,000 rows (84) | of 2,000 (42) |
|---|---:|---:|
| cumulative (the ratio rule now) | **−1,093** | **−1,170** |
| discounted over 3,000 rows | −1,108 | −1,206 |
| time-normalised (each CPU second scaled by the overall rate then against now) | −1,132 | −1,217 |
| flat (all members equal) | −1,276 | −1,357 |
| the hand-set priors alone | −1,650 | −1,742 |

* At discount and normalisation scales of 1,000 and 10,000 rows the order is the same.
* So the cumulative estimate ranks members best: its information is real (+185 over flat), and recency weighting
  only adds noise. No change to the ratio rule.
* The hand-set priors rank worse than no information at all. That supports `--explore` with data over hand-set
  priors for new members.
* **The prior's weight (10:42).** Production's priors inside the cumulative estimate are a little better than flat
  ones (−1,093 against −1,099 at 1,000 rows). A lighter prior weight is a little better still: YW 0.25 −1,078, 0.5
  −1,081, 1 −1,086, 2 (production) −1,093, 8 −1,108.
  * loop.py `--prior-weight` (default 2, cfb748e).
  * With `--explore` giving each new member at least 1 CPU hour of its own data, 0.5 is safe. It goes into the
    next production script.

**Which kNN ranks do the lemma-count members' proofs use? Deep ones (10:50; hints/exp/knn_ranks.py).**

| member | proofs | highest used kNN rank, median | proofs using a rank ≥ 30 | ≥ 100 | ≥ 200 |
|---|---:|---:|---:|---:|---:|
| L0 (30 lemmas) | 2,998 | 9 | 0 | 0 | 0 |
| Vk60@0 | 143 | 55 | 134 | 0 | 0 |
| Vk100@0 | 69 | 90 | 63 | 0 | 0 |
| Vk200@0 | 14 | 183 | 13 | 13 | 0 |
| Vk400@0 | 12 | 361 | 11 | 11 | 10 |

* They use few kNN lemmas (median 4-12), spread over the ranks. 93 of the 101 used deep lemmas of the k400 proofs
  are from other originals (567 of 609 for k100).
* So beyond the top 10 or so the similarity ranking carries little information about which lemma a proof needs.

**A learned lemma ranker: a feasibility test (10:57; hints/exp/lrank_feas.py).**
* Set: the 238 goals proved by k60@0-k400@0. Candidates are each goal's top 400 by today's index (2,960 of the 2,982
  used lemmas are among them). The label is used or not.
* LightGBM on pair features: rank, similarity, idf-weighted overlaps, containments, sizes, same theory, same
  original, use count (minus the target's own use, which leaked at first), goal number. 5-fold CV grouped by
  original.

| features | AUC | targets with all used lemmas in the top 30 | in the top 60 |
|---|---:|---:|---:|
| similarity rank alone | 0.897 | 18 | 68 |
| all | 0.920 | 23 | 89 |
| without the use count | 0.907 | 24 | 81 |
| without the use count and goal number | 0.903 | 17 | 74 |

* The lift comes from lemma popularity and the lemma's goal number (its depth in its original), not from better
  similarity. It is real but modest.
* The lemma-count members already reach the deep lemmas, at one 5 s run each. So a learned member would mostly
  save CPU, not add proofs. Not built. (The use-count selection kp@0 proved 0 in 523 runs.)
* A first run of this test used LightGBM's default thread count, every core: 9,000% CPU for 9 minutes,
  10:46-10:55, at load 135. It slowed production and exp29's wall clock in that window. Thread counts are now
  capped (n_jobs=2, OMP_NUM_THREADS=2).

**ul63's explored members after about 1 CPU hour each (rows 130,377-, at 11:10):**

| member | runs | proved | CPU h | per CPU h |
|---|---:|---:|---:|---:|
| Vk400@0 | 438 | 12 | 1.05 | **11.5** |
| Vk200@0 (measured in ul62 too) | 843 | 12 | 1.52 | 7.9 |
| L0 (fresh, new contexts) | 586 | 7 | 1.56 | 4.5 |
| Vm4b@0 (rule model rm4b) | 489 | 2 | 1.03 | 1.9 |
| Vk200s12@0 | 539 | 2 | 1.22 | 1.6 |
| Vhl@0 (kNN lemmas' proof steps as hints) | 537 | 1 | 1.05 | 1.0 |
| Vm7t@0 (rule model rm7t) | 534 | 1 | 1.03 | 1.0 |
| Vnopg@0 (no parental guidance) | 464 | 1 | 1.02 | 1.0 |
| Vr2@0 (rule threshold 0.2) | 596 | 0 | 1.05 | 0 |
| Vnom@0 (no rule model) | 466 | 0 | 1.03 | 0 |
| Vk100@0 | 521 | 0 | 0.92 | 0 (on goals where it had run in ul60-62) |

* Problem changes pay, search-setting changes much less. The larger lemma sets lead: 400 lemmas at 11.5 per CPU
  hour, after 60, 100 and 200 had failed. The other rule models and no PG make about 1-2 per CPU hour, a quarter of a
  fresh run's rate. A threshold of 0.2 and no model made none in 1 CPU hour each.
* All are kept: the ratio rule now orders them by these yields, so the weak ones run only when nothing better is
  left for a goal. In ul64 they run with `--prior-weight 0.5`.
* All the proofs came after other members had failed on the goal in the same context.
* **Per-original member yields do not predict better (11:12; hints/exp/famcmp.py).** A chronological split of
  production's rows, train 47,531-114,999 (67,469 runs), test 115,000 on (21,632 runs, 310 proofs). P(proof |
  member, original) is shrunk toward P(proof | member) with weight m.
  * Test log-loss: global 0.07530; per original m=5 0.07718, m=20 0.07615, m=100 0.07523.
  * Within a member's test runs, the per-original rate ranks at chance: Vk60@0 AUC 0.49, L0 0.59. (The members new
    since the split, k100-k400, have no training rows.)
  * So the ratio rule's single estimate per member stays. Which goal a member proves is not predicted by its
    original, at the resolution these counts give.

## ul64/ul65 members after their explore hour (19 Nov 15:50)

`levyield.py loops/UL/r5/results.tsv 145787` (ul64 from 12:40, ul65 from 14:46; 4 workers until 14:46, then 19):

| member | runs | proofs | CPU h | per CPU h |
|---|---:|---:|---:|---:|
| Vs40@0 (40 sibling lemmas) | 937 | 6 | 1.70 | 3.52 |
| Vk400 (80 s) | 8 | 1 | 0.32 | 3.17 |
| Vk1000@0 | 1,832 | 17 | 5.47 | 3.11 |
| L0 | 939 | 7 | 2.38 | 2.94 |
| Vk400@0 | 3,564 | 12 | 7.67 | 1.56 |
| Vk2000@0 | 233 | 1 | 1.01 | 0.99 |
| Vpw@0 (ProofWatch, ul65) | 620 | 0 | 1.14 | 0 |
| Vs200@0 | 426 | 0 | 1.01 | 0 |
| Vk100@0, Vk200@0, Vk60@0, Vkd@0, Vs12@0 | 245-912 each | 0 | 0.4-1.7 each | 0 |

* The lemma-count members keep paying, but they are decaying: Vk400@0 went from 11.5 per CPU hour (ul63, 11:10) to
  1.6, as its easy goals are used up. Vk1000@0 and Vs40@0 are now the best (about 3), and each proved goals after
  many other members had failed in the same context (exp/condvar.py: Vs40@0's 6 came after up to 12 others).
* Members with 0 in 1-1.7 CPU h fall below the live ones under the ratio order, with no hand change. Since 15:39,
  ul66 runs beside the climber (exp32, notes/2026-11-19-climber-member.md).

## The deep tail starved since 06:00 (found 16:20 through exp32)

* exp32's climber proved 4 heads by 16:19. Its plain 160 s control runs, which run only after a climb has
  proved its goal, proved 3 of the 4, in 19.6, 40.5 and 75 s, with the pool hints.
* Production had run 22-24 fresh 5 s pool runs on each of these heads, 1-4 40 s chain runs (L1) and dozens of 5 s
  members, but never a pool run beyond 5 s, nor anything at 80, 160 or 320 s.
* **Since ul58 (06:02, row 103428):** L0 ran 12,742 times (488 proofs), L1 213 times (10 proofs), Vk400 at 80 s 11
  times (explored). L2, L3 and L4 never ran (the last such row is 90626), and neither did the 80 s variants k60,
  p9, unf, two and nom.
* **Cause, a gap in the ratio order:** a label whose hand-set prior sits below the live members never runs, so its
  estimate is never updated. Meanwhile the live 5 s members decay (Vk400@0 from 11.5 to 1.6 per CPU hour in 5
  hours). L2's prior is 1.1 and L3's is the default. The explore rule covered only the labels listed by hand.
* **Fix (ul67 16:22, ul68 16:24):**
  * Fresh pool runs at 40 s and 80 s right after the 5 s level: `pool@1:0`, `pool@2:0` (loop.py 902f904, new
    syntax NAME@B:F = level B's budget, offered after level F).
  * Every label explored (no `--explore-labels`): each label with under 1 CPU h in round 5 is estimated at no less
    than the best measured one until it has 1 CPU h. That covers L2, L3, L4, the 80 s variants and the new pool
    members, about 10 CPU h in all.
* Still open: labels that were measured once and then decayed below others are not re-measured when the goals
  change. A periodic re-exploration (a label idle for X hours gets another slice) would close that.

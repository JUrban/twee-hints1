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

## Conditional yields (18:52, an independent check of the priors)

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
* **Pending:** exp20 (the 160 s control; extension cost by increment), exp15 (unfolded), exp19 (set-join).

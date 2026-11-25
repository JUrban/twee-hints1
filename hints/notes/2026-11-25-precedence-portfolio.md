# A portfolio of symbol precedences (exp85)

Written 25 Nov 2026, 08:08 UTC.

## Why

* The user (25 Nov, after exp84): Veroff just tried all possible symbol precedences (120?); maybe that can be reduced
  to some of them after portfolio construction, keeping the most complementary ones. Do not keep m, ld, rd, e at
  their default; evaluate experimentally. And build it in randomized stages: first all orderings on a small random
  set of problems, then a reasonably big portfolio of complementary ones with some redundancy, then a bigger random
  set with that smaller number of orderings, and iterate.
* exp84 (notes/2026-11-25-precedences.md) tried four random precedences on unsolved targets: 0 gained. On goals
  nobody can prove, complementarity cannot be seen. Here the orderings run on goals that are provable but not easy,
  in a context without their own proofs, with identical inputs per ordering.
* The user also: Veroff reorders the hints by the current term ordering in each search. Twee already does the
  equivalent: hints are matched in an orientation-free canonical form, and rewritten to normal form with the run's
  own rules as they are learned (`--eqhint-normalise`, on by default), so each ordering sees the hints in its own
  normal forms.
* AIM's signature: m, ld, rd (binary), e (constant), and the defined a, l, r (ternary), k, t (binary); 5! = 120
  orders of a, k, l, r, t. Twee ranks listed symbols above unlisted ones, in list order; the rest by occurrence
  count in the problem (lemma axioms included), so twee's default changes with each run's lemmas.

## Stage 1 (exp85): all 121 orderings on a small random set

* Orderings (exp/sets/exp85.orders): 0 = twee's default (no `--precedence`); 1-120 = each order of a, k, l, r, t
  exactly once, with m, ld, rd, e at random places (a full list of all nine symbols; order i: random.Random(85000+i)
  shuffles the nine, then the five defined ones take the slots of the defined ones in permutation i).
* Candidates (sets/exp85.cand, exp/sets/exp85.cand, seed 85): 40 of ul84's 55 L1 proofs (since 24 Nov 11:23, proved
  at the 40 s level, not at 5 s) and 80 of the 343 other climber-proved targets (CLS71 since 08:59, CLQ83).
* Capture (abs/exp85.sh, exp/exp85.sh, bash 4082683 from 08:07:13; loops/P85C, loops/EXP85.pids): CLQ83's final
  (clq83.sh's options, set mode `--targets`, `--runs 0 --final-cpu 40`, -j 4) on the 120 candidates, in
  t0758.trusted's context without them (49,624 solved; their rows and hints left out), with CLQ83's true.tsv,
  fillhints/, sketches/. `--twee exp/twee_capture.py`: a wrapper that keeps each run's problem, hints and rule-goal
  files and its arguments (loops/P85C/cap/log.jsonl), then runs twee-pg61.
* Dev set (loops/P85C/dev.txt): the candidates whose captured final proved with at least 1 CPU s, or failed; at
  most 50 (seed 85).
* Replay (exp/prec_replay.py, loops/P85C/replay.tsv): each dev goal's captured final under the 121 orderings,
  `--max-cpu 10`, without the --print-given/--print-hints output flags, -j 5. At most 121 x 50 x 10 s = 16.8 CPU h.
* Checked at 08:08: the replay reproduces captured runs (goal 420: captured final 9.76 CPU s, replay at the default
  9.65; goal 495: 19.26 and 18.24), and finds THM.

## Measures and the next stages

* Per ordering: proved of the dev set within 10 s; the default's count; the union of all 121; how many goals only
  non-default orderings prove; pairwise overlap.
* Stage 2: a portfolio of about 20-30 orderings by greedy cover with redundancy (each dev goal covered at least twice
  where possible) plus the default, on a bigger fresh random set (about 200 candidates, captured the same way).
* Stage 3: prune to the most complementary few, a bigger set again; then the portfolio against the default at equal
  CPU on stalled unsolved goals (CLQ83's failures) before any production use.
* Caveat: the dev goals are proved goals made unsolved in the context (their siblings' lemmas and the climbers'
  sketch hints still there); the use is on goals nobody has proved.

## Capture and dev set (08:07-08:23)

* Capture: 120 finals in 16 minutes, 76 proved within 40 CPU s in this context (without their own proofs; 44 failed).
* Dev set (loops/P85C/dev.txt): 50 of the 120 (seed 85, from those proved with at least 1 CPU s or failed): 31 the
  captured default proved (16 under 10 CPU s, 15 in 10-40 s: 11.8 to 38.5), 19 it failed at 40 s. So at the replay's
  10 s cap the default proves about 16, and the other 34 are where other orderings can show what they add.
* Replay from 08:23:17: 6,050 runs (50 x 121), -j 5, --cpu 10.

## Replay with abstract work (restarted 08:34)

* The user (08:2x): an ordering or strategy also dominates another when it proves the problems much faster (in
  abstract or real time) without losing any. The first replay recorded only THM/NO and CPU under a 10 CPU s cap, so
  it was stopped at 292 rows (kept in loops/P85C/replay.v1.tsv) and restarted at 08:34:42 (abs/exp85r.sh,
  exp/exp85r.sh, bash 4087625) with:
  * twee's WORK line in every row (critical pairs considered, rules), failed runs included;
  * an abstract cap: `--abstract 5` (twee `--max-time 5`; with `--abstract-time 2000` that is 10,000 considered
    pairs, production's first cascade level), `--cpu 30` only as a safety cap. Deterministic: goal 420 under order 2
    proved with exactly 2,013 pairs in both smoke runs; failed runs stop at 10,000. (The default's proof of 420 takes
    10,407 pairs, 5.2 abstract s, so it fails at this cap.)
* exp/prec_portfolio.py now also reports, from the work counts: the orders no other order dominates (a superset of
  their goals, at most their work on each goal, and more goals or less total work); the orders no other beats in the
  user's sense (a superset of their goals in at most half their total work); and a cost-greedy portfolio (cost: the
  sum over goals of the least work among the chosen orders, an unproved goal twice the cap), beside the coverage
  greedy with redundancy 2.

## BliStr's recipe (the user pointed to it; Urban 2013, arXiv:1301.2683, read in full 25 Nov)

* **Start set** (2.1): all 280 predefined E strategies on 200 random problems of the 1000 at a low 5 s limit (117
  solved); a minimal set covering those solutions (exact, MiniSat++): 6 strategies; those 6 on all 1000 at 60 s.
* **Metric** (2.3): given-clause loops, not CPU (hard to measure on easy problems); unsolved within the low limit:
  10^6. Here: twee's critical pairs considered, unproved = twice the cap.
* **Selection heuristic** (2.4): the performance matrix of all strategies on all problems at t_high = 10 s; keep per
  problem only the best (lowest) value, and only within [c_min, c_max] = [500, 30000] loops (too easy problems steer
  to strategies that do not help the hard ones, too hard ones cannot guide the low-limit search); a strategy is
  eligible if it is best on at least V = 8 problems (generality), at most N = 20 (size), ordered by that count; its
  problem set D_i = the problems where it is best.
* **Growing strategies** (2.2-2.4): ParamILS (iterated local search: perturb, then first-improvement) on the best
  eligible strategy with its D_i at t_low = 1 s (400 s per run); each new strategy evaluated on all problems at
  t_high, the matrices and the eligible list updated; next eligible strategy (not one already run with the same D_i);
  stop when none is left. The idea: make solvable problems much easier, and related harder ones become solvable.
* **Result** (3): 6 runs, 113 ParamILS runs in 30 h on 12 cores: 659 of 1000 at 10 s (597 at start with 60 s); a
  greedy cover needs 22 strategies (22 x 10 s = 220 s, less than 6 x 60 s); on 400 unseen problems at 160 s, 16 new
  strategies 253 against 6 old 233. Random search from scratch on the 403 unsolved (section 4): 15 solved in 7 h,
  first after about 1000 tries.

**Mapping to exp85.** Stage 1 here is BliStr's start-set step with the 121 orderings as the predefined strategies
(50 problems, abstract 5 s, work = considered pairs). exp/prec_portfolio.py now also prints BliStr's selection
(`--cmin 500 --cmax <cap> --versatility 2 --n 20`: V scaled to 50 goals from BliStr's 8 of about 600 solved; ties count
for every tied order) and writes REPLAY.blistr (order, best-on count, its D_i, its list). Not yet done: an exact
minimal cover (greedy only), and BliStr's growing step: local search over precedences (swaps of adjacent symbols,
then other twee options) on each eligible order's D_i at the low limit, evaluating new orders on all goals. The
space is 9! = 362,880 orders, so after stage 2 that step is the way to new orders beyond the 120 sampled.

## exp85's dev set was too hard; exp85b (09:22)

* The user (09:2x): the goals may be too hard for the ordering test to give reliable statistics (BliStr's heuristics).
  BliStr keeps a problem only when its best value lies in [c_min, c_max] = [500, 30000] given-clause loops: too easy
  problems steer to strategies that do not help harder ones, too hard ones cannot be solved at the limit.
* exp85's dev set: 19 of 50 failed even the 40 CPU s capture and 15 needed 10-40 s, while the cap was 10,000 pairs
  (about 5 abstract s). Reading at 09:18 (14 goals with all 121 orders): the default proved 3, the union 5, 9 goals
  no order proved. The replay was stopped at 09:21 (1,929 rows kept in loops/P85C/replay.v2.tsv).
* **exp85b** (abs/exp85b.sh, exp/exp85b.sh, bash 4096805 from 09:22:47; loops/P85D; log lines in loops/EXP85.pids):
  * 300 random trusted goals (sets/exp85b.cand, exp/sets/exp85b.cand: random.seed(851) over t0758.trusted without
    exp85's candidates; 109 originals), as BliStr's 200 random problems, not hard ones;
  * captured as before in t0758's context without them (49,444 solved), CLQ83's final at 40 CPU s, -j 5;
  * pre-pass: orders 0 (default) and 60 (exp/sets/exp85.pre.orders) at `--abstract 20` (40,000 pairs);
  * dev set: the goals whose lesser work of the two lies in [500, 10000] pairs (BliStr's window on the best value,
    with two orders standing in for all); at most 60 (seed 85). Selecting on order 0 and 60 favours those two a little;
  * replay: all 121 orders at `--abstract 10` (20,000 pairs, twice the window's top, so an order twice as slow as the
    better of the two still proves), `--cpu 60` safety cap, -j 5. About 60 x 121 runs; expected 2-3 hours.

## exp85b pre-pass (09:36) and the resolution of twee's work count

* Capture and pre-pass were quick (09:22:51-09:36:47): 295 of 300 proved by order 0 or 60 at 40,000 pairs; the
  lesser work in [500, 10000] for 191, under 500 for 91, over 10,000 for 13; dev set 60 (loops/P85D/dev.txt). Replay
  from 09:36:47: 7,260 runs.
* **The work count is coarse.** Of 588 pre-pass proofs, 198 show exactly 2,000 considered pairs, 55 show 0, and 2001-2009
  are common. twee rechecks the goals at most once per abstract second (recomputeGoals, `newTask 1 0.02` in Twee.hs;
  src/Twee/Task.hs: a task runs at most once per its frequency in seconds of the abstract clock), which is 2,000 pairs
  with `--abstract-time 2000`; a proof found by that recheck is seen only then. Others are seen at once (126, 132, ...).
  So work is measured to about one abstract second. exp/prec_portfolio.py now rounds work up to steps of `--level
  2000` pairs, so equal steps are ties (BliStr's best-on counts every tied order); the dominance and cost views use
  the rounded values. BliStr's window [500, 10000] on the best value thus means: proved within 1 to 5 abstract s.
* 09:48: CLS71 had no target left (0 runs since its 09:45 refresh; new targets ran out about 00:18 and 596 of its 870
  re-climbs are done) and CLQ83 idles, so the replay was resumed with -j 10 (abs/exp85c.sh, exp/exp85c.sh, from 09:48:57;
  1,011 rows kept, 6,249 to go). Runs are deterministic under the abstract cap, so the thread count does not change rows.

## exp85b result (10:21; exp/prec_portfolio.py loops/P85D/replay.tsv, and CPU figures from the rows)

* **Every order proves every dev goal**: 60 of 60 under each of the 121 orders within 20,000 pairs (the largest
  rounded work 18,000). So in this window the orders differ only in speed.
* The default's work in 2000-pair steps: 1 step 32 goals, 2 steps 21, 3 steps 3, 5 steps 1, 6 steps 3; its CPU
  median 2.9 s (q75 3.5, max 10.2). Most goals are at the measure's floor.
* Work: the sum of the least work per goal over all 121 orders 152,000 against the default's 212,000; the cost
  greedy reaches 152,000 with three orders (0, 119, 1). Dominance: 120 of 121 not dominated, none dominates the
  default; in the user's "much faster" sense (a superset in at most half the total work) no order beats another.
  BliStr's best-on (ties counted): order 1 best or tied on 49 goals, 19/28/45 on 47, the default on 35.
* CPU (finer than the work steps, noisier): totals 176-199 s over the 60 goals for all orders, the default 191 s
  (rank 62 of 121; by work rank 72). Per goal, the best of 121 orders against the default: median 0.88, q25 0.80, about
  what the minimum of 121 noisy timings gives; some order is at least twice as fast on only 2 of 60 goals. Order 1:
  median 1.01, never twice as fast; order 18 (the best total): median 0.96.
* **Reading.** On goals the climber's final proves in 1-5 abstract s, the symbol precedence hardly matters: a
  portfolio of orders buys about 10% CPU at best, inside the noise. The differences, if any, are on harder goals:
  exp85's partial replay (goals needing 10-40 s, 10,000-pair cap) had 2 of 5 proved goals proved only by non-default
  orders. Next: the same stage on goals of medium difficulty (the better work of orders 0 and 60 in 5-30 abstract s),
  with a 40 abstract s cap, so the measure is far above its floor.

## exp85d: medium-hard goals (10:23)

* abs/exp85d.sh, exp/exp85d.sh, bash 4122881 from 10:23:57; rows in loops/P85C/pre40.tsv and loops/P85C/replay40.tsv.
* Goals: exp85's 120 candidates (hard ones: the climber's targets; captures already in loops/P85C/cap, context t0758
  without them). Pre-pass: orders 0 and 60 at `--abstract 40` (80,000 pairs), `--cpu 120` safety cap, -j 10.
* Dev set: the goals whose lesser work of the two lies in [10000, 40000] pairs (5-20 abstract s, far above the 2000-pair
  step); at most 30 (seed 85). Replay: all 121 orders at `--abstract 40`, -j 10 (at most 3,630 runs).
* Question: on goals that need 5-20 abstract s, do orders other than the default prove goals the default misses
  within 40 abstract s, or prove them much faster (the user's dominance)? If so, the greedy and cost portfolios
  pick the complementary ones for stage 2 (a bigger random set); if not, precedences are not worth a portfolio slot.
* Pre-pass (10:23:57-10:37:15): 98 of 120 proved by order 0 or 60 within 80,000 pairs; the lesser work under 10,000
  for 40, in [10000, 40000] for 45, over 40,000 for 13; dev set 30 (loops/P85C/dev40.txt). Between the two orders
  alone: both 88, only the default 3, only order 60 7, neither 22; on the 88 the work ratio 60/default median 1.00,
  under 0.5 on 7, over 2 on 8. So on harder goals single orders already differ. Replay from 10:37:15, 3,630 runs.
* The stopped hard replay (replay.v2.tsv, 10,000-pair cap; 15 goals with all 121 orders): 10 proved by none; goal 420
  (default 10,407 pairs, over the cap) proved by 86 orders, 32 of them in one 2000-pair step; goal 522 (default
  fails) by 39 orders; goal 340 by 107 orders in 2 to 5 steps.

## exp85d result (13:05; exp/prec_portfolio.py loops/P85C/replay40.tsv, the equal-budget figures from the rows)

* 30 dev goals x 121 orders at 82,000 pairs. The default proves 29; per order min 28, median 29, max 30; the union 30
  (one goal only non-default orders prove, 47 of them). Goals proved by all 121 orders: 22.
* Work: no order dominates the default, none is "much faster"; all 121 non-dominated. Total work (unproved = 82,000):
  the default 779,251 (rank 25 of 121), the best order 750,412 (113), the median 826,645: no order is systematically
  better (the best saves 4%). Per goal the least work of all 121 orders against the default's: median 0.80, q25 0.55.
  Order 113 against the default: median 1.01, under half on 5 of 29, over twice on 0.
* Equal budget (k orders each at B/k pairs, chosen on these same goals, so optimistic) against the default at B:
  B 20,000: the default 12, 2 orders 7, 3 orders 3; B 40,000: 29 against 18 and 12; B 80,000: 29 against 30, 24, 19.
  The dev window favours the default (selected on its or order 60's work), but per-goal work ratios near 1 mean
  slicing must lose: the orders' work on a goal is spread about +-20%, a light tail, so a restart with another order
  rarely costs less than half of continuing.
* **Reading.** On AIM goals of 5-20 abstract s, twee's symbol precedence changes the work by a scatter of about 20%,
  not systematically; best-of-121 is a minimum over that scatter. A fixed-budget portfolio of orders loses against
  the default. A precedence portfolio can only pay where extra budget is spent anyway on stalled goals.

## exp85e: orders on stalled goals at equal work (pre-registered, launched 13:07; bash 4143336)

* The user's last stage: the portfolio against the default at equal work on stalled goals. Goals: the 22 of exp85's
  120 that neither order 0 nor 60 proved within 80,000 pairs (exp/sets/exp85e.goals, 12 originals).
* Arm D: the default at `--abstract 160` (320,000 pairs; --cpu 900). Arm P: orders 3, 116, 104, 20 (exp85d's
  coverage and cost greedy, exp/sets/exp85e.orders) at `--abstract 40` (80,000 pairs) each: 320,000 pairs in all.
  Orders 0 and 60 at 80,000 are known to fail on all 22 (pre40.tsv). -j 10; rows loops/P85C/e85d.tsv, e85p.tsv.
* Expected: if precedence variety matters on hard goals, P proves more than D; if the scatter is light as above, D
  (one long run) wins.

## exp85e result (13:30; loops/P85C/e85p.tsv, e85d.tsv; figures from the rows)

* 22 goals neither order 0 nor 60 proved within 80,000 pairs. **Arm D (the default at 320,000) proves 16; arm P
  (orders 3, 116, 104, 20 at 80,000 each) proves 6.** Both 5, only P 1 (lra2aa__goal_426: order 20 at 49,055; the
  default fails at 320,000), only D 11; the union 17.
* Cost: P 1.73 CPU h (6.8M pairs, most runs at the cap), D 1.35 CPU h (4.1M pairs: proved runs stop early). Per
  CPU h: P 3.5 proofs, D 11.9.
* D's 16 proofs by work: 80-100k pairs 5, 100-160k 6, 160-320k 5. Most "stalled" goals were simply a little beyond
  the 80,000 cap; continuing pays more than restarting under another order.
* By order in P: order 20 proves 5, orders 3 and 116 2, order 104 1. On nil3_1K_e__goal_528 all four orders prove
  within 32-48k while orders 0 and 60 failed at 80k (the default needs 104k): one goal where the precedence matters.

## Conclusion of exp85 (the user's staged precedence portfolio)

* Stages: easy goals (exp85b, 1-5 abstract s): every order proves every goal, CPU within about 10%. Medium goals
  (exp85d, 5-20 abstract s): no order better than the default by more than 4% in total work; the per-goal scatter is
  about 20%; splitting a budget over orders loses (40,000: 29 against 18). Stalled goals at equal work (exp85e): one
  long default run 16, four orders 6.
* So for twee on AIM, symbol precedence is a weak lever: it re-randomises the search by about +-20% in work, with a
  light tail. Veroff's many precedences pay in Prover9, whose search changes more with the ordering; in twee, at a
  fixed budget, the time is better spent continuing the default run. exp84 (random precedences on unsolved targets,
  nothing new) agrees.
* Worth keeping: a precedence variant as a last member on goals the default has failed at a long run (like
  lra2aa_426), at a small share, measured by the ratio rule. Not built now: the frontier (production's stall) has
  other cheaper members first (the climber's final, long default runs).
* Hint reordering by the current term order (the user: Veroff reorders the hints per run): twee already matches hints
  orientation-free and normalises them with the run's own rules (`--eqhint-normalise`), so a precedence change needs
  no separate reordering.

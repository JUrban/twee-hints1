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

# Larger lemma lists in the plain levels, from zero (exp65)

Written 23 Nov 2026, 15:47 UTC, before the launch (it starts 2 minutes after exp64 ends, about 16:54).

## Question

exp64 put two plain levels into the from-zero cascade (P4B: `plk100s40@0`, `plk400s130@0`). At 4 hours P4B led the
control by +397 at equal work, and its plain levels had proved 80 goals P4A had not (notes/2026-11-23-plain-level.md).
Offline, on 235 held-out goals of Z9's gap (goals production proved and the from-zero loop Z9 did not; Z9's final
context, plain 5 s, kNN lemmas only), the number of similarity kNN lemmas mattered far more than a learned order:
11, 20, 22, 35, 35 and 40 proofs with 30, 100, 200, 400, 800 and 1,600 lemmas; as two levels, 100+400 (P4B's sizes)
prove 39 and 400+1,600 prove 46 (notes/2026-11-23-lemma-ranker.md, "Size, not order" and "800 and 1,600 lemmas").
Do plain levels with four times longer kNN lists raise the from-zero curve over P4B's?

This replaces the first exp65 design (every run's kNN lemmas from the ranker lr2h, `--lemma-ranker-all`), which was
dropped before its start: the ranked list lost to similarity at 30, 100 and 400 lemmas on those goals.

## Setup

* abs/exp65.sh (exp/exp65.sh): two arms by abs/or_test3.sh, sets/half2 from zero (loops/EMPTY), 4 workers each,
  6 hours, solve_new.sh's defaults, transfer every 5 minutes, SCHED= ; as exp64.
* Q5A, the control: P4B's DEEP exactly (plain levels `plk100s40@0`, `plk400s130@0`, prior 3 each, in
  `--explore-labels`), on P4B's CPU set 7-13,35-41. Q5A against P4B is a cross-time replica of one configuration,
  which measures the run-to-run spread the "under about 400" rule guesses at.
* Q5B: the same with the plain levels' kNN lists four times as long: `plk400s40@0`, `plk1600s130@0` (siblings as
  P4B's), on P4A's CPU set 0-6,28-34 (the slower one in exp64's first hour; equal-work readings correct for it).
* The DEEP strings are in loops/EXP65.args. Binary /project/bin/twee-pg61 (solve_new.sh's).
* Caveats from the pre-checks: they had no sibling lemmas (condprove.py's sibling pool came from --set, the 500 gap
  goals, none proved), and a 1,600-lemma run costs about 8 s of wall time against 3.4 s at 400. In the loop the
  levels run on goals L0 failed, early in a thin context, so the offline ranking of sizes may not carry over.
* Launch condition: exp64's 6-hour reading. If P4B does not lead at 6 hours, the control changes (or exp65 waits).
* Proofs: loop.py's proof jobs and exp/proofq.py into loops/Q5A/proofs, loops/Q5B/proofs.

## Readings

abs/setcurve.py sets/half2 Q5A Q5B and exp/abscurve.py at 60, 120, 240 and 360 minutes; Q5A against P4B at the same
minutes (the replica); at 6 hours exp/armdiff.py Q5A Q5B and the plain levels' proofs per run. Rule as exp64's: +200 or
more at 6 hours by wall time and at equal work, and beyond Q5A's spread against P4B.

## Frontier sweep PLG1 (from 15:45)

The same lever on production's frontier: abs/sweepq.sh runs PLG1 (`--time 5 --sibs 100 --after 30 --knn 1600`, W's
siblings) on production's 3,268 unsolved goals, 3 threads, context loops/UL/solved.tsv at 15:45; proofs into
loops/CI3 and loops/UL. W (400 kNN, PLW1) proved 23 of 3,318 on this frontier at 08:24 and the live loop's 400-lemma
cycles 0-4 a cycle since.

## Twee's startup with long lists (15:53)

One problem (aa1_45_c__goal_305) of each size arm, `--max-time 0.01` (twee checks the limit only after it has
activated every axiom):

| arm | fof lines | seconds to give up |
|---|---:|---:|
| ZGS | 31 | 0.06 |
| ZKS | 101 | 0.13 |
| ZK4S | 401 | 0.66 |
| ZK8S | 801 | 1.62 |
| ZKGS | 1575 | 8.09 |

Superlinear: twee activates every axiom and builds its critical pairs with all earlier ones before the first time
check (`+RTS -s` at 1,575: 6.6 s mutator, 1.0 s GC). Duplicates up to renaming and orientation are 0.2% of the kNN
lemmas, so deduplication would not help. At 1,600 lemmas the startup is about half of a 5 s run's wall time. If the
1,600-lemma level pays (exp65, PLG1), lazy lemma axioms (activated when selected, like passives) are the twee change to make.

## Lazy lemma axioms: twee-e63 (16:01)

twee-e63 `--lazy-lemmas` (commit d262fb3): the axioms named lemma_* are not added before the first step. They wait in
a list sorted by their critical-pair score (scoreCP at depth 0, times `--lazy-lemma-factor`, default 1), and the
main loop activates the next one whenever its score is at most the best queued pair's. So a lemma enters the search
when a pair of its size would, the way an SOS clause does in Otter or Prover9. Without the flag e63 is byte-identical
to e62 on 3 goals. On the 1,575-axiom problem, giving up at `--max-time 0.01` takes 1.2 s instead of 8.1 s. On 10 of
ZKGS's proofs, a biased pick, the lazy runs proved 4, faster in wall time. Lazy runs reach the 5 s abstract limit
sooner, because each step pairs with fewer active rules.

A/B (exp/z9lazy.sh): the 235 goals with ZKGS's settings (1,600 kNN, no siblings), cond/ZLG1 (factor 1) and cond/ZLG5
(factor 0.5) against cond/ZKGS (eager, 40 proofs).

Result (16:36):

| arm | goals | proved | eager ZKGS on them | + | − | wall s | eager wall s |
|---|---:|---:|---:|---:|---:|---:|---:|
| cond/ZLG1, factor 1 (stopped) | 165 | 11 | 28 | 0 | 17 | 699 | 1319 |
| cond/ZLG5, factor 0.5 | 235 | 40 | 40 | 3 | 3 | 1932 | 1870 |

At factor 1 the lemmas enter too late (stopped when it was 17 proofs behind); at 0.5 they enter early enough to prove as much, and the wall time is the same, so the startup is not waste: pairing the lemmas early is the work that proves these goals. e63 is not used; the eager default stays.


## Pre-check with siblings (16:36)

exp/z9gap9.sh: the 235 goals with the sibling pool from sets/all (each problem checked: 40 or 121 sibling lemmas), the plain levels' settings in condprove.py's terms (earlier+later siblings):

| arm | level | proved | wall s |
|---|---|---:|---:|
| cond/ZQA1 | P4B's plk100s40 (30+10, 100 kNN) | 26 | 796 |
| cond/ZQA2 | P4B's plk400s130 (100+30, 400) | 36 | 999 |
| cond/ZQB1 | Q5B's plk400s40 (30+10, 400) | 36 | 929 |
| cond/ZQB2 | Q5B's plk1600s130 (100+30, 1,600) | 39 | 2082 |

As pairs: P4B's levels 40, Q5B's 45 (+8 −3, union 48). Q5B's first level against P4B's: +14 −4 at 1.17 times the wall time; the second: +9 −6 at 2.08 times. Siblings against none at the same kNN size: 100 kNN +9 −3, 400 +4 −3, 1,600 +1 −2: siblings matter at 100 kNN lemmas and hardly beyond. exp65's design stands.

## Started

loops/EXP65.pids: Q5A 3439500 23 16:55:36; Q5B 3439502 23 16:55:36. loop.py PIDs: Q5A 3439513 (CPUs 7-13,35-41), Q5B 3439516 (CPUs 0-6,28-34); the DEEP strings in loops/EXP65.args. Crash watcher on these and production's processes. Readings at 60, 120, 240 and 360 minutes, and Q5A against P4B at the same minutes.

## The frontier is 92 heads (17:01)

PLG1 (5 s, 1,600 kNN, W's siblings, production's frontier) was stopped after 1,453 of 3,268 goals with 1 proof
(lra2aa__goal_390, merged into production; it used a kNN lemma ranked 1,420, beyond any 400-list). The 400-lemma sweep
PLW1 had no proof among these goals either: the 5 s frontier is exhausted in this context.

Of the 3,268 unsolved goals (loops/TRUSTNOW/t1457), 92 have every earlier sibling proved, one in each of the 92
originals that still have unsolved goals: each original's first unsolved step. The rest have 1 to hundreds of
unproved earlier siblings (2,496 have 10 or more). With siblings assumed, most of those are easy (COND1), so these 92
heads are what blocks the frontier. sets/heads92 (copy exp/sets/heads92). Two plain 60 s sweeps of them by
abs/sweepq.sh (cond/SWEEPQ.txt), 3 threads, context loops/UL/solved.tsv, proofs into loops/CI3 and loops/UL:
HDW1 (W's sizes: 100+30 siblings, 400 kNN) and HDG1 (1,600 kNN). sweepq.sh now passes the sweep's --time to
condimport.py (whose default of 5 s would have failed to re-prove a 60 s proof).

HDW1 result (17:49): 4 of 92 heads in 2.25 CPU h of twee runs (1.8 per CPU h; production's own loop about 5 in its last 6 hours on 6 workers); condimport: 4 of 4 into loops/CI3; 4 merged into loops/UL (round 5).

| head | seconds | kNN lemmas used | unsolved goals after it in its original |
|---|---:|---:|---:|
| aK1_to_aK2__goal_75 | 13.0 | 19 | 1 |
| aK2_eq_aK3_f__goal_409 | 14.6 | 4 | 0 |
| gbol_to_aK1__goal_458 | 54.0 | 17 | 1 |
| KK_Kcom_to_aK1__goal_283 | 5.7 | 10 | 2 |

Three of the four took 13-54 s, beyond the 5 s sweeps. With these proofs in production the next goal of each original becomes a head.

## 1 hour (17:56)

| | 30 min | 60 min | equal abstract work |
|---|---:|---:|---:|
| Q5A | 15,193 | 17,367 | 15,193 at 30 min, 17,300 at 58 min |
| Q5B | 15,064 | 17,495 | 15,384 at 32 min, 17,492 at 60 min |
| P4B (exp64, the same configuration as Q5A) | 15,303 | 17,602 | |

Q5B by wall time: 30 min -129, 60 min +128; at equal work (the points above, in order): +191, +192. The replica: Q5A against P4B (same configuration, same CPU set, 6 hours apart) 30 min -110, 60 min -235: the spread between identical runs is as large as Q5B's lead so far.

## HDG1: 1,600 kNN lemmas on the heads

* HDG1 ran the 88 heads left after HDW1 (60 s, 100+30 siblings, 1,600 kNN lemmas; exp/sets/SWEEPQ.txt), ended 18:52.
* **1 proof in 88** (aK1_nil3_b__goal_177, 40 s, 49 kNN lemmas used), 3.02 CPU h: 0.33 per CPU h. HDW1 with 400
  lemmas: 4 in 92, 2.25 CPU h, 1.78 per CPU h. The 4 HDW1 proofs were not rerun (already trusted), so this is not a
  paired test on them.
* At 60 s on the heads, 1,600 lemmas cost a third more CPU (startup) and prove less. plainlive4's H setting keeps 400.
  Merged into loops/UL through CI3.

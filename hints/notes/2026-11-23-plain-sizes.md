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

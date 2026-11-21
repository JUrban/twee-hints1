# exp49: a quick first run for every goal (`--quick Q`) (21 Nov 04:47)

**Question.** From zero, the first hour gives about 90% of a 5-hour run's proofs (P2J: 19,161 at 60 minutes,
21,706 at 300), and the frontier's first pass over all goals ends at about 150 minutes. Does a first pass with a
much shorter budget move the frontier faster, so deeper goals get their siblings' lemmas sooner?

## Why

P2J's results (loops/P2J/r1/results.tsv, half2 from zero, 6 workers, 5 hours):

* 23,520 goals had a first fresh run: 17,309 proved at L0 (2.8 CPU hours) and 6,211 failed (10.3 CPU hours, 6.0 s
  each). **The failed first runs took 79% of the first pass's CPU.**
* Of the 17,309 first-run proofs, 12,220 came within 0.5 s, 14,904 within 1 s (86%), 16,341 within 2 s (94%) and
  17,034 within 4 s.
* With a 1 s first run the first pass would cost about 4.4 CPU hours instead of 13.1: the frontier passes every goal
  about three times sooner. The 2,400 goals that need 1-5 s then get their 5 s run later, in a context with more
  lemmas. The other 6,200 failures would have failed at 5 s anyway, and their 5 s runs also come later, when more
  of their siblings are proved.
* P2J's first runs by half hour (proved / failed): 14,971 / 346, 1,591 / 1,045, 496 / 1,309, 145 / 1,361, 69 / 1,224,
  37 / 926. From 60 minutes on the first runs mostly fail (27%, 10%, 5%, 4% proved) and still hold most workers: the
  4,820 failures of 60-180 minutes took about 8 of the 12 CPU hours. Of all 6,211 first-run failures, 2,070 were
  proved later (L0 859, Vunf@0 127, other variants and L1 107, the side writers 977).
* Earlier: a 5 s first level beat 10 s in production's context (2ag: 33 against 20). A shorter first run from
  zero has not been tried.

## Change

loop.py `--quick Q` (default off; with `--cascade --fail-order`, not with the learned scheduler):
* A goal's first fresh run in the round runs at Q seconds, without saving its state.
* If it fails, the goal is not counted as failed (nf, the --fail-order count) and stays untried. It waits behind
  the goals never run, ahead of the goals that failed a T0 run (sort key: fewest failures, then quick-failed last,
  then the rest of the --fail-order key). Its next fresh run is at T0, as before.
* Its results row has the label L0 and a column `q=1`. On a restart (--cascade-continue), a q=1 row is not an
  attempt; a goal with a failed q=1 row still waits for its first T0 run.

## Smoke tests

sets/smoke487, 2 workers, 12 minutes, abs/or_test2.sh with solve_new.sh's defaults:
* loops/QKT (04:46, `LOOPARGS="--quick 1"`) against loops/QKC (04:46, no LOOPARGS), started together. No errors;
  both 395 solved at 12 minutes. Curves (1, 2, 3, 4, 6, 8, 10 minutes): QKT 308, 323, 351, 367, 385, 389, 393; QKC
  288, 344, 354, 377, 382, 385, 394. QKT's 487 quick runs proved 323 (66%) and ended at 128 s; then the 164 that
  failed had their 5 s runs. One original's chain at 2 workers is too small for the frontier effect.

## Plan

An A/B on half2 from zero, 6 workers, against a control with the same base, when exp48 ends (about 09:40): the
base is exp48's winner. Measures: setcurve at 15, 30, 60, 90, 120 and 180 minutes; the time the first pass ends
(the last never-run goal's first run); the quick runs' proofs and failures; the later 5 s runs of quick-failed
goals (proved, failed); latency of the first-run proofs (exp/latency.py).

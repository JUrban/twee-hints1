# Failed-before goals as their own class in the cascade (exp44, 20 Nov)

Written 20 Nov 2026, 18:44 UTC, before launch; design changed at 19:37 (below). Launched with exp45 by
abs/exp4445.sh ([hints/exp/exp4445.sh](../exp/exp4445.sh)), automatically when Z6 ends (about 23:33;
abs/afterz6.sh), so the CPU budget holds.

## Why

* With `--fail-order`, solve_new.sh's default, the cascade keeps one list of goals to run fresh: those never failed
  in the round first, then those that failed once and have a new context since (`--retry-knn`: a changed kNN lemma
  set; or new siblings). Early on that is right: in Z1 a first run proved 51%, a repeat 4-6% (REPORT 2as).
* **Late it is wrong** (Z6, notes/2026-11-20-z6.md; exp/retrysplit.py):

  | Z6, minutes | first runs | retries |
  |---|---|---|
  | 0-30 | 27,560/27,831 | 72/209 |
  | 60-90 | 1,557/4,248 | 47/483 |
  | 90-120 | 287/3,037 | 31/383 |
  | 120-150 | 102/3,006 | 8/535 |
  | 150-180 | 34/2,035 | **1,096/2,331** |

  The first runs of all 51,784 goals ended at about 150 minutes. Then the retries of goals that had failed once,
  about 1.9 hours earlier (median), proved 47%. The last first runs proved 3%.
* The half tests never get there: after 2 hours on 6 workers about 22,300 of half2's 25,847 goals have had a first
  run (P2E, P2F). Their retries, a few hundred per half hour at 4%, are mostly deeper levels and variants.
* Z4 (17 Nov) had no such burst: at most 136 retries per half hour. The context-change retries come from today's
  system.

## Change

loop.py `--retry-class` (with `--mix` and `--fail-order`): the failed-before goals of the list are a mix class of
their own (q) beside the never-failed (r) and the deeper levels (d). Each class keeps the `--mix` share of the
workers (0.1 × 12) while it has waiting goals, and the other slots go to the class with the most proofs per run
second over its last 300 runs. Within q the order is as before: fewest failures, near before far.

Smoke test (18:37-18:42, loops/RCT, 487 goals of two originals, 2 workers, 6 minutes): class q ran 17 retries, no
errors.

## Set and setting

* **Changed at 19:37: 5 hours, with a 5-hour control.** On half2 with 6 workers the first runs last beyond the
  2 hours of P2E/P2F (22,300 of 25,847 goals had one at 2 hours), so the late retries come after 2 hours. Three
  arms start together on sets/half2 from zero, abs/or_test2.sh (solve_new.sh's defaults, 6 workers, SCHED=,
  transfer every 5 minutes), HOURS=5:
  * **P2K:** the control (LOOPARGS empty);
  * **P2H:** `LOOPARGS=--retry-class`;
  * **P2J:** exp45's arm ([notes/2026-11-20-yield-discount.md](2026-11-20-yield-discount.md)).
* P2E (exp41, 20,152 at 2 h) and P2F (exp42, 20,174) are the same system as P2K for the first 2 hours. Identical
  runs differ by about 185 at 2 hours.

## Measures

* `abs/setcurve.py sets/half2 P2K P2H P2J --at 30,60,120,180,240,300` (and P2E, P2F to 2 hours); one-arm goals.
* exp/retrysplit.py on P2H against P2K: first runs and retries per half hour.
* **Decision:** P2H ≥ P2K + 185 at 5 hours (or at 2-3 hours with P2E/P2F in the same range as P2K) makes
  `--retry-class` solve_new.sh's default; ahead early but within noise at 5 hours is a speed gain, reported as
  such. Then on the whole benchmark (Z7, against Z6).

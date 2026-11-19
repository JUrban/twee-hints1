# Today's system from zero: half1 in 2 hours with the deep portfolio (exp27)

Started 19 Nov 2026, about 07:20 UTC (`date` checked 07:16). Script abs/exp27.sh (hints/exp/exp27_run.sh). Part of the
portfolio task (notes/2026-11-18-portfolio-review.md).

## Why

* The user's goal is a system that, unleashed on a benchmark like AIM60k, solves as many problems as possible in as
  little time as possible. The last from-zero measurement of the whole system was PGA (17 Nov 16:54,
  notes/2026-11-17-pg-ab-half1.md): sets/half1 from zero, 6 workers, 2 hours, 18,987 proved.
* Everything since was developed and measured on production's hard tail (UL, round 5):
  * chain hints for the deep levels (exp3, exp8, exp11);
  * the variant portfolio as optional attempts ordered by live yield (`--ratio-order`, REPORT 2az);
  * the 40 s chain level (ul58).
  solve_new.sh, the script for new problems, has none of it.
* So: does today's portfolio help from zero, hurt it (for instance through production's tail priors), or do
  nothing within 2 hours? The tail's yields (L1 about 2 per CPU hour) are far below a from-zero run's (5 s runs at
  hundreds an hour), so the deep class may matter little early and more after the first hour.

## Set and setting

* **Goals:** sets/half1, 64 of the 129 originals (random, seed 17). **Context:** loops/EMPTY, so no lemmas, hints or
  chain records from outside. The chain records are the loop's own proofs (no `--chain-records`).
* **Script:** abs/or_test.sh, as PGA. That means solve_new.sh's defaults: `--mix 0.1 --fail-order`,
  `--no-fresh-states`, rule model rm4t, 6 lemmas and 30 kNN lemmas, and the live transfer (twee-e39, every 300 s,
  2 workers at times).
* **PGC (the arm):** PGA plus the following.
  * twee-pg61, that is twee-e61 with `--pg-threshold 0.25 --ground-joining-branch-limit 100`. PGA's twee-pg was
    e48 with PG 0.25. e61 judges PG before unification, as e50 does, so the search is the same. The branch limit
    only ends hangs.
  * `--cascade 5,40,80,160,320` (PGA: 5,20,80,320, the pool at every level).
  * `--chain-level 1`, `--variants unf@0,k60@0,k60,p9,unf,two,nom`, `--variants-after 3`, `--variant-budget 80`.
  * `--priors L1=1.73,L2=1.1 --ratio-order`.
* **Control:** PGA as it ran on 17 Nov, with the same script, set, workers and hours. There is no new control run,
  to save 8 CPUs. The machine's load then was similar: production beside it.
* **CPUs:** 6 workers plus the transfer's 2 at times. Production goes to 12 workers meanwhile (ul59), and exp23 keeps 1.

## Measures

* `abs/setcurve.py sets/half1 PGA PGC --at 10,20,30,60,90,120`: goals of half1 proved at each minute. Noise: about
  185 at 2 hours between identical runs (ORA/ORD).
* By level (r1/results.tsv): runs, proofs and CPU for L0, L1, L2 and each variant. Where PGC's own proofs came from.
* Goals only one arm proved.

## Results

(running)

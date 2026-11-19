# From zero with the explored 5 s lemma members (exp29)

Written 19 Nov 2026, 10:21 UTC. Started 10:38:51 (loops/PGD), after exp28 ended. Production went to 12 workers at
10:38:39 for its 2 hours (ul63 with J=12; first results row 133503). Script abs/exp29.sh (hints/exp/exp29_run.sh). Part of the portfolio task
(notes/2026-11-18-portfolio-review.md); it follows exp27 (notes/2026-11-19-from-zero-portfolio.md).

## Why

* exp27 ran today's tail system from zero on half1: neutral at 2 hours (PGC 18,917 against PGA 18,987).
  * Its deep class (about 1 of 6 workers) ran Vunf@0 at 28 per CPU hour.
  * The 40 s chain level L1 was starved by the ratio order's priors: 4 runs in 2 hours, all 4 proved.
* On production's tail this morning, 5 s members with other lemma sets paid as well as fresh 5 s runs in new
  contexts, each after the others had failed (REPORT 2az):
  * k100@0: 14 per CPU hour;
  * k200@0: 13.8;
  * kd@0: 4.9.
  `--explore` measures a member before its prior can starve it.
* From zero, the second hour adds only 2.5% (18,500 to 19,000): the 5 s level saturates. Does a portfolio of cheap
  5 s problem changes, explored early, lift that second hour?

## Set and setting

* **PGD:** exp27's PGC (sets/half1, loops/EMPTY, abs/or_test.sh = solve_new.sh's defaults, 6 workers, the live
  transfer, twee-pg61, cascade 5,40,80,160,320 with chain level 1, the ratio order with L1=1.73 and L2=1.1), plus:
  * variants k100@0, k200@0, k400@0 and kd@0 (kNN lemma sets of 100, 200 and 400 goals, and proof-dependency
    selection), after unf@0 and k60@0;
  * `--explore 0.2 --explore-labels L1,Vk100@0,Vk200@0,Vk400@0,Vkd@0`: each gets 0.2 CPU hours (12 CPU minutes)
    before its own yield decides. That is about 1 CPU hour of the 12 the run has, mostly in the deep class.
* **Controls:** PGC (19 Nov, same script and machine) and PGA (17 Nov). No new control run.
* **CPUs:** 6 workers plus the transfer's 2 at times. Production goes to 12 workers (ul63 restarted with J=12).

## Measures

* `abs/setcurve.py sets/half1 PGA PGC PGD --at 10,30,60,90,120`. Noise about 185 at 2 hours.
* By level (r1/results.tsv): runs, proofs, CPU, per CPU hour for each label, and the conditional proofs of the new
  members (hints/exp/condvar.py).
* Goals only PGD proved, against PGC and PGA.

## Results

(running; ends about 12:40)

* **Caveat:** from 10:46 to 10:55, a LightGBM fit with default threads ran at 9,000% CPU (load 135; portfolio
  review). This run's minutes 7-16 had less CPU than PGC's had. Its 10 and 20 minute points are biased against
  it; the 60 and 120 minute points less so.

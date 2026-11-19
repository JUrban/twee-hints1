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

## Results (ended 12:39)

* **Caveat:** from 10:46 to 10:55, a LightGBM fit with default threads ran at 9,000% CPU (load 135; portfolio
  review). This run's minutes 7-16 had less CPU than PGC's had. Its 10 and 20 minute points are biased against
  it; the 60 and 120 minute points less so.
  * Runs completed per 3 minutes (results rows' t=), PGC against PGD: minutes 6-9 3,257 against 2,425; 9-12 1,319
    against 1,469; 12-15 866 against 609; 15-18 752 against 715. So PGD lost about 1,100 runs in minutes 6-15, and
    early runs almost all prove. From minute 18 on PGD completed more runs than PGC.
* 30 minutes (11:10): PGD 16,540, against PGC 16,980 and PGA 16,913 (10 minutes: 10,314 against 11,704; 20: 14,300
  against 15,080). The gap is closing.
* **60 minutes (11:40): PGD 18,713, against PGC 18,545 (+168) and PGA 18,529 (+184).** At 45 minutes: 17,976 against
  17,934 and 17,872. PGD has overtaken both, despite the runs it lost to the contention. That is within the noise
  so far (about 185 at 2 hours).

| PGD label, first hour | runs | proofs | CPU h | per CPU h |
|---|---:|---:|---:|---:|
| L0 (5 s) | 17,973 | 16,186 | 4.77 | 3,393 |
| L1 (40 s chain) | 17 | 10 | 0.22 | 46 |
| Vk100@0 | 62 | 14 | 0.07 | 189 |
| Vk200@0 | 45 | 5 | 0.06 | 82 |
| Vk400@0 | 38 | 1 | 0.06 | 17 |
| Vk60@0 | 6 | 2 | 0.01 | |
| Vkd@0 | 34 | 0 | 0.05 | 0 |
| Vunf@0 | 152 | 30 | 0.34 | 88 |

* Against PGC's first 2 hours (L1: 4 runs, Vunf@0 885): exploration gave L1 and the lemma-count members runs early.
  The deep class is still small (351 runs against 17,954 in the r class).

**2 hours (12:39): PGD 19,309, against PGC 18,917 (+392) and PGA 18,987 (+322)** (`abs/setcurve.py`; 19,318 in
solved.tsv once the last runs had ended).

| minutes | 10 | 30 | 60 | 90 | 100 | 110 | 120 |
|---|---:|---:|---:|---:|---:|---:|---:|
| PGA (17 Nov) | 11,467 | 16,913 | 18,529 | 18,875 | 18,912 | 18,941 | 18,987 |
| PGC (19 Nov 07:18) | 11,704 | 16,980 | 18,545 | 18,834 | 18,866 | 18,902 | 18,917 |
| PGD | 10,314 | 16,540 | 18,713 | 19,216 | 19,250 | 19,296 | **19,309** |

* +392 against PGC is about twice the difference between identical runs (185), after PGD had lost about 1,100 runs
  to the contention in minutes 6-15. PGD's second hour added 596, PGC's 372, PGA's 458.
* One-arm goals: only PGD 652, only PGC 251 (union 19,569); only PGD 635, only PGA 305. 485 goals were proved by PGD
  and neither control.

By level (PGD r1/results.tsv, 2 hours):

| label | runs | proofs | CPU h | per CPU h |
|---|---:|---:|---:|---:|
| L0 (5 s) | 21,708 | 16,690 | 9.38 | 1,780 |
| L1 (40 s chain) | 17 | 10 | 0.22 | 46 |
| Vk100@0 | 157 | 17 | 0.20 | 85 |
| Vk200@0 | 149 | 10 | 0.20 | 49 |
| Vk400@0 | 128 | 4 | 0.20 | 20 |
| Vk60@0 | 6 | 2 | 0.01 | |
| Vkd@0 | 159 | 0 | 0.21 | 0 |
| Vunf@0 | 428 | 43 | 1.02 | 42 |

* Where the PGD-only goals (against PGC) were proved: L0 534, the transfer 80, Vunf@0 11, Vk200@0 9, Vk100@0 8,
  L1 6, Vk400@0 4.

## Reading

* **The explored portfolio wins from zero: +392 at 2 hours.** It is the first from-zero gain of the tail machinery
  (exp27 alone was neutral).
* The deep members proved 86 goals themselves, but most of the gain is in 5 s fresh runs: 534 of the 652 PGD-only
  goals. A deep member's proof becomes a sibling lemma and a kNN lemma, and its neighbours then fall to fresh 5 s runs
  in the new context. Checked (12:55, USEDAXIOMS of the proofs): 429 of the 534 PGD-only L0 proofs used a lemma
  that only PGD had proved, 102 used only lemmas PGC had too, 3 used none. That is the chain effect, started earlier and in more places. PGC never measured these
  members: L1 ran 4 times, and no lemma-count member ran.
* The 40 s chain level, starved in PGC (4 runs), got 17 runs with exploration and proved 10.
* Proof-dependency lemmas (kd@0) proved 0 in 159 runs from zero, where in production they make 4.9 per CPU hour.
  From zero the proof-dependency data are thin.
* Caveats: one run per arm, and the controls ran on other days or hours under similar load. The early contention
  biases against PGD, so it does not explain the gain.

## Decision and next

* **solve_new.sh's defaults are now PGD's setting** (19 Nov 12:41): twee-pg61 with PG 0.25 and the branch limit, the
  cascade 5,40,80,160,320 with chain hints from level 1, and DEEP = the members and exploration. `DEEP=` with
  `CASCADE=5,20,80,320 TWEE=/project/bin/twee-e48` gives the 17 Nov system.
* Next: replicate on the other half of the benchmark (half2), PGD's setting against the 17 Nov system, to confirm
  that the gain is not specific to half1's originals.

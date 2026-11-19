# Today's system from zero: half1 in 2 hours with the deep portfolio (exp27)

Started 19 Nov 2026, 07:18 UTC. Script abs/exp27.sh (hints/exp/exp27_run.sh). Part of the
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

## Results (ended 09:18)

`abs/setcurve.py sets/half1 PGA PGC --at ...` (goals of half1 proved):

| minutes | 10 | 30 | 60 | 90 | 100 | 110 | 120 |
|---|---:|---:|---:|---:|---:|---:|---:|
| PGA (17 Nov) | 11,467 | 16,913 | 18,529 | 18,875 | 18,912 | 18,941 | **18,987** |
| PGC (today's system) | 11,704 | 16,980 | 18,545 | 18,834 | 18,866 | 18,902 | **18,917** |
| difference | +237 | +67 | +16 | −41 | −46 | −39 | **−70** |

* **Neutral at 2 hours:** −70 against a noise of about 185 between identical runs. PGC leads in the first hour and
  trails slightly in the second. Only PGA proved 341 goals and only PGC 270, so the union is 19,258.

By level (r1/results.tsv):

| arm | level | runs | proofs | CPU h | per CPU h |
|---|---|---:|---:|---:|---:|
| PGA | 5 s (pool) | 21,257 | 16,537 | 8.92 | 1,855 |
| PGA | 20 s (pool) | 273 | 72 | 2.42 | 29.8 |
| PGA | 80 s, 320 s | 2 | 0 | 0.17 | 0 |
| PGC | 5 s (pool) | 21,836 | 16,335 | 9.36 | 1,746 |
| PGC | Vunf@0 (5 s unfolded) | 885 | 58 | 2.07 | 28.0 |
| PGC | L1 (40 s chain) | 4 | 4 | 0.01 | |
| PGC | Vk60@0 | 1 | 0 | 0.00 | |

* PGC-only goals by where they were proved: 204 at 5 s, 31 Vunf@0, 2 L1, 33 the transfer.

## Reading

* In 2 hours from zero the deep portfolio barely engages. With `--mix 0.1` and 6 workers the deep class has about one
  worker. The ratio order gives it to Vunf@0, whose prior (3.8) and live yield (28-50 per CPU hour) are above L1's
  prior (1.73). So the 40 s chain level ran 4 times, and proved all 4.
* PGA's deep worker ran the 20 s pool level instead, at about the same rate (29.8 against 28.0 per CPU hour). The two
  deep members are equivalent here.
* So today's tail machinery neither helps nor hurts the first 2 hours on a new benchmark half. Its gains are on the
  tail, where production measures them (L1 about 1.9 per CPU hour, the 5 s variants 3-8).
* **The starvation is an exploration problem, the same as production's lemma-set variants in ul60.** L1 was never
  measured because its prior was below the best live member. With an exploration rule (portfolio review: `--explore
  H`), it would get H CPU hours. 4 of 4 proved suggests it would have paid well here.
* No change to solve_new.sh's defaults: neutral at 2 hours. A longer from-zero run (6-8 hours, where the tail begins)
  would be the test that could show the portfolio's value from zero. It costs about 50 CPU hours a pair, so not now.

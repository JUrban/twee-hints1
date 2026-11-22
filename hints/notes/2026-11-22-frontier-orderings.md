# Another term ordering on production's frontier (exp63)

Written 22 Nov 2026, 16:48 UTC.

## Why

* Production (loops/UL) has 3,432 unsolved goals. It has spent 698 CPU hours on them, a median of 47 runs each, and
  1,126 have had a run of 80 s or more. Its last five hours brought 2, 1, 7, 12 and 27 new proofs: about 0.5 per
  CPU hour.
* All of its runs use twee's default KBO precedence. Its variants change hints, lemmas, models and budgets, never
  the term ordering. Only the Prover9-style loops use other orderings (`--p9-orders`, `--precedence`, a fixed
  pseudo-random permutation of the symbols per ordering k).
* On 14 Nov (REPORT 2aa), on 32 stalled gap-1 goals, a fresh 80 s run under another ordering proved 8 (5.9 per
  CPU hour). A new ordering changes which equations are oriented and so the whole completion; on a frontier the
  default has saturated, it is a different search.

## Run

sets/ulu120 (exp/sets/ulu120): 120 of production's 3,379 unsolved unit goals, random.seed(63) over the sorted
list. loops/ULF.ctx: production's solved.tsv at 16:48 (48,352 goals) and a link to its hints. abs/ordtest.sh
(exp/ordtest.sh, PID 2280966): one fresh 20 abstract s run per goal with production's core options (original pool,
rm4t model, 6 + 30 kNN lemmas), two arms at once with 1 worker each: loops/OD (default ordering) and loops/OO1
(ordering 1: `--p9-orders 4 --p9-order-offset 1`).

## Measures

* Proved per arm, one-arm goals, the union; proofs per CPU hour against production's current 0.5.
* Decision: if OO1 proves at least 4 goals OD does not, add an ordering variant to production's variant list (its
  explore/yield rules then judge it), and test orderings 2-3 the same way.

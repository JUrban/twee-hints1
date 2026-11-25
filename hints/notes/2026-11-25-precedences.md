# Other symbol precedences on the quick finals' failures (exp84)

Written 25 Nov 2026, 04:20 UTC.

## Why

* The user (25 Nov): Veroff tries many different symbol precedences to prove subgoals; are we doing that in our
  portfolios? No. Production's variants change hints, lemmas, models and budgets; CLS71 and CLQ83 change the climb
  and the final's time; all of them run under twee's default KBO precedence.
* Earlier tests, all with one or two seeded random precedences (`--p9-orders`, `--precedence`):
  * 14 Nov (REPORT 2x): 32 stalled gap-1 goals, fresh 80 s: another ordering 8 of 32, the default "as well" (4 of 11
    run, stopped). "The ordering is not the main effect."
  * 14 Nov (REPORT, Bigloop test 2): a second ordering per goal and round solved 14 against 9 for one run, at twice the
    wall time; at equal time resume was ahead. Each ordering arm solved one goal no other arm did.
  * 15 Nov (REPORT, the st80 portfolio): orderings 1 and 2 at 20 s on about 35 stalled goals proved nothing beyond the
    base configuration.
  * 22 Nov (exp63, notes/2026-11-22-frontier-orderings.md): 120 unsolved unit goals at 20 s: 0 of 120 for both the
    default and ordering 1.
* None of these ran the climber's final setting (30 siblings, 400 kNN lemmas, fill lemmas and sibling sketch hints),
  and none tried more than two other precedences per goal. The 40 s quick finals (CLQ83) prove about 3 per CPU h on
  targets near a proof, so their failures are the goals where another precedence is the cheapest new search.

## Set and arms

* sets/exp84.targets (exp/sets/exp84.targets): 100 of the 1,728 goals whose CLQ83 final failed and which are still
  unsolved (loops/TRUSTNOW/t0238.trusted and loops/UL/solved.tsv), random.seed(84) over the sorted list; 38 are local
  heads (sets/localheads71), 40 originals.
* abs/exp84.sh (exp/exp84.sh), started 25 Nov 04:18:58 (bash 4052569; loops/EXP84.pids): CLQ83's final (clq83.sh's
  options; set mode, `--targets`, `--runs 0`, `--final-time 160 --final-cpu 40`), -j 1 per arm, five arms:
  * P84O0: twee's default precedence, the control (the context has grown since CLQ83's runs);
  * P84O1-P84O4: ordering k = 1..4, `--p9-orders 5 --p9-order-offset k-1` (without a cascade loop.py takes ordering
    (1 + offset) mod 5), so twee gets `--precedence` with loop.py's fixed pseudo-random permutation of the problem's
    symbols for k (seed 1000003 k + 17; ordering 1 is exp63's).
* Context: t0238.trusted (49,625 goals) with production's hints, CLQ83's true.tsv, fillhints/ and sketches/.
* Checked at 04:19 (each arm's first twee command, the same target aa1_45_c 343): P84O0 no `--precedence`; O1
  `ld,e,l,a,t,k,r,m,rd`; O2 `l,r,k,ld,rd,m,a,t,e`; O3 `e,k,a,r,l,rd,ld,t,m`; O4 `k,r,m,e,rd,ld,l,t,a`; all `--max-cpu 40`.

## Measures and decision

* Per arm: proved, CPU h (climb.tsv), proofs per CPU h; the union of O1-O4; targets only orderings prove (not O0);
  unique per arm.
* Expected cost: 5 arms x 100 targets x at most 40 CPU s, about 5.6 CPU h, about 70-80 minutes.
* **Decision:** if O1-O4 together prove at least 5 targets O0 does not (1 or more per CPU h of the 4.4 CPU h they
  spend, against CLS71's 1.0-1.2 now), add an ordering stage to the quick finals: a target whose default final fails
  gets the next precedence on its next turn, and test more orderings the same way. Else not adopted.

## Result (25 Nov 05:29; exp/exp84_read.py)

| arm | precedence | finished | proved | CPU h | per CPU h |
|---|---|---:|---:|---:|---:|
| P84O0 | default | 100 | 1 | 1.14 | 0.88 |
| P84O1 | ordering 1 | 100 | 1 | 1.14 | 0.87 |
| P84O2 | ordering 2 | 100 | 1 | 1.15 | 0.87 |
| P84O3 | ordering 3 | 100 | 1 | 1.15 | 0.87 |
| P84O4 | ordering 4 | 100 | 1 | 1.14 | 0.87 |

* orderings O1-O4: union 1, not proved by O0 0 (0.00 per CPU h of their 4.58), O0 only 0.
* **Not adopted.** All five arms proved the same one target, nslm_to_aa1 1093, and nothing else: the context had grown
  since CLQ83's failure (its proof uses kNN lemmas and the fill lemmas true_19 and true_49), not the precedence. The
  four orderings add 0 targets in 4.58 CPU h, against the bar of 5.
* The precedences do change the search: the five proofs of 1093 differ (74, 76, 89, 143 and 157 lines; 10.6-17.4 CPU s
  for the final), and every failed target used its 40 s in every arm. So on these targets a different completion is
  no closer to a proof than the default's: they fail for want of hints or lemmas, not because of how the default
  orients the equations.
* With exp63 (0 of 120 at 20 s on production's frontier) and the 15 Nov stalled portfolio, a random precedence has
  now added nothing in three tests on stalled goals; it helped only on 14 Nov, as a second run per goal, at twice
  the time. Not tried: precedences chosen by a rule rather than at random (for example the defined operations
  a, k, l, r, t above or below m, ld, rd), and KBO weights (`--kbo-weight0`).
* nslm_to_aa1 1093 imported into production at 05:41 (P84O0's hints file into loops/UL/hints, then a solved.tsv row,
  as a live climber's proof goes in).

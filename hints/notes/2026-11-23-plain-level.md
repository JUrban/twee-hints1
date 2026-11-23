# A plain level from zero (exp64)

Written 23 Nov 2026, 07:10 UTC, at the launch (it starts 5 minutes after Z9 ends, about 10:51).

## Question

Plain runs (no hints, no rule model, no PG; only sibling and kNN lemma axioms) proved goals that production's hinted
members never did (notes/2026-11-23-conditional.md: PLN1, 24 proofs, 22 of them new, on production's frontier
in 2.71 CPU h of twee runs, 8.1 new per CPU h against production's 0.35). In Z8's final context (PLZ8) they proved 160 of 2,000 of Z8's unsolved goals in
1.88 CPU h, 85 per CPU h, as much as Z8's own late L0 retries (81) but on goals those had failed. Does a plain level
in the from-zero cascade raise the curve?

## Setup

* abs/exp64.sh (exp/exp64.sh): two arms by abs/or_test3.sh, sets/half2 from zero (loops/EMPTY), 4 workers each,
  6 hours, CPU sets 0-6,28-34 (P4A) and 7-13,35-41 (P4B), as exp60's pinned arms; solve_new.sh's defaults (LATE with
  `--knn-drift 5`), transfer every 5 minutes, SCHED= .
* P4A: control. P4B: DEEP is solve_new.sh's with `plk100s40@0` after `unf@0` (loop.py's plain variant, f79acac:
  100 kNN and 40 sibling lemmas, either side, 5 s), `--priors ...,Vplk100s40@0=3` and in `--explore-labels`.
  **Changed 07:57 (before the start):** P4B has two plain levels, `plk100s40@0` and `plk400s130@0` (the live loop's N
  and W settings, which find different proofs: notes/2026-11-23-conditional.md, "Two settings"), each with prior 3
  and in `--explore-labels`. The reading is of the plain levels together.
* It takes Z9C's slot: loops/Z9C.skip (07:10) keeps abs/z9cont.sh from continuing Z9. Z9's 6- and 8-hour readings
  stay; a long-horizon run comes later with the plain level if it pays.
* Proofs: loop.py's proof jobs and exp/proofq.py into loops/P4A/proofs, loops/P4B/proofs.

## Readings

abs/setcurve.py sets/half2 P4A P4B and exp/abscurve.py at 30, 60, 120, 240 and 360 minutes; at 6 hours the one-arm
goals (exp/armdiff.py) and P4B's proofs by the plain level. Rule: +200 or more at 6 hours by wall time and at equal
work; under about 400 it needs a replica pair before production or solve_new.sh change.

## Started

loops/EXP64.pids: P4A 3128630 23 10:52:03; P4B 3128632 23 10:52:03. loop.py PIDs: P4A 3128645 (CPUs 0-6,28-34), P4B 3128644 (CPUs 7-13,35-41); P4B's
command line has both plain variants with their priors and explore labels. Crash watcher from 10:52 on these and
production's processes. Readings at 30, 60, 120, 240 and 360 minutes.

## 1 hour (11:53)

| | 30 min | 60 min | equal abstract work (P4A's 58 min) |
|---|---:|---:|---:|
| P4A | 15,273 | 17,562 | 17,441 at 58 min |
| P4B | 15,303 | 17,602 | 17,395 at 56 min |

P4B +40 by wall time, −46 at equal work. P4B's plain runs so far: 124, 25 proved (the plain levels follow 3 failed attempts,
so they start late). Too early to read.

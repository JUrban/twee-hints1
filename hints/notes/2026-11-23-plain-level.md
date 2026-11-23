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

## 2 hours (12:53)

| | 60 min | 90 min | 120 min | equal abstract work (P4A's 118 min) |
|---|---:|---:|---:|---:|
| P4A | 17,562 | 18,523 | 19,434 | 19,387 at 118 min |
| P4B | 17,602 | 18,601 | 19,669 | 19,472 at 116 min |

P4B +235 by wall time, +85 at equal work. Its plain levels: Vplk100s40@0 34 of 203, Vplk400s130@0 16 of 150 proved.

At the same reading the solved lists: P4B 19,720, P4A 19,470; only P4B 421, only P4A 171. The plain levels proved 50 of P4B's
goals, 6 of them unsolved in P4A: the direct effect is small, so most of P4B's lead is indirect (a plain proof's
steps become hints and its goal a lemma for its neighbours) or the arms' own spread. The 6-hour one-arm goals will
say more; a replica pair is needed before a change either way.

Where the lead is from (12:56, solved lists): only P4B 421 (L0 334, transfer or GML 79, Vplk100s40 3, Vplk400s130 3, Vunf 2), only P4A 161 (L0 127, transfer or GML 23, Vunf 4, L1 2, Vk100 2, Vk200 2). Of
P4B's one-arm goals with a kept output (342), 3 used a plain-proved goal as a lemma. So the lead is in the first
hinted level, not in the plain proofs or their lemmas. The arms' speeds differ: P4A's CPU set ran 1.30 CPU s per
abstract second in hour 1 against P4B's 1.07, so by wall time P4A did less work; the equal-work difference (+85)
is the fair one, and it is within the spread of a replica pair.

## 4 hours (14:55)

| | 120 min | 180 min | 240 min | equal abstract work |
|---|---:|---:|---:|---:|
| P4A | 19,434 | 20,440 | 21,146 | 19,433 at 120 min, 20,439 at 180 min, 21,131 at 238 min |
| P4B | 19,669 | 21,053 | 21,547 | 19,578 at 118 min, 21,046 at 179 min, 21,528 at 237 min |

P4B by wall time: +401 at 240 min; at equal work (the points above, in order): +145, +607, +397.

exp/armdiff.py P4A P4B --at 240:

```
at 240 min: P4A 21146, P4B 21547, P4A-only 87, P4B-only 488, union 21634
P4A-only 87, by how P4A proved them: synced 21, first L0 20, later L0 18, later Vunf 14, later L1 11, later Vk100 2, later Vk200 1
   the proved-by-a-run ones had from P4B (rows so far): 0 runs 1, 1-2 runs 15, 3+ runs 50
   proved at their first run (20): minute of the first run, quartiles: P4A 77/172/212, P4B 101/150/170
P4B-only 488, by how P4B proved them: first L0 233, later L0 92, later Vplk100s40 80, synced 70, later L1 7, later Vplk400s130 3, later Vunf 2, later Vk400 1
   the proved-by-a-run ones had from P4A (rows so far): 0 runs 229, 1-2 runs 124, 3+ runs 65
   proved at their first run (54): minute of the first run, quartiles: P4B 154/165/171, P4A 178/215/231
```

Runs so far by level: P4A L0 21787, Vunf@0 939, Vk100@0 234, Vk200@0 212, Vkd@0 206, Vk400@0 184, L1 127, Vk60@0 5, L2 1; P4B L0 22555, Vplk100s40@0 1549, Vplk400s130@0 239, Vunf@0 227, Vk100@0 199, Vkd@0 198, Vk200@0 189, Vk400@0 172, L1 85.

Now the plain level proves P4B-only goals itself (later Vplk100s40: 80, against 3 at 2 h), and P4B ran Vunf@0 227 times against P4A's 939: the cheap plain runs take goals the unfiltered member would have run, and that work goes to L0 instead (the P4B-only "first L0" goals that P4A has not run yet). The lead grows with time; the 6-hour reading decides, and a replica pair comes before a production change.

## 6 hours (16:53)

| | 120 min | 240 min | 300 min | 360 min | equal abstract work |
|---|---:|---:|---:|---:|---:|
| P4A | 19,434 | 21,146 | 21,541 | 21,697 | 19,433 at 120 min, 21,146 at 240 min, 21,541 at 300 min, 21,687 at 355 min |
| P4B | 19,669 | 21,547 | 21,724 | 21,803 | 19,578 at 118 min, 21,538 at 238 min, 21,723 at 300 min, 21,800 at 356 min |

P4B by wall time: 120 min +235, 240 min +401, 300 min +183, 360 min +106; at equal work (the points above, in order): +145, +392, +182, +113.

exp/armdiff.py P4A P4B --at 360:

```
at 360 min: P4A 21697, P4B 21803, P4A-only 114, P4B-only 220, union 21917
P4A-only 114, by how P4A proved them: synced 27, later L0 27, later Vunf 23, first L0 20, later L1 11, later Vk100 5, later Vk200 1
   the proved-by-a-run ones had from P4B (rows so far): 0 runs 0, 1-2 runs 7, 3+ runs 80
   proved at their first run (20): minute of the first run, quartiles: P4A 179/240/293, P4B 152/181/249
P4B-only 220, by how P4B proved them: later Vplk100s40 62, first L0 58, synced 54, later L0 30, later L1 7, later Vplk400s130 4, later Vk100 2, later Vunf 2, later Vk400 1
   the proved-by-a-run ones had from P4A (rows so far): 0 runs 34, 1-2 runs 53, 3+ runs 79
   proved at their first run (26): minute of the first run, quartiles: P4B 160/174/222, P4A 188/230/260
```

P4B's plain levels over the 6 hours: Vplk100s40@0 201 of 2496 runs proved, Vplk400s130@0 33 of 378 runs proved; the unfiltered member ran 227 times in P4B, 1358 in P4A.

**Reading.** The lead peaked between 3 and 4 hours (+607 at 180 minutes and +397 at 238 in the 4-hour reading, at equal work) and was +113 at 6 hours, under the +200 rule: both arms near the end of what this system proves on half2 in 6 hours, and P4A catching up. So the plain levels make the loop faster rather than stronger: P4B had 21,547 at 240 minutes, a count P4A had not reached at 300 minutes (21,541) and passed before 360 (21,697): about an hour later. solve_new.sh's default is not changed on this; exp65's control is P4B as planned (the plain levels are the frontier lever, and Q5A against P4B gives the spread a replica needs).

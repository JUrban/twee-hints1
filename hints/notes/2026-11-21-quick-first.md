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
* exp/quickstat.py on P2J: its first pass ended at 172 minutes. In 120-180 minutes the last first runs proved 106 of
  2,256 (3.8 CPU hours) while L0 retries in a new context proved 379 of 671 (0.7 CPU hours) once they ran
  (`--retry-class` gives those a share; `--quick` makes the first pass itself cheaper).
* Why first runs only: an L0 retry's proof is slower. Of the retries' proofs, P2J's 17% came within 1 s (60% within
  2 s), P2H's 23% (59%), Z6's 37% (70%), so a quick retry would lose most of them.
* Z6 (all goals, 12 workers): its first pass ended at 169 minutes; in 90-180 minutes its first runs proved 423 of
  8,076 (5%) in 11.5 of the 18 CPU hours, while retries in a new context proved 1,071 of 1,938 at 150-180.
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

**Launch (05:00):** abs/after48.sh (copy in hints/exp; PID 143725 in loops/AFTER48.pid) waits for loops/P2N.done
and loops/P2O.done, then up to 20 minutes for loops/GO49, and starts P2Q (base + `--quick 1`) and P2R (the base)
on half2, 6 workers, 5 hours. The base is P2O's options if P2O ends at least 185 above P2N, else P2N's;
loops/<ARM>.args overrides. Production stays paused.

## Started (21 Nov 09:45)

exp48 ended 09:38 with P2O 21,940 against P2N 21,702 of half2 solved, so abs/after48.sh took P2O's options as the base
B (`--retry-class --yield-discount 2000 --reexplore 12:0.25 --knn-ctx 10 --head-class`). abs/prof12.sh profiled 12
workers for 7 minutes (notes/2026-11-21-dispatch-profile.md) and wrote loops/GO49 at 09:45:18. Started 09:45:32:
**P2Q** = B + `--quick 1` (or_test2.sh PID 401094, loop.py 401107) and **P2R** = B (401097, loop.py 401110); exp50's
P2S beside them at 09:45:47 (403343, loop.py 403368). All three run loop.py with the goal files written at first use
(a145d98); their lemmas.py is the one before the conjecture cache. Crash watcher on the three loop.py PIDs and the
side loops. They end at about 14:50.

## Interim at 1 hour (21 Nov 10:46)

| arm | 15 min | 30 min | 45 min | 60 min |
|---|---:|---:|---:|---:|
| P2R (control, P2O's set) | 12,893 | 15,960 | 17,102 | 18,119 |
| **P2Q** (`--quick 1`) | **13,868** | **16,541** | 16,878 | 17,385 |
| P2S (exp50, `--retry-time 3`) | 12,894 | 16,016 | 17,134 | 18,114 |
| P2O (exp48, 2 arms on the machine) | 13,450 | 16,453 | 17,886 | 18,792 |

* P2Q leads by 975 at 15 minutes and 581 at 30, then trails: −224 at 45, −734 at 60.
* exp/quickstat.py: P2Q made 24,824 quick runs, nearly every goal, and proved 15,306 (62%). In 30-60 minutes they
  proved 133 of 3,754 and 29 of 2,583 (2.2 CPU hours). 8,966 quick-failed goals still wait for their T0 run; those
  that had it proved 457 of 552 (83%).
* P2R made only 16,308 first runs by 60 minutes (96% proved), the near goals first, and beside them deeper runs
  (73 proved) and retries (70). Its mix line: r 16,293, d 353, q 464, h 45 runs; P2Q's r 25,363, d 44, q 41, h 7.
* **Why:** the sort key puts a quick-failed goal after every goal never run, the far ones included (`(nf,
  quick-failed, orig-rate bin, near/far, ...)`). So P2Q's class r quick-ran the whole far tail before any T0 run of
  a near quick-failed goal. And a quick-failed goal is neither failed (no retry class q) nor tried in its context
  (no deeper level, no head), so classes d, q and h had almost nothing to run.
* The fix for a second try: near/far before quick-failed in the key, so a near goal's T0 run comes before a far
  goal's quick run. The A/B goes on unchanged; P2Q may still catch up as its T0 runs prove at 83%.
* P2R is 673 behind P2O at 60 minutes, with the same options: three arms and their side loops load the machine more
  than exp48's two (load average about 30). At 10:47 the proof worker and the sweep were stopped to bring that down;
  they restart after exp49/50.

## The fix as an option: `--quick-near` (10:48)

loop.py `--quick-near` (default off): with --quick, the --fail-order key is (failures, far, quick-failed, orig-rate
bin, gap lines, goal number) instead of (failures, quick-failed, orig-rate bin, far, ...). A near goal's T0 run after
its failed quick run then comes before a far goal's quick run.

Smoke test loops/QKN (10:48, smoke487, 2 workers, 12 minutes, `--quick 1 --quick-near`): no errors, 402 solved (QKT
and QKC 395; one run each, so no comparison). In its first 2 minutes it made 348 quick runs (308 proved) and 33 T0
runs after a failed quick run (28 proved); QKT made only quick runs then (471, 323 proved) and its T0 runs came after
2 minutes. If P2Q loses at 5 hours, the second try is `--quick 1 --quick-near` against the same base.

## Interim at 2 hours (21 Nov 11:46)

| arm | 60 min | 90 min | 120 min |
|---|---:|---:|---:|
| P2R (control) | 18,119 | 19,356 | 20,234 |
| P2Q (`--quick 1`) | 17,385 | 18,607 | 19,607 (−627) |
| P2S (`--retry-time 3`) | 18,114 | 19,380 | 20,300 (+66) |
| P2O (exp48) | 18,792 | 20,084 | 20,934 |

* P2Q's T0 runs after a failed quick run: 1,764 proved of 3,236 so far (554 per CPU hour; in 90-120 minutes 595 of
  1,317), and 6,282 quick-failed goals are still waiting. P2R's first runs in the same window: 502 of 1,247 (about
  390 per CPU hour); its first pass ended only at 121 minutes, since classes d, q and h share the workers.
* P2Q is catching up slowly (−734 at 60 minutes, −749 at 90, −627 at 120).
* Load: the arms' own processes are about 25 running; the machine's load average rose to 43 at 11:46 from outside
  this sandbox, so all three arms are slower than P2O was at the same minutes.

## Result: stopped at 3 hours (21 Nov 12:47), `--quick 1` rejected

| arm | 120 min | 150 min | 180 min | vs P2R at 180: +, −, union |
|---|---:|---:|---:|---|
| P2R (control) | 20,234 | 20,929 | 21,264 | |
| P2Q (`--quick 1`) | 19,606 | 20,100 | 20,545 (−719) | +225, −959, 21,508 |
| P2S (exp50) | 20,300 | 20,761 | 21,098 (−166) | +206, −389, 21,489 |

All three arms were stopped at 12:47 instead of at 5 hours: P2Q would have needed about 900 more than P2R in the last two
hours, while its remaining T0 runs after a failed quick run proved 27% (199 of 737 in 150-180 minutes; 4,905 still
waiting). Its 225 goals that P2R lacks are at the level two identical runs differ by (about 200), so it is no portfolio
member either.

What the test showed: the quick runs themselves are cheap and productive (15,306 proofs at 3,330 per CPU hour, 62% of
the goals at 1 s), but failing them sorts a goal after the far tail, and the goals that need 1-5 s then wait for
an hour or more. The early lead (+975 at 15 minutes) is the value of a 1 s first pass; the loss is the ordering after
it. `--quick-near` (smoke QKN) fixes the order; it is a candidate for a later, short A/B (2 hours is enough, since the
difference shows in the first pass), not for Z7.

## The portfolio check (21 Nov 14:30)

The portfolio rule is: report +/−, the union, and the union per CPU hour against a time-matched control.
* Union per CPU: P2R ∪ P2Q at 3 hours each (36 worker-hours) has 21,508 goals; P2R ∪ P2S has 21,489. P2O alone at 5
  hours (30 worker-hours) has 21,940. So a single longer run beats either pair, by about 430-450 with fewer worker-hours.
  Caveat: P2O ran under a lighter load, which can be worth 167-426 (notes/2026-11-21-late-combo.md).
* Unique proofs: among the three arms, P2Q 132, P2S 112 and the control P2R 253. None is new to the whole collection
  (all other runs and production's 48,234).
* Why this was expected: with --abstract-time, a 1 s or 3 s run is a prefix of the same 5 s run, so these options
  change only when a proof is found, not which proofs exist. Their one-arm goals come from scheduling (contexts at
  different times), as between two identical runs. A complementary member has to search differently (other hints,
  lemma sets, options, provers).

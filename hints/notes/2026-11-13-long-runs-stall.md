# Long runs: how long runs stay on hints, the whole-pool advantage, and resumed rounds

*Reconstructed on 17 Nov from REPORT 2m and the session's commands (13 Nov 10:10 – 14 Nov morning). Abstract
time.*

**Question.** The user, 12 Nov 20:51: "hints are usually useful in harder proofs that run for longer (and get
eventually lost without hints); veroff would typically stop a job if there is no hint matcher after many given
clauses". So: in long runs, does a gap without new hint matches predict failure? Do hints help more in long
runs, and which pool?

**Setup.**
* **Replay:** twee-e16 prints `HINTLOG` (the critical-pair count of each hint's first match). With abstract
  time a run is deterministic, so stallsim.py replays every stall limit G from one long run: the run stops
  at the first gap of G without a new match, and the proof counts if it came before that.
* **fam_long** (sets/fam_long, 13 Nov 10:11): 60 goals, 30 each of aK2_eq_aK3_d and nil3_30, unsolved by the
  full-benchmark loop (loops/ALL_lem).
  * Chosen as the unsolved goals with the most solved goals among the 10 before them, ties to the lower goal
    number. REPORT 2m says "the first 30 unsolved", which is wrong: the set favours lemmas.
  * 120 abstract s (240k critical pairs), rm4t, 3 sibling lemmas + 10 subset-kNN lemmas, kNN hints (median
    144, at most 200).
* **v2_hard** (abs/v2.sh): the 8 fam_long failures plus the next 30 unsolved goals of each original, 68 in all.
  * 300 abstract s with rm4t and the same lemmas, CPU cap 1,200 s, `--keep-out`, -j 9, twee-e18.
  * Arms: V2p, whole original pool (all lemmas of solved siblings, most frequent first: 1,994 hints for
    aK2_eq_aK3_d, 1,693 for nil3_30); V2k, kNN 30:200; V2n, no hints.
* **Later rounds** on what V2p left: abs/v2r2.sh (900 abstract s, stall gap 60 s, CPU cap 3,600 s, states
  kept), v2r3.sh (resume), v2r4.sh (resume redone with twee-e20).
* **Prover9 long runs** (p9_long.sh, long/P1 and long/P0): fam2_long, 40 fam2 goals the short loop left, 3,000
  given clauses, hints = all proof steps of the solved siblings.

**Results.**

fam_long, 120 abstract s, by stall limit:

| stall limit (abstract s) | 5 | 10 | 20 | 30 | 45 | 60 | none |
|---|---:|---:|---:|---:|---:|---:|---:|
| solved (with hints) | 33 | 37 | 43 | 49 | 51 | 52 | 52 |
| work (abstract h) | 0.09 | 0.13 | 0.19 | 0.22 | 0.25 | 0.27 | 0.30 |

* No hints 51, with hints 52.
* Proofs came at quartiles 1, 4, 20 and 78 s. The last new matches of solved runs came at 0.7, 2.3, 9.7 and
  43.5 s.
* The 3 unsolved runs had matched 41 of 76, 50 of 76 and 106 of 200 hints.

v2_hard, 300 abstract s:

| arm | solved | against no hints |
|---|---:|---|
| whole pool (V2p) | **48** | +13 −1 |
| kNN 30:200 (V2k) | 40 | +5 |
| no hints (V2n) | 36 | |

* All 19 V2p failures hit the CPU cap at 115–261 abstract s, still matching hints (520–690 matched, the
  last near the end).
* kNN runs stopped matching early: the last new match at a median of 3 abstract s, in solved and unsolved
  runs alike.
* Cost of large pools: in the same search, 1,994 hints cost +53% CPU. The abstract clock did not move during
  housekeeping, so hint normalisation ran every 40 critical pairs. Tasks now charge an abstract cost
  (`newTaskCost`, twee-e19): +11%.
* 48% of the new proofs' lemmas were already in the pool (8,196 in 48 proofs).

Later rounds:

| round | runs | solved | total of 68 |
|---|---|---:|---:|
| 2: fresh, pools + round-1 proofs, 900 abstract s | 20 | 13 | 61 |
| 3: resume states with round-2 proofs | 7 | 1 | 62 (invalid: signature bug) |
| 4: round 3 redone with twee-e20 | 6 | 2 | 64 |

* In round 2, 7 were solved by 60 abstract s, 9 by 120, 12 by 300 and 13 by 600. Four took under 15k
  critical pairs where round 1 had failed at 230k–520k.
* In round 4 resuming cost most of the CPU. On nil3_30__goal_355 (477 MB state, 111k rules, 19.4M queued
  pairs): loading took 130 s, normalising hints 5 s, and re-scoring the queue 333 s.

Prover9 on fam2_long: with hints 18, without 16 (13 both), at the same CPU. Proofs came late (median 997
givens with hints). A 750-given gap limit would keep 7 of the 18.

**Reading.**
* **The stall signal only means something with a large pool.** With small kNN lists, falling off the hints
  means "list used up". With the whole pool, runs keep matching until late, so the signal does not separate
  winners from losers either. For Prover9 too, "still on hints" did not predict success.
* The whole pool beats kNN at long limits (48 against 40). At 2 s it was the other way round
  (2026-11-12-hint-selection.md).
* **Abstract time is not constant work.** Late pairs on big rule sets cost more (goal_336: 270 pairs per CPU
  second). Five fam_long runs fell below 300 per second and the wall-clock kill lost their output.
  `--max-cpu` (twee-e18) now stops cleanly.
* The round-3 failure was a bug, not a finding (resumed problems with new lemmas got a second signature).
* The sets are two originals and chosen near solved goals, so they favour lemmas and siblings' hints. The
  numbers say what the loop does on such frontiers, not on hard problems in general.

**Decision and next.** Whole-original pools for long runs; no stall cutoff; `--max-cpu` as the safety limit;
states kept for resumes. REPORT 2m.

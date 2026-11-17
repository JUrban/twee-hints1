# Veroff's P9loop and Bigloop in twee, against resuming the saved search

*Reconstructed on 17 Nov from REPORT 2w and the session's commands (14 Nov 14:00–23:00). Abstract time.*

**Question.** The user, 14 Nov ~17:00, on Veroff's AITP 2026 slides: a P9loop reruns the target theorem over and
over, keeping every hint matcher of each failed run as an extra input lemma for later runs, and cycling term
orderings (36 per P9loop in the NIL3 proof). A Bigloop runs several P9loops at once sharing one lemma pool (in
the NIL3 proof, 1,155 of 3,594 steps were Bigloop lemmas). Does this beat continuing the saved search?

**Setup.**
* twee-e30 `--print-hint-matchers`: every rule matching a hint, as TPTP (`HINTMATCHER n fof(...)`).
* loop.py:
  * `--p9loop` keeps a goal's matchers in DIR/p9lem/<goal> as axioms for its later runs. They are consequences
    of the axioms and lemmas, so sound; matchers with a skolem of a conditional goal are dropped.
    `--p9-max N` keeps the most recent N.
  * `--p9-orders N` gives attempt k its own KBO precedence (a seeded shuffle; attempt 1 is twee's default).
  * `--p9-parallel P` is the Bigloop: P runs per goal and round at once, sharing the pool.
* **Test 1:** sets/u3n73 (14 Nov 14:10), the 73 of u3n150 (nil3_31) that N3x6 (20 s, production config) left
  unsolved, from all of N3x6's proofs (loops/N3xI). 4 rounds of 20 abstract s. Arms: P9loop with matcher
  lemmas only; P9loop + a new ordering each round; resume.
* **Test 2** (abs/bl.sh, from 16:08):
  * sets/fr100: 100 goals (88 originals) drawn with seed 11 from fr150. Those are goals the full loop failed
    at 20 s in round 4 whose nearest lower sibling is proven (gap 1).
  * From loops/ULsI (a snapshot of the full loop's 40,961 proofs), production config, twee-e30, 2 workers
    per arm, 80 abstract s per goal in all.
  * Arms: BRS resume ×4 (the saved queue re-scored); BRSn resume ×4 with `--no-resume-requeue`; BP9 P9loop
    with 4 orderings ×4; BBL Bigloop with 2 orderings at once ×2.

**Results.**

Test 1 (73 goals):

| arm | after rounds 1 / 2 / 3 / 4 | wall per goal and round |
|---|---|---|
| P9loop, matcher lemmas only | 1 / 3 / 3 / 3 | 39–43 s |
| P9loop + a new ordering each round | 1 / 1 / 2 / 2 | 40–57 s |
| resume | 1 / 3 / stopped | 55 s, then 115 s |

* After round 2 the matcher lemmas reach the same hint coverage as resuming (2,220 of 3,728 hints joined
  against 2,214) in half the wall time.
* Lemmas pile up: about 880 per goal after round 1, 1,440 after round 2. New matchers dry up (about 115 per
  run in round 3).
* Orderings derive different matchers: in a 1 s test of one goal, 204 with the default against 528 with
  another.

Test 2 (fr100):

| arm | after rounds 1 / 2 / 3 / 4 | wall (sum over runs) |
|---|---|---|
| BRS, resume, queue re-scored | 9 / 17 / 23 / 26 | 7.8 h for 4 |
| **BRSn, resume, queue as saved** | 9 / 18 / 27 / **29** | 5.3 h for 4 |
| BP9, P9loop + orderings | 9 / 16 / 18 / 18 | 4.1 h |
| BBL, Bigloop, 2 orderings per round | 14 / 19 | 4.2 h |

All four together solved 33. Only BRSn solved 4 of them; BP9 and BBL one each.

**Reading.**
* **On goals next to a proof, keep searching rather than restart:** 27 against 18 at the same 4.1 h.
  P9loop stalls after round 2 in both tests.
* Re-scoring the saved queue costs 20–55 s per resume and buys nothing (26 in 7.8 h against 29 in 5.3 h).
* A second ordering solves 14 against 9 in round 1, at twice the wall time. At equal time resume is still
  ahead (18 at 2.9 h against 14 at 2.6 h). Orderings are a candidate for stalled resumes.
* Veroff's loop gets its strength from many orderings and many runs per hard theorem. Here each arm had
  80 abstract s per goal. Test 1's 73 goals are very hard: four 20 s rounds add only 2 in any arm.
* fr100 is the frontier as the cascade sees it (gap 1), which favours resume and lemmas.
* Our test only takes the matchers as lemmas. Veroff's practice also expands proofs back to the axioms to
  grow the hint lists (the user, 17 Nov); that is 2026-11-17-expanded-proofs.md.

**Decision and next.** The full loop resumes with `--no-resume-requeue` (round 5 continued at 19:35). P9loop
and orderings parked. REPORT 2w.

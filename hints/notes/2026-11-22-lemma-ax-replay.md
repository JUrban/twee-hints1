# The lemma-axiom fix replayed on a from-zero live loop (exp58a)

Written 22 Nov 2026, 12:57 UTC.

## Question

exp56 (notes/2026-11-22-gm-retry.md) found that given-rule sketches from failed runs lacked the source run's lemma
axioms, and fixed it in givenmatch.py (`live --lemma-ax`). In production the fix turned 0 of 30 into 12 of 25 at the
20 s ancestry pass. Should solve_new.sh's live loop use it from zero, and is a 6-hour from-zero pair (the planned
exp58) worth it?

## The bound

In Z8's live loop (loops/Z8_GML, from zero, 22 Nov 02:53-08:55):
* 765 ancestry-pass runs proved 665, and the 40 s prefix pass then proved 40 of 95.
* 59 goals had an ancestry run and no proof by any pass. Z8 later solved 23 of them by other routes.
* The other failures of that loop (682 goals in all) were same-statement runs, which the fix does not touch.

So from zero the fix can change at most 59 goals at 6 hours, well below a from-zero pair's noise (up to about 400
across times, about 100-185 side by side). The 6-hour pair is dropped; this replay measures the fix directly.

## Replay

exp/gmreplay.py loops/Z8_GML loops/Z8 loops/GMRP -j 1 --control 15 (seed 58), with Z8's live-loop transfer arguments
(solve_new.sh's MOD, `--pool original --twee twee-pg61 --wall-factor 15 --args="--abstract-time 2000
--no-eqhint-consider"`, TWEE_PG_ARGS as solve_new.sh). For each of the 59 goals:
* the context is Z8's goals whose hint file is older than the goal's sketch files, i.e. what the live loop had at the
  time of its run;
* arm lax: copies of the same sketch files, with givenmatch.lemma_ax applied with that context's goals;
* arm ctl, 15 goals drawn with seed 58: the copies unchanged, to check that the replay reproduces the failures;
* 20 s, `--src-lemmas 6`, 1 worker, as the live loop's first pass. Rows in loops/GMRP/replay.tsv.

Started 12:57 (PID 2059788), log loops/GMRP.log. A first launch at 12:56:50 stopped at once: lemma_ax kept the newline
in the last path of a two-column goals file (the live loop's files have three columns). Fixed in givenmatch.py.

## Measures and decision

* lax: proved of 59, and of the 36 Z8 never solved; for the 23 it solved later, how much earlier.
* ctl: proved of 15. If the replay reproduces the failures (at most 2 of 15 proved), lax's count is the fix's effect.
* Decision: if lax proves at least 10 more than the control rate predicts, solve_new.sh's GIVENARGS get `--lemma-ax`
  before exp55 starts (both arms then have it), as a bug fix without a from-zero pair.

## Result (22 Nov 13:26; the replay ran 12:57:10-13:21:35)

| arm | goals | proved | CPU h |
|---|---:|---:|---:|
| lax (named lemma axioms) | 59 | **46** | 0.17 |
| ctl (sketches as the live loop had them) | 15 | 0 | 0.14 |

* The control reproduces the live loop's failures: 0 of 15. On the same 15 goals lax proved 12.
* Of the 36 goals Z8 never solved, lax proved 27. Of the 23 it solved later by other routes, lax proved
  19, a median of 19 minutes earlier (from 0 to 115).
* Soundness, on the 46 proofs (exp/proofq.py rerun, 13:22-13:25, no NOPROOF): the proofs have 597 axiom lines. 282 are the
  original's axioms; the other 315 are skax_<i>_<goal> 164, lemma_knn 116, srclem 24 and lemma_goal_J 11. Every one
  names a goal in that run's context (proven before the run), never the target, with axioms within the target's.
  One lemma_goal_J is a later sibling (456 for 453), which `--lemma-after` allows; it was proven at the time.
* **Decision: solve_new.sh's GIVENARGS default now has `--lemma-ax` (13:26).** exp55's two arms copy solve_new.sh at
  their start (about 15:20), so both have it, and the knn-drift comparison stays like for like.
* From zero, this adds at most about 27 goals at 6 hours to a run like Z8, plus the 19 earlier: within the noise of
  a from-zero comparison, which is why there is no from-zero pair.


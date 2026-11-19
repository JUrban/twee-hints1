# The explored portfolio from zero on the other half of the benchmark (exp30)

Written 19 Nov 2026, 12:42 UTC, at launch. Script abs/exp30.sh ([hints/exp/exp30_run.sh](../exp/exp30_run.sh)).
Follows exp29 ([notes/2026-11-19-from-zero-explore.md](2026-11-19-from-zero-explore.md)).

## Why

* exp29 on half1: PGD 19,309 at 2 hours, against the 17 Nov system (PGA) 18,987 and this morning's PGC 18,917.
  solve_new.sh's defaults became PGD's setting at 12:41.
* That was one run per arm, on one half, with the controls run at other times. A replication on the other half
  (different originals), with both arms at once on the same machine load, tests whether the gain holds.

## Set and setting

* **Set:** sets/half2, the 65 originals not in half1, 25,847 goals ([hints/exp/sets/half2](../exp/sets/half2)).
  From zero: context loops/EMPTY.
* **Script:** abs/or_test2.sh, which is abs/or_test.sh with the set as a parameter. That means solve_new.sh, 6
  workers, 2 hours, the live transfer every 300 s, `SCHED=`.
* **P2A (control): the 17 Nov system,** PGA's setting: `DEEP= CASCADE=5,20,80,320 TWEE=/project/bin/twee-e48`
  (PG 0.25), so no chain level and no variants.
* **P2D: solve_new.sh's new defaults,** PGD's setting:
  * twee-pg61 with PG 0.25 and the branch limit 100;
  * cascade 5,40,80,160,320 with chain hints from level 1;
  * the 5 s members unf@0, k60@0, k100@0, k200@0, k400@0 and kd@0, and the 80 s variants;
  * `--ratio-order --explore 0.2` for L1 and the lemma-count members.
* **CPUs:** 2 × (6 + the transfer's 2 at times). Production goes to 4 workers for the 2 hours (ul64 with J=4).
* rm4t, the rule model of both arms, was trained on public proofs, including half2's. So "from zero" is not
  fully clean, but it is the same for both arms.

## Measures

* `abs/setcurve.py sets/half2 P2A P2D --at 10,30,60,90,120`. Noise between identical runs on half1: about 185 at
  2 hours.
* One-arm goals, and where P2D's came from (exp29/ana.py, adapted).
* If P2D ≥ P2A + 185, the gain replicates. If within noise, half1's +392 was partly luck, and the defaults stay
  (they do not lose). If P2D loses by more than the noise, revisit the defaults.

## Results

(running; ends about 14:45)

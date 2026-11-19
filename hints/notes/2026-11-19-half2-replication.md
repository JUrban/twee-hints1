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

## Results (ended 14:46)

`abs/setcurve.py sets/half2 P2A P2D --at ...` (goals of half2 proved):

| minutes | 10 | 30 | 60 | 90 | 120 |
|---|---:|---:|---:|---:|---:|
| P2A (17 Nov system) | 11,489 | 17,345 | 19,041 | 19,442 | **19,501** |
| P2D (new defaults) | 11,369 | 17,397 | 18,963 | 19,323 | **19,383** |
| difference | −120 | +52 | −78 | −119 | **−118** |

* **Not replicated: −118 at 2 hours, within the noise of about 185.** Half1 gave +392 with the same comparison
  (exp29, PGD against PGA's 17 Nov run).
* Only P2D proved 295 goals, only P2A 414; the union is 19,798 (+297 over P2A alone).

By level (`exp/exp30_ana.py`):

| arm | level | runs | proofs | CPU h | per CPU h |
|---|---|---:|---:|---:|---:|
| P2A | L0 (5 s pool) | 20,984 | 16,719 | 8.04 | 2,080 |
| P2A | L1 (20 s pool, resumed) | 283 | 82 | 2.29 | 35.8 |
| P2A | L2 (80 s) | 43 | 5 | 1.31 | 3.8 |
| P2D | L0 (5 s pool) | 22,377 | 16,979 | 8.95 | 1,898 |
| P2D | Vunf@0 | 632 | 50 | 1.45 | 34.4 |
| P2D | Vk100@0 | 175 | 18 | 0.20 | 89.1 |
| P2D | Vk200@0 | 164 | 11 | 0.20 | 54.7 |
| P2D | Vk400@0 | 144 | 3 | 0.20 | 14.8 |
| P2D | Vkd@0 | 166 | 1 | 0.20 | 5.0 |
| P2D | L1 (40 s chain) | 14 | 6 | 0.20 | 29.7 |

* One-arm goals by where they were proved:
  * P2D: 220 at 5 s, 38 by the transfer, Vunf@0 15, Vk100@0 10, Vk200@0 8, L1 2, Vk400@0 2.
  * P2A: 296 at 5 s, 67 by the transfer, L1 47, L2 4.

## Reading

* **Deep work is about equal in both arms.**
  * P2A's 20 s pool level made 35.8 proofs per CPU hour, and 47 goals only P2A proved came from it.
  * P2D's deep members made 89 proofs in 2.65 CPU h (34 per CPU hour), and 37 goals only P2D proved came from
    them.
  * The rest of the one-arm goals are 5 s runs and transfers, which differ by chance (twee's chaos) in both
    directions: 220 against 296.
* **So half1's +392 was mostly luck at the 5 s level.** Pooled over both halves, the new defaults are +137 per half
  (+392 and −118), below the noise of one pair. They do not lose, and they do not win either.
* **The 20 s pool level is a member P2D lacks.** It runs from the 5 s state (a resume), at about the yield of the best
  5 s lemma members. P2D's cascade goes 5 → 40 s with chain hints. Its L1 ran 14 times and proved 6 (29.7 per CPU
  hour), and the explore rule gave it only 0.2 CPU h.
* The explore budget (0.2 CPU h each) ran out for every member within the first hour. After that the ratio order
  gave the deep worker to Vunf@0 (1.45 CPU h).

## Decision

* solve_new.sh's defaults stay (no loss), but **REPORT no longer claims a from-zero gain**: +392 on half1, −118 on
  half2.
* **Portfolio follow-up:** the 20 s pool resume as a member beside the 5 s lemma members, with a measure of the
  union. A test should give both new and old members the same deep CPU, since the arms' deep work tied here.
  Not started: from-zero pairs cost about 25 CPU hours, and the union (+297) is the target, not either arm.

Interim, 13:45 (`abs/setcurve.py sets/half2 P2A P2D`, goals of half2 proved):

| minutes | 10 | 30 | 45 | 60 |
|---|---:|---:|---:|---:|
| P2A (17 Nov system) | 11,489 | 17,345 | 18,422 | 19,041 |
| P2D (new defaults) | 11,369 | 17,397 | 18,406 | 18,963 |
| difference | −120 | +52 | −16 | −78 |

* Level so far. On half1 the same comparison was +184 at 60 minutes (PGD 18,713 against PGA 18,529) and +322 at
  120, so half1's gain has not appeared yet. Half1's gain grew in the second hour, from the deep members' cascades.
* P2D's levels at 60 minutes (`levyield.py loops/P2D/r1/results.tsv 1`):
  * L0: 18,893 runs, 16,663 proofs, 4.76 CPU h;
  * Vunf@0: 37 proofs in 0.37 CPU h (99 per CPU h);
  * Vk100@0: 10 in 0.08;
  * L1: 6 in 0.20;
  * Vk200@0: 3, Vk400@0: 2, Vkd@0: 1.

# The whole benchmark from zero, and a faster dispatcher

*Reconstructed on 17 Nov from REPORT 2as (16 Nov 23:49 – 17 Nov 03:02). Abstract time; counts by proof-file times.*

**Question.** What does the final system do on all 51,784 public problems from zero, with no context? And why were
the workers idle?

**Setup.**
* **Z0** (abs/z0_test.sh, from 23:49): solve_new.sh with an empty context, no learned scheduler (from zero it
  needs `--sweep-first`, which at this size would run every goal once before any retry), transfer every
  5 minutes, 12 workers.
* **Profile:** cProfile of the same start (3 workers, 4 minutes). Three changes:
  * `ctx()` cached per original (b1bb8c5);
  * kNN picks memoised in the lemma index (c9d1341);
  * `--pass-every 1` (a2b03ec): the full scheduling pass at most once a second.
* **Check:** PE1, rp3 from zero with `--pass-every 1`, against LVZ.
* **Z1** (abs/z1_test.sh, from 00:56): Z0 with the new dispatcher, 12 workers, stopped at 126 minutes.

**Results.**

| minutes | 2 | 5 | 10 | 15 | 20 | 30 | 45 | 60 | 90 | 120 | 126 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Z0 | 600 | 1,877 | 6,215 | 12,001 | 17,435 | 22,979 | 28,909 | 32,475 | | | |
| **Z1** | 1,167 | 2,064 | 7,942 | 15,460 | 22,165 | 28,996 | 32,664 | 34,181 | 35,514 | 36,552 | **36,760** |

| change | runs in the first 1 / 2 / 3 minutes (12 workers) |
|---|---|
| none (Z0) | 872 / 1,403 / 1,765 |
| `ctx()` cached | 1,030 / 1,596 / 1,905 |
| + kNN picks memoised (30.7 → 16.8 ms a goal) | 1,058 / 1,605 / 1,916 |
| + `--pass-every 1` | **1,454** / 1,872 / 2,079 |

* Z0's busy workers by 10-minute window: 4.8, 2.7, 3.7, 5.3, 7.3 of 12. The main thread ran at 100%; `ctx()`
  took 260 of 472 s (43M calls).
* PE1: 733, 809, 830 at 4, 10, 15 minutes against LVZ's 732, 806, 830.
* Z1: busy workers 8.1–11.9 of 12. Production (44,841) has 8,116 proofs Z1 lacks; Z1 has none production lacks.
* **Every one of Z1's 34,579 runs was at the first level (5 s).** 12,998 of its 15,062 unsolved goals never ran;
  the other 2,064 were retried, many 6 or more times. 6,080 of production's 8,116 extra proofs are on goals Z1
  never ran.

**Reading.**
* **In 50 minutes on 14 CPUs, Z0 matches plain twee at 4 s on the whole benchmark** (31,060 in 28 CPU h). Z1 is
  +30% at 20 minutes.
* The transfer did about 12k of Z0's proofs: goals that are instances of, or steps of proofs of, proven goals of
  other originals with the same or weaker axioms.
* **These counts are lemma-assisted.** Most come through siblings, kNN lemmas or transfer
  (2026-11-17-lemma-circularity.md: from zero, 14% of recorded proofs use no lemma).
* **The dispatch order is the flaw.** Near retries go first and there is always one waiting on 51,784 goals, so
  goals beyond the gaps never run. Replays (PE1: 438 of 489 unsolved never run) and production (4,114 of 6,943
  not run in round 5) have it too.

**Decision and next.** solve_new.sh passes `--pass-every 1` (production kept 0). The dispatch order became the next
experiment (2026-11-17-mix-fail-order.md). REPORT 2as.

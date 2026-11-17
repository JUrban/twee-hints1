# Distance in proof lines, and stalled goals: run fresh with new hints rather than resume

*Reconstructed on 17 Nov from REPORT 2z–2aa (14 Nov evening). Abstract time.*

**Questions.**
* The user, 14 Nov: goal numbers are not the real distance. Does the proof-line distance to the nearest proven
  goal predict success better than the goal-index gap?
* Goals that fail their resume to 80 s: should they resume further, run fresh, or run with another ordering?

**Setup.**
* **Proof lines:** each LADR problem file gives its goal's line in the original Prover9 proof
  (`% goal_313 line_1531`). Goals were picked in stripes 3, 5, 8, 13, 21, 34 and 55 lines apart. The original
  proofs are not available, so the parents of a step are unknown.
* **Replay:** the full loop's round 5 in order, measuring each run's line distance to the nearest proven goal
  below it at run time.
* **sets/sg1:** 32 gap-1 goals that failed L1 (resume to 80 abstract s) in round 5. All arms from the snapshot
  loops/ULsJ (41,473 proofs), production config:
  * SG1: resume to 320 s, as the cascade's L2;
  * SO: fresh 80 s, another term ordering;
  * SD: fresh 80 s, default ordering;
  * S20: fresh 20 s;
  * SG2 for comparison: gap-2 goals, L0 state resumed to 80 s (48 goals).

**Results.**

| distance to the nearest proven goal below | L0 retries (20 s) | L1 (resume to 80 s) |
|---|---:|---:|
| ≤ 8 lines | 9/29 (31%) | 36/100 (36%) |
| 9–13 lines | 69/216 (32%) | 125/495 (25%) |
| 14–21 lines | 36/172 (21%) | 47/296 (16%) |
| 22–34 lines | 29/219 (13%) | 37/155 (24%) |
| 35–144 lines | 41/356 (12%) | 11/75 (15%) |
| index gap 1 / 2 / 3 | 22% / 12% / 14% | 23% / 17% / 40% (5 runs) |

| arm (sg1) | solved | proofs per CPU-hour |
|---|---|---:|
| SG1, resume to 320 s | 0 of 13 run (stopped) | 0 |
| SO, fresh 80 s, other ordering | 8 / 32 | 5.9 |
| SD, fresh 80 s, default ordering | 4 of 11 run | 12 |
| S20, fresh 20 s | 4 / 32 | 14 |
| SG2, gap-2 goals resumed to 80 s | 5 / 48 | 2.8 |

None of the sg1 goals had a new sibling lemma since its last fresh run, but their pools had grown by up to 75%:

| pool growth since the last fresh run | S20 | SO |
|---|---:|---:|
| < 10% | 0/12 | 1/10 |
| 10–25% | 1/11 | 3/13 |
| ≥ 25% | 3/9 | 4/9 |

The full loop's rate (round 5, about 16 workers): 129 proofs an hour with re-scoring off (19:35–20:13), 203 an
hour with consider-emulation also off (20:15–20:57).

**Reading.**
* Line distance predicts success at L0 (31% near, 12% far). At L1 the trend is weaker and not monotone
  (22–34 lines: 24%).
* **Resuming does not use new hints.** The saved queue was scored without them, and since `--no-resume-requeue`
  is never re-scored. A fresh run with a grown pool does use them.
* The ordering is not the main effect (SD as good as SO). SD was stopped at 11 goals, so its rate rests on 4
  proofs.
* sg1 is small (32): the pool-growth table rests on 8 and 4 proofs. It motivated a rule, not a measured gain.

**Decision and next.**
* `loop.py --line-gaps R,F` (6b76a1b) orders retries and deepening by line distance and admits within R and F
  lines. The full loop runs with `--line-gaps 21,13` from 20:58. Admission barely changed (1,407 against
  1,406); the gain is in the order.
* `loop.py --retry-hints G` (4a34404) retries a goal fresh when its pool has grown by G since its last fresh
  run. In the full loop with 1.25 from 22:28.
* REPORT 2z, 2aa.

# A learned scheduler for the cascade, stalled goals, and tail heads

*Reconstructed on 17 Nov from REPORT 2ac (15 Nov 01:30–07:40). Abstract time per run; arms compared by proofs
over wall minutes from the same copy of UL.*

**Question.** With fresh runs ahead of resumes (UL14: about 610 proofs an hour against UL13's 243), which goals
should run fresh first? Can a model of past runs pick them? And what to do with goals that stall?

**Setup.**
* **Features** (schedfeats.py): 16,000 fresh runs of rounds 3–5, replayed in order, with features as they were
  when each run started:
  * proof-line distance to the nearest proven goal below and above;
  * failed runs so far, and failed fresh runs with the same nearest proven goal below (`nfail_ctx`);
  * the growth of the original's proven set since the goal's last fresh run;
  * the original's success rate over its last 30 fresh runs;
  * goal size and variables.
* **Model** (schedmodel.py): logistic regression on one-hot quantile bins, 61 weights. Trained on rounds 3–4
  and the first 60% of round 5, tested on the last 40% (2,253 runs, 21% proved).
* **In the loop** (`--sched-model M.json`): candidates are the goals whose context or pool changed, ordered by
  predicted success. Those below `--sched-pmin` 0.06 wait for idle slots.
* **A/B 1:** ABa (distance order) against ABb (sched/m2.json), from one reflink copy of UL, 9 workers each,
  04:05–05:07.
* **A/B 2** (05:16): ABc distance; ABd m3 (fixed bins, `lg_new`) with `--sched-max-lgap 320
  --sched-retrain 200`; ABe as ABd with `--cascade 10,80`. 7 workers each.
* **Stalled goals:**
  * sets/st80: 80 of the 1,575 goals within 80 lines of a proof whose last fresh run failed with the same
    nearest proven goal below (abs/stalled_set.py);
  * abs/port.sh: 8 variants of the L0 configuration from snapshot loops/ULsM, 2 workers each;
  * st79 probes: the climber (abs/clst.sh) and fresh 80 s.
* **Tail heads** (`loop.py --head-first --head-only-from L`, 9cc44be): UL19, UL20, UL21.

**Results.**

| failed fresh runs, same nearest proven goal below | runs | proved |
|---|---:|---:|
| 0 | 1,232 | 43% |
| 1 | 695 | 15% |
| 2 | 776 | 13% |
| 3 | 846 | 14% |
| 4+ | 1,985 | 11% |

| ordering (test, 2,253 runs) | AUC | top 10% | top 25% | top 50% |
|---|---:|---:|---:|---:|
| model | 0.737 | 54% | 43% | 32% |
| proof-line distance | 0.599 | 30% | 29% | 25% |

A/B 1, new proofs:

| minutes | 8.5 | 29 | 43 | 53 | 62 |
|---|---:|---:|---:|---:|---:|
| ABa (distance) | 11 | 97 | 122 | 166 | 177 |
| ABb (model) | 60 | 128 | 156 | 171 | 180 |

* In ABb's fifth 10-minute bin, 65 of 132 runs went to nslm_to_aa1 at a median of 702 lines from a proof
  (6 proved, 22 predicted). The cause: one quantile bin held every distance beyond 84 lines. Fixed bins
  raised the AUC from 0.751 to 0.807 on ABb's last 515 runs.

A/B 2, new proofs:

| minutes | 12 | 22 | 33 | 35 (stopped) |
|---|---:|---:|---:|---:|
| ABc (distance) | 15 | 19 | 22 | 22 |
| ABd (model) | 34 | 43 | 52 | 52 |
| ABe (model, 10 s first level) | 33 | 63 | 68 | 69 |

* All three ran dry after 25 minutes: A/B 1 and UL14 had taken most of the new contexts.
* Portfolio on st80: every variant except the 500-hint one proved the same single goal (com_Ralt__goal_246).
  Climber 0 of 15 on st79; fresh 80 s 1 of 11.
* UL16: fresh runs proved 27 of 424 (6%, predicted 41); resumes about a quarter.
* Where the unsolved are (06:45): 8,335 goals in 1,006 runs of consecutive unsolved goals; 559 single holes;
  95 open tails with 4,851 goals (58%).
* Tail heads at 320 s (UL20): 5 of 62 (8%, not the 30% assumed), about 0.4 proofs per CPU-hour.

**Reading.**
* **A fresh run in a new context is the signal:** 43% against 11–15%. A rerun in the same context repeats a
  deterministic search, so it can only gain if the pool grew.
* The model wins early in both A/Bs. A/B 1 ends tied: ABa's late surge is its near goals in proof order, each
  proof giving the next goal a new context. Arms from one copy compete for the same new contexts, so the
  later minutes compare less.
* **The stalled-goal probes were invalid,** as I found at 09:40. `--init` imports only round-0 rows, and
  snapshot ULsM kept the loop's round numbers, so the probes ran with the 33,720 round-0 proofs instead of
  43,484. That covers the portfolio, the breakthrough probes, and 2ad's stalled-goal probes. In the full
  context, fresh 20 s proves about 15% of these goals (2026-11-15-retrain-stall-artefact.md). Snapshots
  since then set column 2 to 0 (exp/README).
* Tail heads are the hardest goals, not the cheapest breakthroughs.

**Decision and next.** The scheduler with `--cascade 10,80` in production for a while (UL15–UL17). Later
replaced by `--mix 0.1 --fail-order` (REPORT 2at), with SCHED left as an option in solve_new.sh. UL21 went back
to level order. REPORT 2ac.

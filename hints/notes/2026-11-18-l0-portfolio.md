# A portfolio at the cheap level: 5 s variants on goals that failed their 5 s fresh run (exp21)

Started 18 Nov 2026, 17:17 UTC. Directory /project/hintwork/exp21; scripts in hints/exp/exp21_*. Part of the portfolio
task (notes/2026-11-18-portfolio-review.md).

## Question

Production's fresh level makes 11.3 proofs per CPU hour against 1.16 for the 80 s chain level (UL r5 since 12:02).
A 5 s run costs about 8 CPU s. So a 5 s variant that proves 1% of the goals a fresh run failed would make about 4.5
proofs per CPU hour, four times the deep level.

On 12-13 Nov the rule-model settings at 8 s had a union of 93 against the best single setting's 69 (2b, on 345
held-out goals). That was in a weak early setting, though, and nothing since has measured short variants on the goals
production holds.

Which 5 s variants prove goals whose 5 s fresh run failed, beyond a plain rerun (context drift), and at what yield
per CPU hour?

## Set

* **Goals (exp21/pick.py, at 17:17):** goals unsolved in UL whose last row in UL r5 is a failed fresh run (L0 NO):
  5,869 candidates. 300 sampled with random.Random(21) from 73 originals (goals300).
* **Context:** UL at 17:17.
* **Capture (exp21/capture.sh):**
  * as in exp11 and exp17: exp3/solve_cap.sh with LOOP_PRINT_CMD, then exp6/tbify.py at 5 s;
  * but at 0.01 abstract s, so the capture loop proves nothing and all 300 commands share one context;
  * with production's twee as TWEE=twee-e61 and PG="--pg-threshold 0.25 --ground-joining-branch-limit 100", so the
    flags are in the commands;
  * KNN=30 (B, production) and KNN=60 (K60).

## Arms (exp21/mk.py)

All at 5 abstract s with `--max-cpu 50`, one command file, ids ARM:goal, goal-major:

| arm | change |
|---|---|
| C | control: production's fresh run, recaptured (it proves what context drift since the goal's last run allows) |
| K60 | 60 kNN lemmas |
| U | definitions unfolded (problem and hints) |
| S | `--eqhint-subsume` |
| R2 | rule-model threshold 0.2 instead of 0.1 |
| N | no rule model |
| G | no parental guidance |
| X | chain hints (production's 80 s hints) instead of the pool |

Runner: exp11/run.py on **6 workers** (2,400 runs, about 5 CPU hours). exp12 stage B was paused at 17:24 for
them.

Build details:
* The first mk.py run (stage.sh, 17:21) stopped on its own check: the K60 commands point to their capture's
  copies of the goal and hint files (tbK60/).
* mk.py now builds K60 as C's command with only the problem file swapped. It checks that the rest matches up to
  that path and that the hint files are identical.
* Rerun: 17:22-17:31, 300 goals, 8 arms, 2,400 commands.
  * K60 problems have 60 kNN lemmas, against 30.
  * All 300 goals have definitions to unfold.
  * Mean pool 7,794 hints, mean chain 11,744 (sizes.tsv).
* Arm N (no rule model) checked on one goal: it runs cleanly. PG pairs a rule without a model score with
  everything (src/Twee.hs, pgFilter), so N is also without PG: G minus the rule filter.
* Started by hand at 17:32:35 (`python3 run.py A.cmds A 6`).
* **Arm P9 (added 17:37):** Prover9 with the pool hints and 6 sibling lemmas (p9twee.py batch, as exp16 but with the
  pool), on the capture's context snapshot (exp21/cap/B.ctx), `--timeout 8`: about the CPU of a twee 5 s run
  (about 8 CPU s). 1 worker, so 21 CPUs for about 40 minutes:
  `python3 /project/twee/hints/p9twee.py exp21/goals300 exp21/cap/B.ctx exp21/out_P9 --timeout 8 -j 1`.

```
cd /project/hintwork
python3 exp21/pick.py; bash exp21/capture.sh
cd exp21; python3 mk.py; python3 run.py A.cmds A 2
```

## Measures

For each arm:
* proved;
* proved and not by C, both in all and per CPU hour;
* the greedy union curve over the arms, by new proofs per CPU hour.

Production comparison: L0 makes 11.3 per CPU hour and L1 1.16.

## Results

(pending)

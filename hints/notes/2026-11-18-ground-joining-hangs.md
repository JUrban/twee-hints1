# Runs that never end: unbounded ground joinability (exp6)

Started 18 Nov 2026, 05:16 UTC. Directory /project/hintwork/exp6; scripts in hints/exp/exp6_*.

## What was seen

* A refinement run in exp4 (com_Ralt 348, conjecture 4003, `--max-time 20 --max-cpu 200`) ran for 2 h 54 min of
  CPU before I killed it. Five exp3 deep runs (320 s, `--max-cpu 3200`) had used 4–8.7 CPU hours each when I
  killed them at 05:03 (exp3/hung_killed.txt):
  * V arm: aK2_eq_aK3_d 506, aa_to_nil3 516, com_Ralt 348, nil3_23_32_to_25 499;
  * C arm: aa_to_nil3 516.
* twee checks `--max-time` and `--max-cpu` only between two steps of the main loop (src/Twee.hs, `loop`). A
  single step that never ends is never stopped.
* Production is bounded by loop.py's wall limit (`--wall-factor 15`). Its round r5 (loops/UL/r5/results.tsv)
  has 219 runs that ended without a WORK/HINTSTATS line, 79 of its 698 CPU hours (11%):

  | level | killed by the wall limit | heap exhausted | share of the level's CPU |
  |---|---|---|---|
  | L0 | 4 runs, 0.4 h | 0 | 0.3% |
  | L1 | 55 runs, 12.4 h | 6 runs, 1.1 h | 4% |
  | L2 | 65 runs, 22.0 h | 89 runs, 43.1 h | 32% |

## Diagnosis (hang/ in exp4)

* The exp4 case reproduces at 1 CPU (hang/cmd, `--quiet` dropped: cmd.loud). Rules are added up to rule 2900 in
  about 75 s, then nothing more within 600 s.
* Just before the stall, the run adds permutation laws over many variables. Rule 2899 is
  `r(r(r(r(r(X,Y,Z),W,V),U,T),S,X2),Y2,Z2) = r(r(r(r(r(X,Y2,Z2),Y,Z),U,T),W,V),S,X2)`, with 11 variables (the
  inner maps commute). twee's ground joinability test (src/Twee/Join.hs) splits on orderings of the variables.
  `--ground-joining-limit` (assume not ground joinable after N orderings) is unlimited by default.
* With `--ground-joining-limit 100` the same run passes rule 2900, reaches rule 3544 and ends normally by
  CPULIMIT at 200 s, with 36,005 pairs considered. That is still slow: about 180 pairs/s. With 10,000 it stalls
  at rule 2900 as before (600 s wall). 1,000: see the results.
* Where the time goes (src/Twee/Join.hs, `groundJoinFrom`): every model in which the pair fails adds
  `diag (modelToLiterals model')` to the case split by `formAnd`. That multiplies the number of branches by up to
  the number of literals, and every later tick solves all branches. The tick limit bounds the number of models,
  not the size of the split.
* **twee-e57** (commit 2eb8fbd): `--ground-joining-branch-limit B` assumes "not ground joinable" (as at the tick
  limit) once the split has more than B branches. On the repro, 20 abstract s, CPU cap 200 s:

  | setting | pairs considered | CPU s | end |
  |---|---|---|---|
  | unlimited (e48) | stalls after rule 2900 | > 600 | killed |
  | tick limit 10,000 | stalls after rule 2900 | > 600 | killed |
  | tick limit 1,000 | 28,661 (one step of about 245 s at rule 2901) | 320 | CPU cap |
  | tick limit 100 | 36,005 | 205 | CPU cap |
  | branch limit 1,000 (e57) | 35,932 | 216 | CPU cap |
  | **branch limit 100 (e57)** | **40,000** | **43** | **normal** |
  | branch limit 30 (e57) | 40,000 | 35 | normal |
  | branch limit 10 (e57) | 40,000 | 30 | normal |

  At 10, 30 and 100 the search is the same (3,870 rules, 40,000 pairs). Only the time differs.
* Watchdog abs/cpuwatch.py (from 05:17, PID 2391999) kills experiment runs (not production) past 1.5 x
  --max-cpu + 60 s CPU, logging to abs/cpuwatch.log. Its first kill was another com_Ralt 348 refinement run (4004,
  997 s CPU against a cap of 200).
* Not yet known: whether the HEAP runs (most of the L2 loss) have the same cause, and whether gdb or perf could
  show it. ptrace and perf are not allowed in this sandbox for processes outside the session's own tree.

## Test

* **A, the real hangs:** the five exp3 commands, rebuilt exactly as exp3/run.py builds them (hang5.cmds), with
  `--ground-joining-limit 100`, 320 s, CPU cap 3200 s. Question: do they end, and do any prove?
* **B, side effects:** the 200 hard goals of the PG testbed (pg/tb/cmds.all, 203 commands; repeated names get
  `#2`, `#3`), as in production: twee-e48, PG 0.25, 20 abstract s, CPU cap 200 s (pg200.cmds). Arms b0
  (unchanged) and g100 (`--ground-joining-limit 100`). We compare proved goals, CPU, ended-by-cap and killed
  runs, and the goals whose considered-pair counts differ.
* The runner is exp6/run.py CMDS ARM J [EXTRA...]. Its wall limit is 1.5 × max-cpu + 60 s. Results go to
  res_<ARM>.tsv (id, proved, CPU, peak MB, considered, end, wall).

```
cd /project/hintwork/exp6
python3 run.py hang5.cmds a_g100 2 --ground-joining-limit 100
python3 run.py pg200.cmds b0 1
python3 run.py pg200.cmds g100 1 --ground-joining-limit 100
```

* **05:21, changed to the branch limit.** Its repro result is far better, so the tick-limit arms were stopped:
  a_g100 had finished no run; g100 had finished 17 of 203 (kept as partial_res_g100.tsv). They were replaced by
  e57 arms with `--ground-joining-branch-limit 100`. b0 continues.

```
python3 run.py hang5_e57.cmds a_gb100 2 --ground-joining-branch-limit 100
python3 run.py pg200_e57.cmds gb100 1 --ground-joining-branch-limit 100
```

* **C, production's stalled goals (launched 05:27).**
  * Set: goals with an L1 or L2 run in production round r5 that ended without a WORK/HINTSTATS line (killed or
    out of heap). That is 169 goals (cap/stalled_r5.tsv), 92 of them still unsolved in UL at 05:22 (cap/goals).
  * Commands captured in production's context as exp3 did:
    `LOOP_PRINT_CMD=1 LOOP_KEEP_TMP=1 SCHED= XEVERY=100000 CASCADE=5 timeout 900 bash exp3/solve_cap.sh
    cap/goals loops/UL cap/CAP 3 0.05`. The context was 44,912 UL proofs. Commands came for 79 goals within the
    3 minutes; the 5 s capture runs proved none.
  * tbify.py turned them into 78 commands (stall78_*.cmds; files in cap/tb) at production's L1: 80 abstract s,
    CPU cap 800 s. The runner's wall limit is 1,260 s; production's at L1 is 1,230 s.
  * Arms: s_b0 (e48 as captured) and s_gb100 (e57 with `--ground-joining-branch-limit 100`).

```
python3 run.py stall78_e57.cmds s_gb100 2 --ground-joining-branch-limit 100
python3 run.py stall78_e48.cmds s_b0 1
python3 run.py pg200_e57.cmds gb10 1 --ground-joining-branch-limit 10    # B: also the limit 10
```

## Results

(pending)

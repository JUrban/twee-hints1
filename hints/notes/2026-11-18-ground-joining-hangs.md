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

## Results

(pending)

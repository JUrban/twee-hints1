# Breaking the walls with chain hints (exp11)

Started 18 Nov 2026, 10:30 UTC. Directory /project/hintwork/exp11; scripts and sets in hints/exp/exp11_*.

## Why

At 10:29, UL had 45,414 of the benchmark's 51,784 goals; 6,370 were unsolved.
* Of the 129 originals, 22 are fully solved. Each of the other 107 has a first unsolved goal, its "wall".
* **Behind the 107 walls are 6,263 of the 6,370 unsolved goals.** Often the tail behind a wall is nearly all
  unsolved: nil3_23_32_to_27 has 1 of 114 solved above its wall, aK2_eq_aK3_b 6 of 158. The biggest:
  * nslm_to_aa1 781, 528 unsolved behind it;
  * nsmr_to_aa1 606, 214;
  * aK2_eq_aK3_a 455, 190.
* In round 5, 86 walls reached the 320 s level and 20 the 80 s level, always with the original's pool as hints.
  Only 10 have been tried with chain hints (3 in exp3, 7 in exp8).
* Chain hints beat the pool at 80 s (exp8: 9 against 5) and at 320 s (exp3: 12 against 9), but not at 20 s
  (exp9).
* A proof at a stalled place gives the goals around it new contexts and cheap 5 s proofs (REPORT 2ax: 152
  proofs in 70 min after the 07:09 merge).

So a wall proof is the most valuable deep proof there is.

## Set and setting

* All 107 walls (no sampling), from loops/UL/solved.tsv and sets/all at 10:29: walls.tsv (goal, unsolved
  behind, goals behind), goals107.
* Commands captured in production's context (`LOOP_PRINT_CMD=1 LOOP_KEEP_TMP=1 SCHED= XEVERY=100000 CASCADE=5
  timeout 1500 bash exp3/solve_cap.sh goals107 loops/UL cap/CAP 3 0.1`), as in exp9. The hints are then replaced
  by the chain: sibchain.py, records chain_records.tsv, UL's 10 nearest proven siblings below the wall.
* Stage 1: 80 abstract s (CPU cap 800 s), 4 workers. Stage 2: the walls stage 1 did not prove, at 320 s
  (CPU cap 3,200 s), same commands.
* There is no pool control: production's own pool runs (r5, results.tsv) failed on every wall at 80 s, and at
  320 s on 86.
* Proofs are merged into UL as they come (exp3/tomerge.py, merge.py). For each merged wall, I count the proofs
  production then finds behind it.

## Launch (10:38)

* Capture: commands for all 107 walls; none proved at 5 s.
* `exp6/tbify.py cap/CAP.log cap/CAP cap/tb s1_pool.cmds 80` (and s2_pool.cmds at 320), then
  `mkchain.py s1_pool.cmds s1.cmds` and `mkchain.py s2_pool.cmds s2_all.cmds`. On average 7,276 chain hints
  against 6,110 pool hints; no chain is empty (sizes.tsv).
* `bash stage.sh` (exp/exp11_stage.sh): `run.py s1.cmds s1 4`, then the unproved walls in `run.py s2.cmds s2 4`.
  Every 10 minutes, and after each stage, `exp3/tomerge.py out_s1 out_s2 xm` + `merge.py loops/UL xm`; times in
  merges.log.

## Results

(pending)

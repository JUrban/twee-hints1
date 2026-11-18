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

## Correction and change of plan (11:21)

* **The "6,263 unsolved behind the walls" overstated what a wall blocks.** It counts every unsolved goal above
  an original's first unsolved goal. Those goals form many separate gaps, each with its own first goal.
* Gap structure at 11:21 (gaps.tsv; a gap is a maximal run of consecutive unsolved goals of an original):
  * 812 gaps: 338 of length 1, 228 of 2-4, 150 of 5-19, 92 of 20-99, 4 of 100+.
  * The 96 gaps of length >= 20 hold 4,045 of the unsolved goals; 83 gaps reach the original's top goal.
* **Only 2 of the 107 walls head a gap of 20 or more** (12 head one of 5 or more). Most walls are isolated holes:
  in four of the first five walls stage 1 proved (Ka1_eq_Ka2 400, aK2_eq_aK3_1243 339 and 1243b 372, aa1_14
  482), the five goals above were already proven. So their proofs unlock nothing new.
* So stage 1 (80 s, cheap) runs to its end, but **stage 2 (320 s on the walls, about 30 CPU h) is cancelled**.
  At 11:21 I stopped stage.sh and its merge loop; its run.py for stage 1 continues on its own. Its proofs are
  merged by hand at the end.
* The deep budget goes to the heads of the 96 long gaps instead (exp12, notes/2026-11-18-gap-heads.md).

## Results

* Stage 1 interim (11:20, 57 of 107): 5 proved, namely Ka1_eq_Ka2 400 (145,609 pairs), aK2_eq_aK3_1243 339,
  aK2_eq_aK3_1243b 372, aKperms_1 344 and aa1_14 482. Four were merged (10:48: 400, 339, 372; 11:08: 482).
  * **aKperms_1 344 came first through the live transfer, at 10:53** (loops/XFL/transfer.tsv: THM in 1.52 s,
    source Ka1_eq_Ka2 400). That is five minutes after 400 was merged. So one wall proof broke a wall of another
    original (50 unsolved behind it) by transfer. exp11's own proof of 344 followed at 11:05.
* **Stage 1 final (complete by 11:52): 15 of 107 walls proved at 80 s in 4.8 CPU h (3.1 proofs per CPU h).**
  * The 15: Ka1_eq_Ka2 400, aK2_eq_aK3_1243 339, aK2_eq_aK3_1243b 372, aKperms_1 344, aa1_14 482,
    mbol_aa1sqrd_to_aa1 528, mbol_nil3_a 476, nil3_18 318, nil3_1K_e 412, nil3_23_32_to_28 392, ns_to_aa1_b 588,
    nslm_to_aa1 781, nsmr_to_aK1 458, osb_Kcom_to_aK1 406, uflex_to_aaip 80. Their proofs took 23,570 to 153,278
    pairs.
  * All were isolated holes: the ten proved after 11:21 head gaps of length 1 in gaps.tsv, and the goals above
    the first five were already proven. So they add 15 proofs but open no runs, apart from the transfer from 400.
  * The last 10 were merged at 11:52 by exp12's runner (exp12/merges.log); with the four from the merge loop and
    344 from the transfer, all 15 are in UL.
  * By comparison, production's pool runs had failed on all 107 at 80 s and on 86 at 320 s.

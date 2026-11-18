# Two-sided chains: siblings above as well as below (exp14)

Started 18 Nov 2026, 13:24 UTC. Directory /project/hintwork/exp14; scripts and data in hints/exp/exp14_*.

## Why

The chain (sibchain.py) takes the proofs of a goal's 10 nearest proven siblings *below* it, expanded through
the lemma records of those proofs. But many unsolved goals have proven siblings *above* them as well.

At 13:20, of the 6,274 unsolved goals:
* 720 have a proven sibling directly above;
* 678 have the nearest proven sibling above at 2 or 3 goals;
* 1,027 at 4 to 10;
* 1,764 farther;
* 2,085 have none (their gap reaches the original's top).

A sibling above is a later step of the same Prover9 proof. Its twee proof did not pass through the goal (else
the transfer would have proved the goal), but it may use the lemmas the goal needs.

## Set and setting

* exp11's 107 walls: each original's first unsolved goal at 10:29, so every sibling below was proven. I use
  exp11's stage-1 commands (s1.cmds, captured 10:38: 80 abstract s, CPU cap 800 s, twee-e48, same lemmas),
  with only the hints file changed.
* **Control:** exp11's stage 1, the below-only chain: 15 of 107 proved (res_s1.tsv).
* **Arm T:** the two-sided chain, `sibchain.Chains.chain(..., two_sided=True)`. It takes the 10 nearest proven
  siblings by goal-number distance, above or below, with ties going below first. "Proven" means UL's
  solved.tsv at 10:29 (its first 45,414 rows), the state the walls were computed from.
  * Siblings above among the 10: none for 7 walls, 1 to 6 for the other 100, a mean of 3.4.
  * The 7 walls with none above get exactly exp11's chain (same files), so they also check that the runs
    reproduce.
  * Mean hints: 7,821 against exp11's 7,276 (sizes.tsv: goal, exp11 chain, T chain, siblings above).
* 4 workers (exp11/run.py).

```
cd /project/hintwork/exp14
python3 mk.py
python3 run.py T.cmds T 4
```

## Results

Complete at 14:50, all 107 walls (exp14/res_T.tsv):

* **Two-sided 16, below-only (exp11) 15: +4 −3, within noise.**
  * Gained: aK2_eq_aK3_t 367, aa1_12 510, mbol_12lemmas 503 and nil3_1K_a 340 (45,147 to 105,384 pairs). Each has
    4 or 5 siblings above among its 10.
  * Lost: aKperms_1 344, aa1_14 482 and mbol_nil3_a 476.
* Where both prove (12 walls): 1,003,587 pairs against 1,176,700 (−15%). The time column is 17% higher, but it is
  wall time on a busier machine, and the pair counts are the fair measure.
* **Reproducibility:** the 7 walls with no sibling above have exactly exp11's chain, and gave exactly exp11's
  results: the same proved/unproved and the same pairs (160,000 or 160,001; uflex_to_aaip 80 proved at 147,759
  pairs in both). Only wall time and memory differ. So exp11 is an exact control whenever only the hints change.
* The 4 gains were new to UL and were merged at 14:50 (`exp3/tomerge.py exp14/out_T exp14/xm`, `merge.py loops/UL
  exp14/xm`). All 4 are isolated holes (the goal above is proven), so they open nothing.
* **Decision:** no production change. The two-sided chain is not better in count, so the evidence does not justify
  a restart. Its gains are different goals, though: as a second chain variant for goals that failed the first,
  it gave 4 new proofs out of 92 failed walls in about 5 CPU h.

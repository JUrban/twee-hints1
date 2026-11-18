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

(pending)

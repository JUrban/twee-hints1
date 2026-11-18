# Prover9 with chain hints on the walls (exp16)

Prepared 18 Nov 2026, 13:34 UTC; it starts when exp14's runner (PID 2432727) ends. Directory
/project/hintwork/exp16; scripts in hints/exp/exp16_*.

## Why

* The 15 Nov side worker (p9twee.py, REPORT 2ad and 2af) gave Prover9 the original's whole twee pool as hints. It proved
  goals that every twee variant failed, such as aK2_eq_aK3_r 241, at about 0.8 proofs per CPU hour. It was
  replaced by the unfolded-twee worker at 10:24 on 15 Nov, after 9 proofs in 283 tries.
* Prover9 is the system that found these proofs in the first place, with Veroff's hint loops, and it relies on
  hints more than twee does.
* For twee, chain hints beat the pool at 80 s and 320 s (exp8, exp3), so Prover9 may gain from them too.
* Its proofs complement twee's: they are new information for the goals around them.

## Set and setting

* exp11's 107 walls (walls107, from exp11/walls.tsv), in UL's proven state at 10:29 (`--solved-rows 45414`, the
  first 45,414 rows of solved.tsv; the walls were computed from it). Every wall therefore counts as unsolved,
  including the 15 exp11 proved.
* p9twee.py batch mode, /project/bin/prover9-new (as on 15 Nov), 60 s per goal (Prover9's max_seconds, wall
  clock).
* Assumptions: the TPTP axioms and the 6 nearest proven siblings on each side. This is p9twee's default, not
  twee's lemma set.
* **Arm P (pool):** the 15 Nov setting, with the original's whole twee pool (all proven siblings' hint files,
  deduplicated) as `formulas(hints)`.
* **Arm Q (chain):** `--chain chain_records.tsv`, the goal's chain (sibchain.py, its 10 nearest proven siblings
  below, expanded through their lemma records). That is exp11's chain.
* 2 workers each, run side by side.
* Comparisons: P against Q, and each against twee's exp11 (15 of 107), exp14 and exp15 on the same walls.

```
cd /project/hintwork/exp16
cut -f1 ../exp11/walls.tsv > walls107
bash stage.sh 2432727
#   python3 p9twee.py walls107 loops/UL out_P --timeout 60 -j 2 --solved-rows 45414
#   python3 p9twee.py walls107 loops/UL out_Q --timeout 60 -j 2 --solved-rows 45414 --chain chain_records.tsv
```

## Results

Complete 14:50-15:43 (exp16/out_P, out_Q: results.tsv).

| arm | mean hints | proved | wall (= CPU) h | proofs per CPU h |
|---|---:|---:|---:|---:|
| P: Prover9 + the original's pool | 6,106 | 2 | 1.77 | 1.1 |
| Q: Prover9 + the chain | 7,276 | **4** | 1.76 | 2.3 |

* P proved uflex_to_aaip 80 (36.6 s) and mbol_KK_to_aK1 170 (9.5 s).
* Q proved uflex_to_aaip 80 (35.5 s), aK2_eq_aK3_j 382 (20.7 s), mbol_lem1 387 (31.8 s) and aa1_12 510 (43.7 s).
* Every other run stopped at the 60 s limit (exit code 4).
* Against twee (exp11, the same walls at 80 s with the chain, 15 proved):
  * Prover9 adds 4 walls twee did not prove: 382, 387 and 510 with the chain, 170 with the pool.
  * Only 80 is proved by both.
  * exp14's two-sided twee chain also proved 510.
* So the chain helps Prover9 as it helps twee (+3 −1 against the pool, small numbers), and Prover9 is a different
  search: its proofs are mostly goals twee fails.
* Merged into UL: 382 at 15:17; 170 and 387 at 15:44 (`merge.py loops/UL exp16/out_P`, then `exp16/out_Q`). 510
  had come from exp14 at 14:50.
* **Decision:** a Prover9 side worker with chain hints, abs/p9c.sh (`p9twee.py --live ... -j 2 --chain
  chain_records2.tsv`, loops/P9C). It starts when exp18's runner ends, to stay within 20 CPUs. At 15:45 it
  has 416 stalled goals within 80 proof lines to try.

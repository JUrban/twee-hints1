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

(pending)

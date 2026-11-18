# Subsumption matching at a deep budget on the walls (exp18)

Started 18 Nov 2026, 14:47 UTC. Directory /project/hintwork/exp18; scripts and data in hints/exp/exp18_*.

## Why

* The user (14:40): Prover9's hint matchers subsume the hints, rather than having to be variants of them. That
  "may be visible on harder research tasks, not immediately on simpler problems".
* exp7 (notes/2026-11-18-subsumption-matching.md) tested twee's `--eqhint-subsume` only at 20 abstract s, on the
  200 PG testbed goals. It was neutral: 87 against 87 (+2 −2), with +17% CPU.
  * Those were goals that a 20 s run proves.
  * The question here is the hard case: unsolved holes at 80 s, guided by the chain. There the run must follow
    long hint sequences, and a general rule that covers several hints may matter more.

## Set and setting

* exp11's 107 walls, with exp11's stage-1 commands (s1.cmds: 80 abstract s, CPU cap 800 s, captured 10:38, chain
  hints h_chain/), with only the binary changed to twee-e61 and `--eqhint-subsume` added.
* **Control:** exp11's stage 1 (twee-e48, 15 of 107).
  * e61 without the flag reproduces e48 exactly on these commands: 3 of exp11's proved walls (372, 392 and 406)
    give identical pairs to proof, 23,570, 24,140 and 55,300 (res_chk.tsv).
  * So the flag is the only difference.
* **Arm SU:** e61 with `--eqhint-subsume`. The 92 walls exp11 did not prove come first, then its 15.
* 4 workers, freed by cutting production from 8 workers to 4 (ul46). Production's 80 s chain runs had proved
  nothing in the 80 minutes before.

```
cd /project/hintwork/exp18
python3 run.py check.cmds chk 3     # identity check, e61 without the flag
python3 run.py SU.cmds SU 4
```

## Results

Complete at 16:48, all 107 walls (exp18/res_SU.tsv; 106 normal ends, 1 at the CPU cap):

* **Proved: SU 13, control 15 (+3 −5).**
  * Gained: aK2_eq_aK3_t 367 (exp14 had it too), a_instances 363 and mbol_to_nil3 572.
  * Lost: Ka1_eq_Ka2 400, nil3_18 318, ns_to_aa1_b 588, nslm_to_aa1 781 and uflex_to_aaip 80.
* **Where both prove (10 walls): 698,057 pairs against 888,252, −21%.**
  * The large drops: aa1_14 482 140,414 → 37,345; aKperms_1 344 86,746 → 55,931; nsmr_to_aK1 458 151,909 →
    118,391; osb_Kcom_to_aK1 406 55,300 → 44,004.
  * The rest are within ±10%.
  * At 20 s (exp7) the same comparison gave −0.6% (872,649 against 878,065). So **in abstract time the effect does
    show on the harder goals, as the user expected, but it does not turn into more proofs here.**
* **CPU: 28,331 s against 17,346 s, +63%** for the same pair budget. exp7 measured +17% at 20 s. Matching every
  general pair against about 7,000 chain hints, with their normal forms, costs more as the run grows.
* The two new proofs (363, 572) were merged at 16:49 (`exp3/tomerge.py exp18/out_SU exp18/xm`, `merge.py loops/UL
  exp18/xm`).
* **Decision:** not in production. Fewer proofs at a 63% higher cost per pair. Two things could make it pay: a
  cheaper subsumption lookup, so the pair savings are not eaten by matching cost; and a run budget equal in CPU
  rather than in pairs. As with the other variants, its gains are different goals (2 new of 92 failed walls).

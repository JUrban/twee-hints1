# Subsumption matching at a deep budget on the walls (exp18)

Prepared 18 Nov 2026, 14:45 UTC. Directory /project/hintwork/exp18; scripts and data in hints/exp/exp18_*.

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

(pending)

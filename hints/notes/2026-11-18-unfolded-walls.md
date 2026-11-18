# Unfolded definitions with chain hints on the walls (exp15)

Prepared 18 Nov 2026, 13:32 UTC; it starts when exp13's two runners end. Directory /project/hintwork/exp15; scripts
and data in hints/exp/exp15_*.

## Why

* Deep runs alone do not reach the hard goals: exp5 proved 0 of 15 at 640 s that had failed at 320 s. Earlier
  work found that stalled goals need new information, such as a proof nearby; other settings did nothing (REPORT
  2ac, 2ag).
* The one change that proved stalled goals there was a different representation, all definitions unfolded
  (REPORT 2af). On the goals nearest a proof it proved 7 of 9 against 2 folded, and 3 of 10 where Prover9 failed.
  It ran as a side worker at 20 s (uflive.py) until 15 Nov 15:17, when it fell to 0 or 1 proof per 24-goal cycle.
* It has never been tried with chain hints, or at 80 s.

## Set and setting

* exp11's 107 walls, with exp11's stage-1 commands (s1.cmds: 80 abstract s, CPU cap 800 s, twee-e48, captured
  10:38, the below-only chain). The control is exp11's stage 1: 15 of 107 proved (res_s1.tsv). exp14 runs the
  two-sided chain on the same commands.
* **Arm U:** the same commands with every definition unfolded (exp15/mk.py, as `loop.py --unfold`). The problem
  goes through `unfold.unfold_text`, and the chain hints through `unfold.unfold_eq` with the problem's
  definitions. The rule model and its goal file are unchanged.
* Order: the 92 walls exp11 did not prove come first, then its 15. A proof among the 92 is new to UL.
* Unfolded terms are bigger, so a run reaches fewer abstract seconds within the 800 s CPU cap. That cost is part
  of what is measured: proofs per CPU hour against exp11's 3.1.
* 4 workers (exp11/run.py).

```
cd /project/hintwork/exp15
python3 mk.py
bash stage.sh 2427900 2427969     # exp13's runners; then: python3 run.py U.cmds U 4
```

## Results

(pending)

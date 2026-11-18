# Successor sets for critical pairs (--set-join) at 80 s on the walls (exp19)

Started 18 Nov 2026, 16:49 UTC. Directory /project/hintwork/exp19; scripts in hints/exp/exp19_*.

## Why

* Waldmeister (Hillenbrand 2003, 4.3; notes/2026-11-18-waldmeister-paper.md) represents each conjecture by its
  set of successors, all terms reachable by rewriting. The conjecture is proved when the two sets meet. This
  pays because the rewrite system is not confluent during completion. Its TPTP count rose from 278 to 300.
* twee already does this for goals (`cfg_set_join_goals`, on by default).
* `--set-join` does it for critical pairs as well: a pair whose sides' normal-form sets meet is joined, so it
  does not become a rule. It is off by default and has not been tested here.

## Set and setting

* exp11's 107 walls with exp11's stage-1 commands (80 abstract s, CPU cap 800 s, chain hints), with only the
  binary changed to twee-e61 and `--set-join` added. e61 without the flag reproduces e48 exactly (exp18's
  check).
* **Control:** exp11 (15 of 107).
* **Arm SJ:** the 92 walls exp11 did not prove first, then its 15.
* 2 workers.

```
cd /project/hintwork/exp19
python3 mk.py
python3 run.py SJ.cmds SJ 2
```

## Results

(pending)

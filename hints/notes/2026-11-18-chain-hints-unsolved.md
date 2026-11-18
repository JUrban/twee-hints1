# Chain hints on production's unsolved goals (exp8)

Started 18 Nov 2026, 07:19 UTC. Directory /project/hintwork/exp8; scripts and sets in hints/exp/exp8_*.

## Question

In exp3 (47 late unsolved goals, 320 s), arm K did best. K keeps production's lemmas, but its hints are the
expanded proofs ("chain") of the 10 nearest proven siblings below the goal, instead of the original's pool. At
07:10, K had proved 11 of 39 goals in 11.9 CPU h, and C (production's own setting) 8 of 41 in 18.4 h. Every goal
C proved, K proved too (notes/2026-11-17-deep-runs-expanded-chains.md).

Does the chain beat the pool on a second, larger set, at production's L1 budget? If so, production's deeper
levels should use chain hints.

## Set and setting

* exp6's 78 captured goals (exp6/stall78_e48.cmds; sets/exp8_goals78). These are unsolved goals whose production
  runs at L1/L2 in round r5 ended without stats, with commands captured in production's context at 05:22.
* 80 abstract s, CPU cap 800 s, twee-e48, everything else as captured.
* **Control:** exp6's arm s_b0 (the same commands, the original's pool as hints; still running, 1 worker).
* **Arm s_K:** the same commands with `--hints-file` replaced by the chain.
  * Siblings: the 10 nearest UL-proven siblings below each goal (pick.py, as exp3_pick.py; UL at 07:11). All 78
    goals have 10, 566 distinct siblings.
  * Expansions: `expand.py sibs10 xd` over the 16 loops' records (39,476 proofs; 472 s). Median closure 715
    goals, median 2,875 hints.
  * Per goal, the chain is the siblings' expansions, nearest first, duplicates dropped, as exp3/mkhints.py. On
    average 12,741 chain hints against 11,902 pool hints.

```
cd /project/hintwork/exp8
python3 pick.py goals78; python3 /project/twee/hints/expand.py sibs10 xd
python3 run.py stall78_K.cmds s_K 2
```

## Caveats

* UL has proofs that were found with these goals' siblings in context, but none of the 78 is proved in UL, so
  no chain contains a proof of its own goal.
* exp6's s_b0 runs at 1 worker and s_K at 2, so they share the machine differently. The comparison is by
  proved goals and pairs to proof, which do not depend on load.

## Results

(pending)

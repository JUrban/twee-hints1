# Chain hints at production's short levels (exp9)

Started 18 Nov 2026, 07:48 UTC. Directory /project/hintwork/exp9; scripts and sets in hints/exp/exp9_*.

## Question

exp3 (320 s, 47 late goals) favoured chain hints over the original's pool; exp8 tests 80 s on 78 stalled goals.
Most of production's work and proofs are at 5 s (L0), on the frontier: unsolved goals with proven siblings
below them. Does the chain also beat the pool there? If so it would go into every level, not only the deepest.

## Set

* Public goals (sets/all) unsolved in UL at 07:48 with at least 3 UL-proven siblings below them, minus exp8's 78:
  6,562 goals. Seed 11 shuffle, the first 200, sorted (goals200; 68 originals).
* Commands captured in production's context as in exp3 and exp6:
  `LOOP_PRINT_CMD=1 LOOP_KEEP_TMP=1 SCHED= XEVERY=100000 CASCADE=5 timeout 1200 bash exp3/solve_cap.sh goals200
  loops/UL cap/CAP 3 0.1`. The twee is e48 with PG 0.25, the hints are the original's pool, and the lemmas are
  production's siblings and kNN.

* Capture result (07:54): commands for 199 of the 200 goals (the missing one never ran in the 6 minutes). The
  report's "1 of 200 solved" is aK2_eq_aK3_l 519. Its row in cap/CAP/solved.tsv is round 0: production proved
  it between the sampling (07:48) and the context copy, so it came in with the context. Its own proof may be in
  its hints, so **519 is left out of the comparison** (198 goals).

## Arms (launched 07:55)

* Commands: exp6/tbify.py at 5 and 20 abstract s (CPU cap 10 T), so pool5.cmds and pool20.cmds.
* chain5 / chain20: the same commands with `--hints-file` set to the goal's chain. The chain uses
  sibchain.Chains on loops/UL with the records file /project/hintwork/chain_records.tsv (sibchain.py --build at
  07:39: 39,554 records of the 16 loops) and UL's proven siblings at 07:55, 10 nearest below.
* On average 11,554 chain hints against 7,907 pool hints; no chain is empty.
* exp6/run.py (proved outputs are kept in out_<arm>/), 1 worker per arm: pool5 then pool20, chain5 then chain20.

```
cd /project/hintwork/exp9
python3 run.py pool5.cmds pool5 1; python3 run.py pool20.cmds pool20 1
python3 run.py chain5.cmds chain5 1; python3 run.py chain20.cmds chain20 1
```

## Results

(pending)

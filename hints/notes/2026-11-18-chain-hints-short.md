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

## Arms (planned)

* pool5 / chain5: 5 abstract s, as captured / with the chain (sibchain.py, records chain_records.tsv of all
  16 loops, 10 nearest proven siblings below).
* pool20 / chain20: the same at 20 abstract s.

## Results

(pending)

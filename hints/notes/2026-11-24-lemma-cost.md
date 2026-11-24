# What twee's runs with many lemma axioms cost (exp80)

Started 24 Nov 2026, 04:00 UTC. Scratch runs in the session scratchpad (prof80/).

## Why

* Tonight's paired climbs (exp67, REPORT 2ab) found that the lemma lists decide the heads, not the climb: one fresh
  run with 30 siblings and 400 kNN lemmas proved 9 of 91 heads, with 6 + 30 lemmas 5. Production's best setting at
  the frontier is now runs with several hundred lemma axioms.
* Those runs get slow as they lengthen. exp74's plain runs on 7 cluster heads (100 + 30 siblings, 400 kNN, 1,200
  abstract s) took 2,909 to 4,393 wall s each, about 3 CPU s per abstract second. The cost profiles so far (REPORT
  2t, 2au; notes/2026-11-19-hint-cost.md) were of hinted runs with few lemma axioms, at 10-20 abstract s.
* "What pays is ... cost (faster runs mean more runs)" (JOURNAL section 5). If the long-run cost with hundreds of
  lemma axioms has a removable part, every long run at the frontier gets cheaper.

## Problem

cond/STR77_A1/p/aa1_45_c__goal_355.p: a local head of exp77's set (seed 77), plain (no hints), 524 input formulas:
the original's axioms, 105 sibling lemma axioms (lemma_goal_J) and 400 kNN lemma axioms, as condprove.py writes it.
twee-e61 with production's PG flags, `--abstract-time 2000 --no-resume-requeue --no-eqhint-consider --quiet
--no-proof --pg-threshold 0.25 --ground-joining-branch-limit 100`, `+RTS -s`. The profile: the dist-prof2 build
of e61's source (`-fprof-auto-top`, notes/2026-11-19-hint-cost.md), `+RTS -p`.

## CPU per abstract second

| abstract s | user CPU s | ratio | max RSS |
|---:|---:|---:|---:|
| 5 | 4.62 | 0.92 | 88 MB |
| 20 | 23.32 | 1.17 | 185 MB |
| 120 | 234.44 | 1.95 | 812 MB |

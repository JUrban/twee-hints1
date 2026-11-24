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
| 300 | 730.99 | 2.44 | 1,994 MB |

The cost per abstract second grows with the run: 0.9 at 5 s, 2.4 at 300 s, and the memory with it (2 GB at 300 s).
A 1,200 s run is then about 3 CPU s per abstract second, as exp74's were.

## Where the time goes (profile at 120 abstract s, 1,813 profiled CPU s)

Inherited shares (summed over outermost occurrences in the call tree; script
scratchpad/profinh.py):

| cost centre | inherited | entries |
|---|---:|---:|
| makePassives (a new rule's critical pairs with all active rules) | 80.2% | 29,738 |
| indexedOverlaps (finding the overlaps and building them) | 71.5% | 29,738 |
| simplify (normal forms, oriented rules) | 56.2% | 96,037,433 |
| simpleRewrite (index lookups for a rewrite step) | 33.6% | 706,445,693 |
| termSubst + buildReplacePositionSub (building the pairs' terms) | 26.6% | |
| simplifyQueue (renormalising the queue) | 13.0% | 2 |
| makePassive (scoring a pair) | 8.6% | 10,316,704 |
| interreduce | 4.5% | 119 |
| joinCriticalPair (the considered pairs) | 2.7% | 169,606 |

* The run made 10.3 million critical pairs from 29,738 new rules (about 350 each) and considered 135,773 of them
  (1.3%). Each made pair is unified, built and simplified on both sides against all rules (simplifyOverlap) before
  it is scored, and that is most of the run. Considering pairs (joining, ground joining) is under 3%.
* So the cost is the size of the rule set the new rules overlap with, and hundreds of lemma axioms make that set
  larger from the start. It is the search itself, not overhead around it.

## A speed-up that did not work (e64, deleted)

simplifyOutermost repeats a rewriting pass over the whole term until nothing changes, and each pass rebuilds the
term: 154 million passes for 96 million calls, so every call ends with a pass that only confirms the normal form.
e64 checked first whether any non-variable subterm is reducible and returned the term unbuilt if not; the pass is
skipped only when it would change nothing, so the normal forms are the same.

| binary | 20 abstract s | 120 abstract s (same socket, cores 12 and 13) | trace |
|---|---:|---:|---|
| e61 | 27.54 CPU s | 226.49 | |
| e64 | 26.63 | 252.43 (+11%) | byte-identical (17,352 and 60,131 lines) |

The rebuild is cheap; the index lookups are the cost, and the check repeats them for every pass that does rewrite.
Reverted, binary deleted (04:48).

## Reading

* There is no free factor here. What remains changes the search: fewer pairs (a smaller active set, as lazy lemmas
  did: notes/2026-11-23-plain-sizes.md, a tie at factor 0.5), or pairs simplified later (cheaper per pair, but the
  clock counts the junk that simplification would have dropped). Neither is promising enough for an A/B now.
* Twee's long runs with hundreds of lemma axioms will stay at 2-3 CPU s per abstract second. Compare such settings by
  CPU, not abstract time (exp67's controls were capped by CPU, so its comparison stands).

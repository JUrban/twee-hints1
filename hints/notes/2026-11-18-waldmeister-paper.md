# Reading: Hillenbrand, "Citius altius fortius: Lessons learned from the theorem prover Waldmeister" (ENTCS 86, 2003)

Read 18 Nov 2026, 16:25-16:30 UTC (the user put the PDF at /project/1-s2.0-S1571066104806492-main.pdf, 16:24:
"there might be some tricks there to try"). Twee's design follows Waldmeister closely, so for each technique I
checked the twee source (branch hints, src/).

## The techniques, and whether twee has them

| paper | technique | twee |
|---|---|---|
| 2 | perfect discrimination trees, nodes as arrays indexed by symbol, single-leaf paths collapsed | **has it**: Twee/Index.hs, `fun :: Array (Index f a)` indexed by function number, `prefix` compression, `minSize_` pruning; plus our FPIndex for overlaps (2v) |
| 3.1 | DISCOUNT loop: passive facts normalised only when generated and when selected | **has it**, plus periodic queue renormalisation |
| 3.2 | passive set compressed: one constant-size entry per activation (its number and the least weight of its unselected pairs), a buffer of promising pairs, regenerate on demand; space linear instead of quadratic in abstract time | **partly**: Data/BatchedQueue.hs stores each activation's pairs as one batch in a PackedSequence. It is compact, but still one entry per pair: 11.4 M queued pairs at 600,000 considered in the profile below |
| 4.1 | AC redundancy (s = t equal modulo AC is redundant) | not needed: the AIM signature has no AC operators |
| 4.1 | ground joinability by case splits on variable orderings | **has it** (Twee/Join.hs `groundJoin`, with our branch limit 100) |
| 4.1 | **equations shown redundant by ground joining are kept for simplification, with no critical pairs built from them.** Deleting them "weakens the simplification relation such that many proof tasks are no longer completed within reasonable time" | **missing**. twee files them in `st_joinable`, which only serves the subsumption checks (`subsumed`, Twee.hs:1017, 1126, 1858). It never rewrites with them |
| 4.2 | automatic control: match algebraic laws, then structures, then look up ordering and weights (e.g. Ring → LPO, weight \|s\|+\|t\|) | AIM is one domain; orderings and weights were tested on stalled goals at 20 s (REPORT 2ac, 2ag: no gain) |
| 4.3 | conjectures as successor sets, proved when S(u) and S(v) meet | **has it** (`cfg_set_join_goals = True`, `Rule.normalForms`); `--set-join` does the same for critical pairs (off by default) |

## Candidates to try

1. **Measured 16:48, and dropped.** In an 80 s run of TLRproperties_2 358 (its exp12 A command without
   --quiet), twee ground-joined only **29 equations ("(hard)" lines) against 20,751 rules**. With so few, keeping
   them for rewriting cannot change much on AIM; the paper's gains came from problems where many unorientable
   equations are ground-joinable. What follows is the original candidate.
   **Ground-joined equations as simplifiers without critical pairs** (4.1). In twee: when a critical pair is
   ground-joined, also add it as an unoriented rule for rewriting only (ordered instances), and keep it out of the
   overlap index. Test on the 107 walls at 80 s, against exp11's exact control.
2. **`--set-join` for critical pairs**, a flag that already exists. It is cheap to test on the same walls.
3. **Constant-size passive batches** (3.2). Lower priority: renormalisation took 40 of 679 CPU s in the profile,
   all of it before 120,000 pairs.

## Context: the profile of a 320 s run (16:16-16:28)

TLRproperties_2 358 (an exp12 gap head; its B command with `--progress 20`), CPU per 40,000 pairs considered:

| pairs (k) | CPU s | queue renormalisation | interreduction | rest of the main loop | rules | queued (M) |
|---|---:|---:|---:|---:|---:|---:|
| 40-80 | 45 | 10 | 9 | 25 | 10,812 | 1.6 |
| 80-120 | 66 | 30 | 6 | 30 | 16,173 | 2.1 |
| 160-200 | 37 | 0 | 4 | 32 | 24,780 | 3.6 |
| 320-360 | 48 | 0 | 6 | 42 | 38,600 | 6.7 |
| 560-600 | 57 | 0 | 7 | 50 | 57,697 | 11.4 |

The rest of the main loop grows about 1.6 times from 160k to 600k pairs, with the rule set: normalising new
pairs, joining tests, the rule model and PG. Hint upkeep is 4.3 s in all. GC is not the cause (`+RTS -s`, the same command, 16:30-16:44):
* 80 s: GC 8.3 of 164.6 s (5%), maximum residency 191 MB;
* 320 s: GC 43.9 of 719.1 s (6%), maximum residency 631 MB.
* twee allocates about 1 MB per pair considered (167 GB, then 631 GB), nearly all of it short-lived.
* On this goal the mutator time grew 4.3-fold for 4 times the pairs, so the goal itself slows little; the
  population median is 1.9-fold (REPORT 2ay).

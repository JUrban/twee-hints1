# Hint guidance for twee: interim report

Branch `hints` of the twee repo. Scripts are in `hints/`. Runs and data are
in `/project/hintwork` (not in git).

## 1. What is implemented

### Equation hints in twee (`src/Twee.hs`, `executable/SequentialMain.hs`)

* **Hint input.** `--hints-file F` reads one hint per line as
  `lhs<TAB>rhs[<TAB>factor]`, in TPTP term syntax. Uppercase names are
  variables. A fast hand-written parser is used, because putting hints into
  the TPTP problem (`cnf(h,axiom,'$hinteq'(l,r))`, also supported) costs
  about 0.12 ms per hint in jukebox. Hints with symbols that are not in the
  problem are dropped.
* **Matching** follows Prover9's equivalence match. A critical pair matches
  a hint if its simplified equation is a variant of the hint, in either
  orientation. The match is done on canonical forms stored in a `Map`. A
  matching critical pair gets the score `s * eqhint-factor + eqhint-weight`
  (factor 0.01 by default), so it is selected next.
* **Back-demodulation of hints** (Prover9's `back_demod_hints`). Live hints
  are re-normalised with the oriented rules every 20 ms, within at most 5%
  of the time. Every form a hint has had is remembered. A hint that
  normalises to `t = t` counts as joined.
* **Goal constants.** Twee flattens goals by default: `ld(x0,e)` becomes a
  constant `ld2`, and so on. Without flattening twee solves 1176/3052 on
  dev10 instead of 1753, so flattening must stay on. Before matching,
  flattening constants are replaced by their definitions and skolems by
  variables. Hints are stored in this general form, so they also transfer
  between problems.
* **Consider-emulation.** If the fingerprint matches but the simplified
  equation does not, the steps of `allSteps` (oriented and unoriented
  rewriting, connectedness) are run on the critical pair, and the rules it
  would produce are looked up. This catches pairs that differ from the hint
  only by ordered rewriting with permutative rules such as
  `t(t(x,y),z) = t(t(x,z),y)`.
* **Fingerprint prefilter.** A hash of the symbol multiset of an equation
  is invariant under renaming, orientation and permutative rewriting. Only
  critical pairs whose fingerprint occurs among the hints are canonicalised
  and looked up. This cut the matching overhead from about 30% to about 7%
  of throughput.
* **Hint-triggered requeue** (`--eqhint-requeue F`). This is Prover9's
  back-demodulation of sos. Twee keeps queued critical pairs in the form
  they had when they were generated. When the rule that would normalise a
  pair into a hint arrives later, the pair would otherwise never match.
  The new task re-simplifies the queue whenever new rules have matched
  hints, using at most the fraction F of the time.
* **Output and diagnostics.**
  * `--print-hints` prints all lemmas of the raw proof, after flattening
    definitions are eliminated, plus the goals.
  * `--track-hints F` reports when rules match the given equations, without
    changing the search.
  * `--eqhint-debug` traces matching critical pairs.
  * `HINTSTATS` line: hints, live, joined, matched, tracked.
* **Per-hint factors.** The optional third column of the hints file
  overrides the boost factor for that hint.

### Scripts (`hints/`)

* `run.py`: parallel runner.
* `loop.py`: Veroff-style hint loop. Round 0 runs without hints, and later
  rounds run every unsolved problem with hints. Pools can be `original`,
  `all`, or `knn:K:N`.
* `transfer.py`: leave-one-out transfer benchmark.
* `hintsel.py`: kNN hint selection.
* `feats.py`: term-shape features.
* `diag2.py`: replay diagnosis, showing which hint was late and its parents.
* `mkhints.py`: generalised hint files from a twee proof.

## 2. Results so far

The dev10 set has all 3052 goals of 10 originals of mixed difficulty:
`aK1_to_aK2 mbol_com aa1_15 aK2_eq_aK3_q a_of_aa aa2_to_aa3 nil3_15
aa1_45_c Ka_eq_aK3 aK2_eq_aK3_b`. All runs use 20 processes in parallel.

| system on dev10 | solved |
|---|---|
| E 2.6, 1 s (README baseline) | 1036 |
| Prover9, 1 s (README baseline) | 1112 |
| twee 2 s, no hints | 1753 / 1771 (two runs) |
| twee 2 s `--no-flatten-goal` | 1176 |
| loop L1: 2 s, pool = all proofs of the same original | 1771 → 1833 → 1835 → 1836 |
| loop L2: 2 s, kNN pool (30 neighbours, 100 hints) | 1771 → 1836 → ... |

### Self-replay: a problem rerun with hints from its own twee proof

`aK2_eq_aK3_b__goal_315`, 89 generalised hints:

| setting | rules | time |
|---|---|---|
| no hints | 2283 | 2.4 s |
| hints, before goal-constant expansion | 2221 | 2.3 s |
| + goal-constant expansion | 1192 | 1.2 s |
| + requeue 0.1 | 334 | 0.16 s |

The diagnosis tool showed what was still late before requeue. The critical
pairs were generated before the rule that normalises them into the hint
existed, and they were not looked at again.

### Transfer benchmark T1

Leave-one-out with hints from the other 1835 proofs, 4 s limit. The set has
176 problems solved in 0.8–2 s plus 100 problems unsolved at 2 s.

| hint selection | slow-solved (176) | PAR2 | unsolved (100) |
|---|---|---|---|
| none | 176 | 1.51 | 6 |
| all of the same original (~1000 hints) | 164 | 1.84 | 11 |
| 10 nearest by proof line | 171 | 1.14 | 8 |
| kNN 30 neighbours, top 100 hints | 175 | 0.71 | 10 |

### Why pools from all proofs of an original fail

Offline over 200 solved problems: the pool of all other proofs of the same
original contains 71% of the lemmas of the problem's own proof, but only
2.4% of the pool's hints are in that proof. Every matched hint becomes a
rule at top priority and then forms critical pairs with every other rule.
In one traced case, `aa1_45_c__goal_224`, 223 irrelevant hint rules came
first and delayed the real proof's lemmas by about 230 rules.

kNN by goal-statement similarity (idf-weighted Jaccard on term shapes of
depth ≤ 3) across all originals does better: recall 0.74 and precision 0.26
at 100 hints. With 400 hints, recall is 0.81.

## 3. Assessment

* Hint guidance works mechanically. Self-replay is 15× faster.
* Transfer between goals is the weak point. About 25–30% of a proof's
  lemmas occur in no other proof, and irrelevant hints cost time.
* The hard remaining goals are late goals whose neighbours in the original
  proof are unsolved too. The chain of hints breaks there.

## 4. Next steps

* Compare a hint loop with increasing time limits (2 s → 8 s → 30 s)
  against a no-hint baseline given the same extra time. This is the fair
  measure.
* Per-hint factors from kNN scores. More relevant hints should get
  stronger boosts.
* Requeue together with kNN hints, with the budget tuned.
* Scale up to more originals and the full benchmark.
* The Prover9-new branches deal with very large hint banks: millions of
  hints in the Josef runs, packed and compiled matchers, and a
  generalised-hash subsumption table. At our pool sizes (≤ 10^4) matching
  cost is not the bottleneck, so none of that is ported yet. Their
  generalised hash (precomputing hint generalisations) is the obvious way
  to add subsumption matching ("critical pair is more general than the
  hint") if it turns out to matter.

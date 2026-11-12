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
| loop L2: 2 s, kNN pool (30 neighbours, 100 hints) | 1771 → 1836 → 1845 → 1848 |
| L2 continued at 8 s (two rounds) | → 1944 → 1955 |
| no hints: 2 s, then 8 s on the unsolved | 1771 → 1928 |

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

### Hints against extra time

Plain twee at 2 s and then 8 s on what is left solves 1928. The hint loop
with the same final limit solves 1945 after its first 8 s round. Hints add
only +17 at these limits; the union is 1958. Most dev10 goals are solved
early or not at all, so at 2–8 s there is little room for hints. Hints
should matter more in long runs that would otherwise lose their way (see
the stall cutoff below).

### Learned hint ranking (ENIGMA features, LightGBM)

`lgbsel.py` reranks the kNN candidates with LightGBM. A row has pair
features (kNN score, frequency) plus ENIGMA-style features of the hint and
of the goal. Training and testing are on different originals.

| hints | recall@100 | precision@100 |
|---|---|---|
| kNN | 0.838 | 0.154 |
| LightGBM rerank | 0.849 | 0.156 |
| all 600 kNN candidates | 0.856 | |

Reranking gains little, because kNN candidates already cap recall at 0.856.
The missing lemmas are in no neighbour's proof.

## 2b. ENIGMA for twee: a learned rule filter

ENIGMA's "enigmatic" featurizer (E prover, ai4reason `enigma` branch,
`che_enigmaticvectors.c`) is ported for unit equations:

* vertical walks of length 2–3 from the `=` root (variables as `*`)
* horizontal features `f.head(arg1)...`
* symbol counts and symbol max depths
* length statistics
* the conjecture as a separate goal block
* overlap counts between rule and goal, and log(rule number)

Python (`enigfeats.py`) and Haskell (`src/Twee/Enigma.hs`) compute the same
features. On test rules, twee's raw scores equal LightGBM's exactly.

**Training data.** `--print-given` logs every rule added. `given.py` labels
each rule: 1 if it is a proof lemma, 0 otherwise, -1 for axioms. Round 0 of
dev10 gives 1771 runs, with 26.7k positive and 605k negative rules.

**Offline**, on 3 held-out originals (253 problems):

* AUC 0.969.
* At threshold 0.1, 97.9% of proof rules are kept and 68.5% of the others
  are rejected.
* The rules up to the proof shrink to 36%.

**In twee** (`--rule-model M --rule-vocab V --rule-goal G`), a critical
pair that would become a new rule is first scored. If the predicted
probability is below the threshold, the pair goes back into the queue once,
with its score times the penalty (default 2). Hint-boosted pairs come back
at once, because their scores are tiny.

The test set is the 345 problems of the held-out originals (aa1_45_c,
mbol_com, nil3_15) that are unsolved at 2 s, run at 8 s:

| system | solved |
|---|---|
| twee, no guidance | 42 |
| hint loop, all rounds (2 s ×3 + 8 s) | 46 |
| rule model, threshold 0.1 | 57 |
| rule model, threshold 0.2 | 40 |
| rule model + kNN hints (100) | **68** |
| union of all runs | 83 |

mbol_com gets 0 with the model, against 4 without. Its theory is unlike
the 7 training originals. Next step: train on many more originals.

### More training data, and ProofWatch

* **Model rm2** is trained on 30 more training originals (12,414 problems;
  7059 solved at 2 s without guidance) plus dev10's 7 training originals.
  On the 3 held-out originals: AUC 0.975 (0.969 before). At threshold 0.1
  it keeps 99.5% of proof rules and rejects 61.6% of the others. Online on
  the 345: 65 solved at threshold 0.1 and 69 at 0.2, both with kNN hints.
  mbol_com is still weak (0–2 against 4). The union of all variants is 93.
* **ProofWatch** (`--eqhint-watch F`). Each hint carries the neighbour
  proofs it comes from, as a 4th column of the hints file. Its factor moves
  from F to its own factor (0.01) as its best source proof gets matched.
  With F = 0.3, on the same 345 with rm2: 67 solved, against 69 without
  (+2/−4). This setting does not help.

### Fixes after the first holdout run, and tuning

The first holdout loop (H1: rm3, threshold 0.2, penalty 2, text model)
solved 3132 at 2 s against 3049 for plain twee. But it lost 123 problems
that plain twee solves, many in under 0.1 s. Two causes:

* **Loading the text model** took about 0.25 s per run, because Haskell's
  `read` is slow on about 100k numbers. `lgb2bin.py` now writes a binary
  forest. It loads in 0.07 s and gives identical predictions.
* **Repeated deferral.** The same equation, reached through different
  critical pairs, was deferred up to 18 times. Each equation is now
  deferred at most once.

Tuning on dev (all 818 goals of the 3 held-out dev10 originals, 2 s, rm2):

| setting | solved |
|---|---|
| plain | 473 |
| threshold 0.1, penalty 2 | 498 (+27/−2) |
| threshold 0.1, penalty 3 | 499 (+29/−3) |
| threshold 0.2, penalty 1.5 | 490 |
| threshold 0.2, penalty 2 | 488 |
| threshold 0.05, penalty 2 | 488 |
| threshold 0.5, penalty 1.2 | 476 |

Parent features (ENIGMA's parental blocks, or a cheap Deepire substitute)
reach AUC 0.971 against 0.969 without them, so they are left off for now.

## 2e. Holdout evaluation (AIM60k `holdout.names`, 5880 problems)

The README reserves the holdout split for reporting. Nothing below is
trained or tuned on it:

* Model rm3 is trained on the 30 extra training originals plus dev10,
  with every holdout problem removed (`given/train_only`).
* The hint pool starts as the proofs of those training problems
  (`hints/train_pool`, 8562). The loop then adds the holdout problems it
  solves itself, as a Veroff loop would.
* Threshold and penalty were tuned on dev originals.

All runs use 20 processes in parallel on a 112-core machine.

| system | 2 s | after the 8 s round(s) |
|---|---|---|
| E 2.6, 1 s (README) | 1853 | |
| Prover9, 1 s (README) | 1911 | |
| H0: twee, plain (2 s, then 8 s on the unsolved) | 3049 | **3385** |
| H3: twee + rule model | 3105 (+126/−70) | (stopped after 2 s) |
| H2: twee + rule model + kNN hints, loop 2, 2, 8, 8 s | 3177 (+190/−62) → round 1: 3221 | (running) |

Most problems the model loses at 2 s are boundary cases solved by plain
twee in 1–2 s. The model's overhead is now about 6% of throughput, after a
binary model file, a dense feature array and hashed feature names.

## 2c. Long runs: stall cutoff and checkpoints

* `--eqhint-stall N` gives up when no new rule has matched a hint for N
  rules. This is Veroff's practice of stopping lost jobs. `HINTSTATS` now
  reports `lastmatch` and `maxgap`, the largest gap between matches, to
  calibrate N on solved runs.
* `--load-state F` resumes a run saved with `--dump-state`, with the hints
  given now. On the new state it re-normalises the hints and re-scores the
  queue. A 1 s run dumped (1.5 MB) and resumed solves in 1.4 s, against
  2.3 s from scratch. Long runs can be continued with new hints instead of
  being restarted, as with Prover9-new's checkpoints.

## 2d. Prover9-new branches: what was ported

| branch | what it does | decision |
|---|---|---|
| packed-fast, better-packed, faster-packed-fallback, adaptive-hint-mask-filter, lazy-hash-gate | fast matching against very large hint banks (millions of hints, Josef runs): packed matchers, 64-bit checklists, bit tables | not ported. With ≤ 10^3 hints per run, matching costs about 7% of twee's throughput after the fingerprint prefilter, which plays the same role. |
| experimental-generalized-hint-hash | subsumption matching by hashing precomputed hint generalisations | not ported yet. This is the way to add "critical pair more general than a hint" matches; twee currently matches variants only, plus consider-emulation. A more general rule makes the hint joinable, but the pair that produced the rule gets no boost. Worth trying if transfer hints turn out to be too specific. |
| proof-parent-guidance, proof-recipe-replay | replay a known proof's parent graph | covered by self-replay with own-proof hints (15× faster). Not useful for new problems. |
| target-directed-inference | hash-guided inference toward targets | the branch reports a no-go; not ported. |
| long-run-scalability, ancestor store, compact indexing, checkpoints | memory and restart for runs with 10^5+ given clauses | checkpoints ported as `--load-state` (twee already had `--dump-state`). Twee's AIM runs are far from those memory limits. |
| (master) back_demod_hints, sos back-demodulation | re-simplify hints and queued clauses | ported as `--eqhint-normalise` and `--eqhint-requeue`. |

## 3. Assessment

* **Hints work mechanically.** Self-replay with a problem's own proof is
  15× faster.
* **Transferred hints help, modestly.**
  * Selection is capped. kNN recall@100 is about 0.82–0.84, and learned
    rerankers (LightGBM on ENIGMA features, or the rule model) add at most
    0.01.
  * At 2–8 s on dev10, the hint loop gives +17 over plain twee at the same
    final limit.
  * With the rule model on holdout at 2 s, hints add +106/−34.
* **The ENIGMA-style rule model is the biggest single gain so far.** It
  reaches AUC 0.975 on held-out originals and adds +5–6% at 2 s on unseen
  originals, more on the hard subset at 8 s (+36%). It is complementary to
  hints.
* **ProofWatch boosting, parent features, reranking hints with the rule
  model:** neutral so far.
* **Long runs.** Plain twee at 60 s solves 26 of 59 hard problems that no
  8 s setting solved. Much of the remaining headroom is time, which is
  where hints are expected to help most (Veroff). The long-run comparisons
  are below.

## 4. Next steps

* Long runs on hard problems: hints, goal-statement hints, the stall
  cutoff, resuming from checkpoints with new hints.
* ENIGMA loop: retrain the rule model on data from guided runs, including
  the newly solved harder problems.
* A full run on all public problems.
* Generalisation matching ("critical pair more general than a hint"), as in
  Prover9-new's generalized hint hash.

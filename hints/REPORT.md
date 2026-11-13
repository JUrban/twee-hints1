# Hint guidance for twee: report

Branch `hints` of the twee repo. Scripts are in `hints/`. Runs and data are
in `/project/hintwork` (not in git).

**Summary.** On all 51,784 public AIM60k problems, with 4 s per problem:

| system | solved | holdout | CPU h |
|---|---|---|---|
| plain twee, 4 s | 31,060 | 3203 | 28.1 |
| loop, 2 + 2 s | **33,249** (+7.0%) | **3417** (+6.7%) | 24.5 |
| the loop, a third 2 s round | 33,668 | 3473 | 35.0 |

The loop's first round is twee with a learned ENIGMA-style rule filter
plus kNN hints from training proofs. Its second round adds hints from its
own proofs and proven sibling goals as lemmas. On hard holdout problems
at 60 s, it solves 56 against 44 for plain twee. Section 3 says where the
gains come from, and why hints from other problems help little in long
runs. Section 5 has the commands.

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
* `given.py`: given-rule logs labelled for training (`--print-given`).
* `rulemodel.py`, `enigfeats.py`, `lgb2bin.py`: the ENIGMA rule model
  (section 2b).
* `lemmas.py`: lemma import (2g). `sketch.py`, `chainhints.py`: sketches.
* `summary.py`: solved problems per AIM60k part.

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
| H2: twee + rule model + kNN hints, loop 2, 2, 8, 8 s | 3177 (+190/−62) → round 1: 3221 | round 2: 3505 → round 3: **3551** |

Against H0 at the same final limit, H2 gains 195 and loses 29; the union
is 3580 (+4.9% over plain twee). Round 3 runs 8 s again, with hints
refreshed from the loop's own new proofs, and adds 46. That is the hint
loop's own contribution at a fixed time limit.

Most problems the model loses at 2 s are boundary cases solved by plain
twee in 1–2 s. The model's overhead is now about 6% of throughput, after a
binary model file, a dense feature array and hashed feature names.

## 2f. The ENIGMA loop, and generalisation matching

* **ENIGMA loop.** Guided runs (rm3, kNN hints, 4 s) on the 5355 training
  problems that plain twee leaves unsolved at 2 s solved 757 of them.
  Their given-rule logs (`given/tr30_g1`) are added to the training data
  of model rm4. These are harder proofs than the plain 2 s ones, from the
  guided search the model has to work in.
  * On 600 random holdout problems still unsolved after H2: 8 for rm3 and
    8 for rm4 at 8 s (4 different each), too few to tell.
  * On the 345 hard dev goals (`ho3_unsolved`, 8 s, model only, no hints):
    rm3 60, rm4 **63** (+4/−1).
  Both rm3 and rm4 were trained on the solved goals of these three
  originals (not on the 345 themselves), so this compares the two models
  in the setting of a loop over one batch, not on unseen originals.
  rm4 is used from here on.
* **Run-to-run noise.** Twee's background tasks are time-based, so runs
  differ. rm4 repeated on the 345 gives 61 against 63 (+0/−2). Differences
  of ±3 there are noise.
* **A second turn (rm5)** adds the 2687 training-split problems that the
  full-benchmark loop (below) solved with rm4 in 0.3–2 s, giving 2.7M rows
  and 290k positives. It does worse on the 345: 58 against 61–63 for rm4
  (+2/−7). More guided proofs of medium difficulty do not help as they
  are. The model may need more capacity or a retuned threshold for the
  larger data; rm4 stays.
* **More capacity (rm4b):** rm4's data with 400 trees of 127 leaves (four
  times the model). On the 345: 65 against 61–63 (+9/−7), within noise.
  Loading takes 0.15 s instead of 0.07 s. Not worth it at short limits.
* **Generalisation matching** (`--eqhint-generalise`, after Prover9-new's
  generalized hint hash). Each hint is also stored with its one-step
  generalisations (one proper non-variable subterm of one side replaced
  by a fresh variable), so a critical pair more general than a
  hint gets the hint's boost. On the 345 with rm2 and kNN hints at 8 s:
  68 against 69 without it. Neutral, left off.

## 2g. Lemma import: proven sibling goals as axioms

All goals `X__goal_N` of one original `X` have the same axioms (checked).
A sibling goal that twee has proven is therefore a theorem of the theory
and a sound extra axiom for the others. This is what CASC's LTB division
allows within a batch: conjectures proven earlier may be used later. It
leans on the batch structure more than hints do, so it is reported
separately from the hint results.

* `lemmas.py` adds the statements of up to M proven siblings, those with
  the nearest goal numbers below N (unit equations only), to the problem.
* `loop.py --lemmas M` does this in rounds after the first, with lemmas
  proven in earlier rounds only. So the chain of lemma proofs is
  well-founded, and each final proof can be expanded into one from the
  axioms. In the training logs, lemma axioms are labelled as axioms.

On the 59 hard dev goals at 20 s (lemmas from the 1966 dev10 problems
solved at 2–8 s):

| setting (20 s) | solved |
|---|---|
| plain (the 60 s run, solved within 20 s) | 12 |
| plain + 10 lemmas | 21 |
| rm4 | 19 |
| rm4 + 3 lemmas | **28** |
| rm4 + 10 lemmas | 27 |
| rm4 + 30 lemmas | 26 |
| rm4 + 10 lemmas + kNN hints | 27 |

Lemmas and the rule model add up. Three lemmas are enough, and more do not
help. Hints add nothing on top.

On the 345 hard goals of the three dev originals at 8 s, lemmas come from
the 473 goals plain twee solves at 2 s, and every goal gets three. rm4
solves 63 and rm4 + 3 lemmas 68 (+10/−5): a smaller gain than on the 59.
Those 59 were chosen to have solved goals shortly before them. With 6
lemmas: 70 (+6/−4 against 3), within noise.

* **Which lemmas are used.** Most proofs that had lemmas use at least one
  (46 of 56 on the hard holdout set below), and not only the nearest: the
  third nearest is used most often there (29).
* **Lemmas into a resumed run** (`--load-state` now adds the problem's new
  axioms). This does not work. The lemma becomes a rule, but its
  consequences go into a large queue scored like everything else. One goal
  that 3 lemmas solve in 0.4 s from scratch takes 3.5 s when resumed from a
  2 s state, the same as resuming without the lemmas. Restarting with the
  lemmas is better, so lemma rounds restart.

### Sketches (Veroff): hints from proofs under extra assumptions

Veroff's sketches are proofs found with extra assumptions; their steps then
serve as hints for the real problem. Here the extra assumptions are the
nearest sibling goals below N, proven or not (`sketch.py`). That is
unsound as a proof but sound as a source of hints.

* On the 59 at 5 s, with rm4: 15 sketch problems are proven with 3 assumed
  siblings, and 19 with 10. Six of those goals are unsolved by rm4 + 3
  proven lemmas at 20 s.
* The real run (rm4 + 3 proven lemmas, 20 s) with these sketch hints: 28,
  the same as without them. The 6 stay unsolved. A sketch covers only the
  stretch from the assumed siblings to the goal. Deriving the assumed
  siblings is the hard part, and it is not covered.
* **Chained sketches.** Sketch every unsolved dev10 goal (389 of 1204
  proven at 5 s with 10 assumed siblings). The hints for goal N are then
  the sketch hints of N and of the sketched siblings in [N−30, N], nearest
  first, at most 400 (`chainhints.py`, 154 on average). Result: 29
  against 28 (+2/−1), within noise. Only a third of the links have
  sketches, so the chains have gaps.

## 2h. The full public benchmark (all 51,784 problems, 4 s per problem)

Every system gets at most 4 s per problem:

* plain twee: one 4 s run, 8 in parallel;
* the loop:
  * round 0: 2 s with rm4 and kNN hints from the start. The pool is the
    training-split proofs (`train_pool` 8562, `tr30_g1_pool` 757).
  * round 1: 2 s on the unsolved, with the pool extended by the loop's own
    round-0 proofs. 12 in parallel.
* the loop + lemmas: the same round 0, then round 1 with 3 proven siblings
  as axioms as well (section 2g).

| system | train | devel | holdout | all | CPU h |
|---|---|---|---|---|---|
| E 2.6, 1 s (README) | | | | 18,369 | |
| Prover9, 1 s (README) | | | | 18,973 | |
| twee, plain, 4 s | 25,416 | 2,441 | 3,203 | 31,060 | 28.1 |
| loop, round 0 only (2 s) | 26,144 | 2,551 | 3,257 | 31,952 | 13.5 |
| loop, 2 + 2 s | 26,493 | 2,578 | 3,306 | 32,377 (+4.2%) | 24.8 |
| loop + lemmas, 2 + 2 s | 27,190 | 2,642 | **3,417** | **33,249 (+7.0%)** | 24.5 |

* Against plain 4 s, the loop with lemmas gains 2530 and loses 341, of
  which 247 plain twee solves in 2–4 s. On holdout it is +265/−51. The
  union of the two is 33,590.
* Round 0 alone, at half the time limit, already solves more than plain
  twee at 4 s.
* Lemmas triple what round 1 adds (1297 against 425 new), at the same CPU.
* **A third round** (2 s, lemmas and hints from rounds 0–1) adds 419,
  giving **33,668** (holdout 3473, +8.4% over plain 4 s), with up to 6 s
  per problem.
* **Speed.** Problems solved within a time, holdout only:

  | within | plain | loop round 0 |
  |---|---|---|
  | 0.25 s | 2309 | 2697 |
  | 0.5 s | 2541 | 2924 |
  | 1 s | 2776 | 3067 |
  | 2 s | 3005 | 3248 |

  Within 1 s the loop solves more than plain twee within 2 s.
* **What is clean.** On the train split, rm4 and the kNN pool contain
  proofs of many of these very problems' siblings (and rm4 of many 2 s
  proofs of the problems themselves), so the train and devel columns are
  optimistic. Holdout is clean as the README defines it:
  * no holdout problem is in any training data or pool;
  * its originals are unseen, except the 1160 late goals moved from
    training originals in step 2 of the split;
  * the loop learns from holdout only what it proves itself during the
    loop.

### Long runs on hard holdout problems (60 s)

The set is 300 random holdout problems that neither plain twee at 4 s nor
the loop (2 + 2 s) solved. Lemmas are 3 proven siblings, from everything
proven in the full-benchmark runs.

| setting (60 s) | solved | vs plain | CPU h |
|---|---|---|---|
| plain | 44 | | 4.7 |
| rm4 | 53 | +11/−2 | 4.5 |
| plain + 3 lemmas | 50 | +12/−6 | 4.5 |
| rm4 + 3 lemmas + kNN hints | **56** (+27%) | +17/−5 | 4.4 |

The union with plain is 61. On unseen originals at long times, the model
and the lemmas each give about +6 to +9 net, and together +12.
**A final 60 s round on all remaining holdout problems.** It covers the
2366 holdout problems that no 4–6 s run solved (rm4, 3 lemmas, kNN hints,
2 hours on 18 cores) and solves 399. That brings
holdout to **3913 of 5880 (66.5%)**. The count includes 40 problems
solved only by the plain 4 s run. For comparison, plain twee at 2 s and
then 8 s solved 3385.

No time-sliced portfolio beats the guided run alone. Plain for 15 s
followed by the guided setting for 45 s solves 50, and rm4 for 40 s
followed by lemmas for 20 s solves 56.

## 2i. Control: a Prover9 hint loop on two families

Prover9-new (master, built from `/project/Prover9-new`, default settings)
in the same loop as twee (`p9loop.py`). The families are aa1_15 (198
goals) and aK2_eq_aK3_q (273 goals), 471 problems, with rounds of 2, 2, 2
and 8 s. Hints are the positive proof steps of all solved goals of the
same original, with skolems generalised to variables (Veroff's practice).
They are given as `formulas(hints)`, about 14 per proof. twee runs plain,
without the model, with the same pool (`--pool original`).

| | round 0, 2 s | +2 s, hints | +2 s, hints | +8 s, hints |
|---|---|---|---|---|
| Prover9 | 240 | 248 | 270 | **288** |
| twee | 347 | 361 | 362 | **376** |

Controls on the round-0 failures, 8 s each:

| control | Prover9 | twee |
|---|---|---|
| no hints | +3 of 231 (243) | +20 of 124 (367) |
| hints = statements of all earlier goals of the original, solved or not | +11 | |

* **Prover9 is a good hint user.** Without hints, four times the time
  gives it almost nothing (+3). Proof-step hints from solved siblings give
  +48, a 19% gain, and the gain grows as the pool grows (+8, then +22).
  Goal statements alone are much weaker hints (+11) than proof steps.
* **Twee gains less from hints:** +29 from the loop against +20 from the
  same time without hints.
* **In absolute terms twee without hints (367) is far ahead of Prover9
  with the hint loop (288).** Prover9's base search on these problems is
  the limit, not its use of hints. Prover9 was run with defaults; Veroff's
  tuned settings might do better.

## 2j. Skolem-free hints, and conditional goals

Veroff turns each proof into a strictly forward, demodulation-free (SFDF)
proof before using it as hints. He iterates Prover9 until the proof no
longer uses the denial, so the hints contain no skolems and carry over to
other problems.

* **Twee gets skolem-free hints without this work.** Completion never
  draws inferences from the negated goal; the goal is only rewritten.
  Every proof lemma therefore follows from the axioms plus the flattening
  definitions, which are conservative. Eliminating the definitions and
  replacing the skolems by variables gives general lemmas.
  * Check: 40 random solved problems, all 814 of their pool hints posed as
    conjectures from the problem's axioms. 807 were proved by twee within
    15 s, and one more within 90 s.
  * The other 6 are false, e.g. `m(X0,X1) = m(X2,X3)`.
* **The hole: conditional goals.**
  * 9,052 of the 51,784 public problems (17%) have goals of the form
    `A = B → C = D`.
  * The hypothesis becomes a ground clause with skolems. Lemmas derived
    from it, and the conclusion itself, hold only for those skolems.
  * Generalising them gave the 6 false hints.
  * In 300 solved conditional problems, 27% of the hints depended on the
    hypothesis.
  * Proofs stayed sound: hints only steer the search, and lemma import
    takes only unit-equation goals. The pools got noise, however.
* **Fix (twee-e14).**
  * `--print-hints` traces each lemma's derivation, and lemmas and goals
    that use a hypothesis go into a new `HINTS-HYP` section.
  * Pools skip that section, while rule-model labels still count those
    lemmas as proof lemmas.
  * `cleanpool.py` cleans existing pools. It removed 19% of the hints of
    the conditional problems in `train_pool` (2,965 hints) and 3% in
    `tr30_g1_pool`.
* **Effect: none measurable.**
  * Test set: the 310 conditional holdout problems that plain twee does
    not solve in 4 s. Settings: rm4 + kNN hints (30 neighbours, 100 hints)
    from `train_pool` + `tr30_g1_pool`, 8,000 critical pairs each
    (`--abstract-time 2000 --max-time 4`).
  * rm4 alone solves 11. With the old pools it solves 17, and with the
    cleaned pools also 17: the same 17 problems.
  * The time-limited version of this test (4 s on a loaded machine) gave
    20 against 18. The two extra solutions of the old pools were finished
    at 4.0–4.1 s, so they were load noise (see section 2k).
  * kNN hints do help on conditional problems (+6 of 310). The false
    generalised hints were noise, not harm, at this budget.
* **Demodulation-free hints do not fit twee.** Twee normalises every
  critical pair before it can match a hint, so unnormalised intermediate
  steps would never match. Twee's counterpart of SFDF robustness:
  * back-demodulated hints, with every form a hint has had remembered;
  * requeue of the passive queue.

  Self-replay goes from 2,283 to 334 rules with them (section 2).
* **The Prover9 control (2i) did not use SFDF hints.** `p9loop.py` drops
  the denial-side clauses instead.
  * Of 120 Prover9 proofs in those families, 99 were already strictly
    forward; the other 21 had 27 denial-side steps.
  * 327 of the 734 steps used demodulation, so SFDF hints might help
    Prover9 somewhat.
  * The two families have unit goals, so the hypothesis problem does not
    affect them. On conditional goals, `p9loop.py`'s skolem
    generalisation would have the same flaw.
* **A cheaper reorientation than iterating the prover.**
  * A twee proof is already a chain of single rewrite steps per lemma and
    for the goal. Each prefix `s = t_i` follows from `s = t_{i-1}` by one
    paramodulation.
  * So an SFDF derivation can be read off the proof in linear time, with
    no search; the same holds for Prover9's denial chain read backwards.
  * For a conditional goal, "forward" means from the axioms plus the
    hypotheses, which is what the dependency trace marks.

## 2k. Abstract time

Earlier comparisons in this report used time limits on a shared machine.
The load from other jobs was up to about 22 on the 20 CPUs. Both the
`--max-time` limit and twee's housekeeping tasks (hint normalisation,
requeue, interreduction) follow CPU time, so results depended on the load.
That is part of the ±3 noise on 345 problems (section 2f).

* **Implementation (twee-e15).** `--abstract-time N` makes the clock count
  critical pairs considered, with N of them per second. Both `--max-time`
  and the task scheduling follow this clock.
* **Determinism.** Runs now repeat exactly: two problems, 6 runs each,
  gave identical results and counts.
* **Calibration.** On 60 holdout problems twee considers a median of 1,800
  critical pairs per CPU second (quartiles 1,700 and 2,300). So
  `--abstract-time 2000` keeps the old budgets roughly comparable.
* **Reporting.** Twee prints `WORK considered=N rules=M`, and `run.py`
  stores it as a fourth column. `run.py --wall-factor 5` (and `loop.py`
  when its args contain `--abstract-time`) allows the wall-clock safety
  limit to be exceeded.
* **Real time is a cost, measured separately.** Abstract time leaves out
  the overhead of the rule model and of hint matching. That overhead
  should be reported on its own, measured on a quiet machine.

## 2l. Axiom groups: lemmas and hints across originals

Lemma import (2g) used only proven siblings of the same original, because
those have the same axioms. But originals share axioms too.

* **Facts** (all 51,784 public problems):
  * The 129 originals use 68 distinct axiom sets. Axioms are constant
    within an original.
  * The largest groups of identical axioms have 15 originals (7,116 and
    7,200 goals), 13 (5,426) and 6 (3,557).
  * 66 of the 68 axiom sets have strict subsets among the others (127
    pairs). A theorem of a weaker theory holds in the stronger one. For
    example, mbol_KK_a has 279 goals with the same axioms, but 12,873
    goals of weaker theories.
  * Exact duplicates are common: 5,842 groups of identical axioms and
    goal across originals, covering 16,048 problems; 41,578 problems are
    distinct. The loop already solves them together: only 24 unsolved
    problems have a solved duplicate.
  * Only 15% of the kNN hint neighbours (from `train_pool`) of the ho3u
    targets have the target's axioms (median 4 of 30).
* **Tools.**
  * `lemmas.py --knn K [--subsets] --pool F` adds the K proven goals
    most similar to the target goal (idf-weighted Jaccard on term-shape
    features), taken from problems with the same axioms, or with subset
    axioms when `--subsets` is given, from any original.
  * `loop.py --lemma-knn K` does the same inside the loop.
  * `hintsel.py knnfiles ... --subsets` restricts hint neighbours to
    subset theories.
* **Results:** see the abstract-time battery below.

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

### Long runs on hard problems (60 s)

The set has 59 dev10 goals, 6 per original, that no 2 s or 8 s setting
solved. Each has solved goals shortly before it in the original proof, so
relevant hints exist. Model rm3 never saw these problems, but it was
trained on the easier, solved goals of the same originals (dev10 is part
of its training data).

| setting (60 s) | solved | CPU total |
|---|---|---|
| plain | 26 | 2682 s |
| kNN hints (100) | 28 | 2623 s |
| hints = statements of solved earlier goals of the same original (50–213) | 26 | 2494 s |
| hints = all earlier goal statements, solved or not | 29 | 2403 s |
| rule model | 36 | 2110 s |
| rule model + kNN hints | 36 | 2116 s |
| rule model + earlier-goal hints + kNN hints | **37** | 1920 s |
| rule model + kNN hints + `--eqhint-stall 2000` | 18 | 777 s |

* In long runs the rule model gives +10. Hints give +2 to +3 without the
  model and +0 to +1 with it.
* Earlier goal statements are the lines of the original Prover9 proof,
  close to Veroff's sketches. They help a little (+3), mostly when unsolved
  goals are included as hints too.
* A stall cutoff of 2000 rules is far too aggressive for 60 s runs, which
  reach about 20k rules: it loses half the solutions. It is about 35% more
  CPU-efficient, so it would suit a loop with many problems only with a
  much larger N.

### Checkpoints: hints arriving late

On the same 59 hard problems:

* Plain twee runs 30 s and dumps its state (19 solved; about 16 MB per
  state).
* The 40 unsolved are resumed for 30 s more:
  * without hints: +8, giving 27 (one plain 60 s run gives 26), so resume
    is a true continuation;
  * with the kNN hints: +9, giving 28, the same as hints from the start
    for 60 s.

Hints that arrive late do as well as hints from the start here.
`loop.py --resume` builds a checkpointed Veroff loop on this. Unsolved runs
dump their state, and the next round resumes them with the current hints,
so search time accumulates across rounds instead of being redone. Cost: a
19 MB state loads in about 1 s and dumps in about 2 s. That is fine for
rounds of 30 s or more, but about 40% overhead for 8 s rounds.

## 2d. Prover9-new branches: what was ported

| branch | what it does | decision |
|---|---|---|
| packed-fast, better-packed, faster-packed-fallback, adaptive-hint-mask-filter, lazy-hash-gate | fast matching against very large hint banks (millions of hints, Josef runs): packed matchers, 64-bit checklists, bit tables | not ported. With ≤ 10^3 hints per run, matching costs about 7% of twee's throughput after the fingerprint prefilter, which plays the same role. |
| experimental-generalized-hint-hash | subsumption matching by hashing precomputed hint generalisations | ported in a simple form as `--eqhint-generalise` (one-step generalisations of each hint go into the hint map). Neutral on the hard dev set (68 vs 69, section 2f). |
| proof-parent-guidance, proof-recipe-replay | replay a known proof's parent graph | covered by self-replay with own-proof hints (15× faster). Not useful for new problems. |
| target-directed-inference | hash-guided inference toward targets | the branch reports a no-go; not ported. |
| long-run-scalability, ancestor store, compact indexing, checkpoints | memory and restart for runs with 10^5+ given clauses | checkpoints ported as `--load-state` (twee already had `--dump-state`). Twee's AIM runs are far from those memory limits. |
| (master) back_demod_hints, sos back-demodulation | re-simplify hints and queued clauses | ported as `--eqhint-normalise` and `--eqhint-requeue`. |

## 3. Assessment

* **Overall.** On all 51,784 public problems at 4 s per problem, the loop
  (rule model + kNN hints, then lemma import) solves 33,249 against 31,060
  for plain twee (+7.0%), with 13% less CPU. On the clean holdout part the
  gain is +6.7% (3417 vs 3203). Problems are solved about twice as fast in
  the 1–2 s range. On hard holdout problems at 60 s it is +27% (56 vs 44).
* **Where the gain comes from**, largest first:
  1. **The ENIGMA-style rule filter.** It defers rules that LightGBM on
     ENIGMA features predicts are not proof steps. It gives +5–6% at 2 s,
     +36% on hard dev goals at 8 s, and +11 of 300 hard holdout goals at
     60 s.
  2. **Lemma import.** Proven sibling goals become axioms. It triples the
     second round's yield on the full benchmark and gives +12/−6 of 300 at
     60 s. It uses AIM60k's structure (the goals of one original share
     axioms and are steps of one proof), so it is reported separately. It
     is sound, and allowed in a CASC LTB-style batch.
  3. **kNN hints.** They help at short limits (+106/−34 at 2 s on holdout
     with the model) and little at long ones.
* **Hints in long runs: a negative result for twee.** With the model, none
  of these help on hard problems beyond noise (±3 on 345):
  * kNN hints, goal statements, ProofWatch;
  * one-step generalisation matching;
  * sketches and chained sketches (Veroff), with up to 400 hints.

  The reason shows in HINTSTATS: hints match early, and solved runs end a
  median of about 1000 rules after their last match. Transferred hints
  cover the part of a proof that twee finds anyway; the late, hard part is
  specific to the problem. For the same reason a Veroff stall cutoff does
  not separate lost runs from good ones: unsolved runs have similar gaps.
  Self-replay (own proof as hints, 15× faster) shows that the mechanism
  itself works when the hints are right.
* **ENIGMA loop.** One turn with hard guided proofs gives +3 (rm4, within
  noise). A second turn with 2.7k medium guided proofs does worse (rm5).
  More data alone does not improve the model.
* **Engineering.**
  * The rule model costs about 6% of twee's throughput (binary model,
    dense arrays, hashed features).
  * kNN selection is a sparse matrix product (6 ms per problem over a
    9k pool).
  * Checkpoints (`--load-state`) continue runs exactly, with new hints.

## 4. Next steps

* Lemma import with checkpoints: resume a saved run with new proven
  lemmas added as axioms, so lemma rounds do not restart the search.
* More loop rounds on the full benchmark (lemma closure), and
  lemma-selection by relevance rather than goal-number distance.
* The model: more capacity, or training only on hard proofs; thresholds
  per run length (0.2 looked slightly better at 20 s, within noise).
* Hints that cover the late part of proofs. One source is sketches whose
  assumptions are themselves sketched or proven, iterated until the
  chains close. Another is Prover9-style degradation of hint boosts.

## 5. How to run the best system

Build twee from this branch (`cabal build exe:twee`). The commands below
are run in `/project/hintwork`, with `venv` holding lightgbm.

1. **Training data.** Given-rule logs of solved training problems:
   `given.py NAMES OUTDIR --twee BIN --timeout 2`. Rows are label, index,
   rule, and parents.
2. **Rule model.**
   `rulemodel.py DIR1,DIR2 --all --save M.txt --vocab M.vocab`, then
   `lgb2bin.py M.txt M.bin`.
3. **The loop** (round 0: model + kNN hints from training proofs; later
   rounds: hints and 3 proven sibling lemmas from the loop's own proofs):

       loop.py NAMES LOOPDIR --rounds 2 --timeout 2,2 -j 12 --twee BIN \
         --pool knn:30:100 --args= --model --model-fixed M.bin,M.vocab \
         --model-args "--rule-threshold 0.1 --rule-penalty 2" \
         --hints-extra hints/train_pool,hints/tr30_g1_pool --hints-from-start \
         --lemmas 3

   Leave out `--lemmas` for hints only. `summary.py LABEL=LOOPDIR ...`
   counts solved problems per part.
4. **Single long runs:**

       twee P.p --max-time 60 --rule-model M.bin --rule-vocab M.vocab \
         --rule-goal G --hints-file H

   `G` comes from `rulemodel.py goalfiles`, `H` from
   `hintsel.py knnfiles`, and `P.p` with lemmas from `lemmas.py`.

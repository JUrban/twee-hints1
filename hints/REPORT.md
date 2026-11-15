# Hint guidance for twee: report

Branch `hints` of the twee repo. Scripts are in `hints/`. Runs and data are
in `/project/hintwork` (not in git).

**Summary.** On all 51,784 public AIM60k problems, with 4 s per problem:

| system | solved | holdout | CPU h |
|---|---|---|---|
| plain twee, 4 s | 31,060 | 3203 | 28.1 |
| loop, 2 + 2 s | **33,249** (+7.0%) | **3417** (+6.7%) | 24.5 |
| the loop, a third 2 s round | 33,668 | 3473 | 35.0 |
| + Veroff-style online loop, 5 abstract s round (2o)\* | **36,057** (+16.1% over plain) | 3747 | +18.9 |
| + its 20 abstract s round (2o)\* | **39,008** (+25.6% over plain) | 4196 | +167.8 |
| + cascade round, 3 lemmas (2p) | 39,746 | 4291 | +33.7 |
| + cascade round 4, 6 lemmas (2r), 14 Nov 08:31–17:25 | 41,074 (+32.2% over plain) | 4460 | +123.7 |
| + cascade round 5 (2w–2ac), from 14 Nov 17:26; at 15 Nov 07:00 | **43,462** (+39.9% over plain) | **4717** (+47.3%) | +199.5 (+15.4 side workers) |

\* Starts from 33,720 proofs: the third round plus 52 from long runs on
two families (2m). Its time is the summed wall time of the runs, close
to their CPU time.

**Totals over time** (all 51,784 problems; holdout 5,880). From 14 Nov
20:00 on, the counts come from the times the proofs' hints files were
written in loops/UL. Merged proofs count from their merge.

| time | solved | holdout | what ran |
|---|---|---|---|
| 14 Nov 07:00 | 39,008 | 4196 | online loop round done (2o) |
| 14 Nov 08:31 | 39,746 | 4291 | cascade round 3 done (2p) |
| 14 Nov 17:25 | 41,074 | 4460 | cascade round 4 done (2r) |
| 14 Nov 20:00 | 41,369 | 4486 | round 5: resumes without requeue (2w), consider-emulation off (2y) |
| 14 Nov 22:00 | 41,686 | 4512 | proof-line distance (2z) |
| 15 Nov 00:00 | 42,053 | 4558 | stalled goals retried fresh (2aa), sketch climber (2ab) |
| 15 Nov 01:32 | 42,234 | 4576 | fresh run first for goals without one in round 5 (2ab) |
| 15 Nov 03:28 | 42,734 | 4645 | UL13, then retry line gap 21 → 80 (UL14, about 610 an hour) |
| 15 Nov 04:00 | 43,001 | 4680 | A/B 1 of the learned scheduler starts (2ac) |
| 15 Nov 05:15 | 43,272 | 4706 | A/B 1 merged; A/B 2 starts |
| 15 Nov 05:51 | 43,360 | 4709 | A/B 2 merged: the scheduler with 10 s fresh runs wins |
| 15 Nov 07:00 | 43,462 | 4717 | stall: resumes to 80 s, then tail heads first at 320 s (2ac; 8%, dropped at 07:36) |
| 15 Nov 09:05 | 43,502 | 4720 | production cut to 6–12 workers for model tests (2ad); Prover9 side worker from 08:56 |
| 15 Nov 10:12 | 43,661 | | `--retry-knn` (2ae): kNN lemma changes reach the cascade |
| 15 Nov 12:05 | 43,735 | 4745 | unfolded-twee side worker from 11:18 (2af) replaces Prover9's |

From 15 Nov 05:30 the rate fell from hundreds an hour to 50–100. The
cheap new contexts are used up; 58% of the unsolved goals sit behind the
95 originals' tail heads (2ac).

The loop's first round is twee with a learned ENIGMA-style rule filter
plus kNN hints from training proofs. Its second round adds hints from its
own proofs and proven sibling goals as lemmas. The online loop then runs
every goal left in goal order. Each new proof joins its original's hint
pool and the lemma source for the next runs at once, and an original is
given up after 30 failures in a row (2o). On hard holdout problems
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
* **Lemmas into a resumed run** (`--load-state` adds the problem's new
  axioms). *Corrected 13 Nov:* the first test said this does not work, but
  that was a bug. A saved state stores each symbol with its precedence and
  id, and both depend on the problem text. A problem with new lemmas
  therefore got a second signature under the same names, and its lemmas
  and hints could never reach the saved rules. twee-e20 makes the problem
  reuse the saved symbols and recognises new axioms by equation, not name.
  Redone on three goals that 13 lemmas solve (2 s states, 4k critical
  pairs):

  | goal | resumed, old binary | resumed, e20 (after resume) | fresh with lemmas | fresh without |
  |---|---|---|---|---|
  | aK2_eq_aK3_d__goal_353 | fails (+40k) | 134 | 288 | fails at 40k |
  | aK2_eq_aK3_d__goal_354 | fails (+40k) | 55 | 456 | fails at 40k |
  | aK2_eq_aK3_d__goal_357 | fails (+40k) | 13.6k | 12.9k | fails at 40k |

  So resumed runs now take new lemmas about as well as fresh runs, and lemma
  rounds can continue saved searches instead of restarting them.

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
* **Results on ho3u** (345 problems, 16,000 critical pairs each =
  8 abstract s, deterministic). Lemmas from the same axiom group only (no
  `--subsets`); the kNN pool is everything plain twee solves in 4 s on the
  full benchmark, plus the 473 solved ho3 siblings:

  | setting | solved |
  |---|---|
  | plain | 70 |
  | rm4 | 81 |
  | rm4t (theory block) | 87 |
  | rm4 + 3 nearest siblings (old lemma import) | 77 |
  | rm4 + 6 nearest siblings | 78 |
  | rm4t + 3 nearest siblings | 83 |
  | rm4 + 3 nearest + 3 group-kNN lemmas | 83 |
  | rm4 + 6 group-kNN lemmas | 85 |
  | rm4 + 3 nearest + 10 group-kNN lemmas | **91** |

  * In abstract time the old lemma import does not help on ho3u (77 vs
    81: 7 problems lost, 3 gained). Its gains in the time-limited runs
    were within the load noise.
  * Lemmas chosen by goal similarity from the whole axiom group help:
    +10 with 13 lemmas.
  * The theory block (rm4t) gives +6, confirming 2f.
* **Results on r1sim**, a simulated loop round:
  * Set: 1,000 random problems (116 originals) that plain twee does not
    solve in 4 s.
  * Lemma pool: the 31,060 problems plain twee solves in 4 s.
  * Budget: 8,000 critical pairs each (4 abstract s).

  | setting | solved |
  |---|---|
  | rm4 | 92 |
  | rm4t | 94 |
  | rm4 + 3 nearest siblings (old lemma import) | 126 |
  | rm4 + 6 kNN lemmas, subset theories | 150 |
  | rm4 + 3 nearest + 3 kNN, subset theories | 166 |
  | rm4 + 3 nearest + 10 kNN, subset theories | **176** |

  * Relevance-chosen lemmas from the target's own and weaker theories
    nearly double what rm4 solves (+91%), and add 40% over the old lemma
    import.
  * On this broad set the theory block is flat (94 vs 92).
  * **kNN hints on top of the lemmas: +18** (battery 6). rm4 + 3
    nearest + 10 kNN lemmas solves 176. With kNN hints (30 neighbours,
    100 hints) it solves 194 from a pool of all solved problems, and 191
    from a pool limited to the target's own and weaker theories. rm4t
    with the same lemmas solves 180.
  * **Noise floor.** rm4 with `--abstract-time` 1990 and 2010 instead of
    2000 (budget ±0.5%, task timing shifted) solves 93 and 95. At most 3
    problems flip, and none of rm4's 92 is lost. Differences of 10 or more
    on r1sim are real.

## 2m. Long runs: how long do runs stay on hints?

Veroff keeps a hinted run going while it keeps matching hints, with gaps
of up to about a minute, and stops it when it falls off. With abstract
time a run is deterministic, so `stallsim.py` replays every stall limit
from one long run. twee-e16 prints `HINTLOG`, the critical-pair count of
each hint's first match. A run with stall limit G stops at the first gap
of G without a new match; the proof counts if it came before that.

**fam_long:** 60 problems, the first 30 goals of aK2_eq_aK3_d and of
nil3_30 that the full-benchmark loop left unsolved. Each run gets 120
abstract s (240k critical pairs), rm4t, 3 sibling lemmas plus 10
subset-kNN lemmas, and kNN hints (median 144, at most 200).

| stall limit (abstract s) | 5 | 10 | 20 | 30 | 45 | 60 | none |
|---|---|---|---|---|---|---|---|
| solved (with hints) | 33 | 37 | 43 | 49 | 51 | 52 | 52 |
| work (abstract h) | 0.09 | 0.13 | 0.19 | 0.22 | 0.25 | 0.27 | 0.30 |

* **No hints: 51, with hints: 52.** This set is too easy at 120 s to
  show a hint effect.
* **A 60 s gap loses nothing and saves 10% of the work; 30 s loses 3 and
  saves 27%.** Short limits lose many: proofs often come long after the
  last new match. Proofs came at quartiles 1, 4, 20 and 78 s; the last
  new matches of solved runs at 0.7, 2.3, 9.7 and 43.5 s.
* **Runs fall off the hints because the hints run out.** The 3 unsolved
  runs had matched 41 of 76, 50 of 76 and 106 of 200 hints. With small
  kNN lists the stall signal means "list used up", not "search lost".
  Veroff's lists are large, so the next test uses whole-original pools.
* **Five runs got no result.** They are the same five with and without
  hints. Their rate fell below 300 critical pairs per CPU second late in
  the run, so 120 abstract s took more than the 780 s wall limit, and the
  kill lost all output. `--max-cpu S` (twee-e18) is a real-CPU safety
  limit that stops like `--max-time`, prints `CPULIMIT` and keeps the
  output. Counting critical pairs is deterministic, but it is not
  constant work per unit: late critical pairs on big rule sets cost more.
* `--load-state` now counts hints that the loaded rules already match as
  matched, and restarts the stall clock at the loaded count (twee-e17).
  Before, a resumed run counted old matches as new, and
  `--eqhint-stall-cps` fired at once.

**Harder eval:** `sets/v2_hard` has the 8 fam_long failures plus the
next 30 unsolved goals of each original (68). Each run gets 300 abstract s
with rm4t and lemmas, in three versions (`abs/v2.sh`, `loop.py
--keep-out`):

* hints from the whole original pool, all lemmas of the solved siblings,
  most frequent first (1,994 hints for aK2_eq_aK3_d, 1,693 for nil3_30);
* kNN hints;
* no hints.

Each run also has a 1,200 s CPU cap.

* **Whole pool (V2p): 48 of 68.** This includes 3 of the 8 that kNN
  hints left unsolved at 120 s; nil3_30__goal_360 is proved at 60 s.
* **All 19 unsolved runs hit the CPU cap** at 115–261 abstract s, and all
  were still on hints. They had matched 520–690 hints, the last one near
  the end of each run. Per gap limit up to 60 s, 47–48 are solved, and
  all 19 failures count as "keep going" in Veroff's terms.
* **Large pools were expensive.** In the same search (hint score made
  neutral), 20 hints cost +2% CPU, 144 hints +4%, and 1,994 hints +53%.
  The cause was the abstract clock: it does not move while a
  housekeeping task runs, so task budgets never bound and hint
  normalisation ran every 40 critical pairs. Tasks can now report an
  abstract cost (`newTaskCost`); hint normalisation charges live/100
  critical pairs. With that, 1,994 hints cost +11% instead of +43%
  (twee-e19). The other tasks cost about 7% more under the abstract
  clock than under real-time scheduling, which is acceptable. Rarer
  normalisation does not weaken the guidance: 12 round-1 proofs rerun
  with e19 take the same or fewer critical pairs (251k in all, against
  285k) and match nearly the same number of hints.
* **Whole pool 48, kNN 40, no hints 36** (same 300 abstract s, same
  model and lemmas). The whole pool solves 13 that the no-hint run
  misses (and misses 1 it solves); kNN only 5. The two hint versions
  differ in how long the runs stay on hints. kNN runs stop matching
  early: the last new match came at a median of 3 abstract s, in solved
  and unsolved runs alike. With a 60 s gap, 34 kNN runs are solved and
  only 1 unsolved run is still on hints. The whole-pool runs keep
  matching until late: unsolved runs' last matches came at 131–228 s.
  So the stall signal is only informative with a large pool.
* **48% of the new proofs' lemmas were already in the pool** (8,196
  lemmas in 48 proofs; per-proof quartiles 52, 64 and 72%). The other
  ~4,300 are new and roughly double the pools for round 2.
* **Round 2** runs the 20 unsolved with the round-1 proofs added to the
  pools (4,109 and 3,494 hints): 900 abstract s, stall gap 60 s, CPU cap
  3,600 s, states kept for later rounds. Round 1 kept no states, so these
  are fresh runs.
  * **13 of the 20 solved (61 of 68 after two rounds).** By per-run
    limit: 7 by 60 abstract s, 9 by 120, 12 by 300, 13 by 600. Four
    took under 15k critical pairs, where round 1 failed at 230k–520k.
    All 7 unsolved hit the 3,600 s CPU cap, at only 222–445 abstract s,
    and 6 of them were still on hints at a 60 s gap. Their saved states
    take 0.3–1.1 GB each.
  * Both new inputs matter. With the new lemmas and no hints, goal_353
    and goal_354 fall in under 500 critical pairs; the big pool costs
    5k there. The others need the hints: goal_357 takes 9.1k without
    them against 6.2k, nil3_30__goal_381 51k against 14k, and goal_336
    and goal_284 fail at 60 s against 31k and 80k with hints.
  * Critical pairs get expensive on these problems. goal_336 without
    hints made only 270 critical pairs per CPU second (18.7k rules), so
    the abstract clock understates the real cost of long runs.
* **Round 3 (invalid, redone as round 4).** The 7 unsolved resumed their
  states with the round-2 proofs: +1 (nil3_30__goal_370). But the resumed
  aK2_eq_aK3_d runs matched only 1–9 hints, against about 1,260 in round
  2. Their problems had new lemmas, which hit the signature bug above
  (twee-e20 fixes it; a polluted state also resumes correctly). Five runs
  stopped exactly 120k critical pairs (the 60 s stall gap) after resuming.
  Round 4 repeats the round with e20 from the round-3 states.
* **Round 4 (round 3 redone with twee-e20): +2, 64 of 68.** The 6
  unsolved resumed their round-3 states with the same new lemmas and
  pools. Now the hints reach the saved search: each resumed run makes
  24–209 new hint matches (2 for goal_371), most within 10k critical
  pairs of the resume, as the new lemmas join. aK2_eq_aK3_d__goal_332
  is proved 24k critical pairs after the resume and nil3_30__goal_371
  after 4k (12 and 2 abstract s). Resuming costs CPU: the two proofs
  took 737 and 1,183 CPU s for those few critical pairs, so most of it
  goes to resuming itself. Measured on nil3_30__goal_355 (477 MB state,
  111k rules, 19.4M queued critical pairs, 3,787 hints, twee-e22
  `RESUMETIME`): loading takes about 130 s, normalising the hints 5 s,
  and re-scoring the saved queue against the new hints 333 s (each queued
  pair is rebuilt and rewritten). `--no-resume-requeue` skips the
  re-scoring; whether guidance suffers without it is not yet tested.
  Of the 4 unsolved, three stopped exactly 120k critical pairs after
  their last match (the 60 s stall gap), at +162k to +549k, and goal_360
  hit the CPU cap 93k after its last match.
  Hints from proofs of siblings keep feeding these runs, but each
  resume gives a short burst of matches, not a long hint-led run.

**Prover9 long runs (`long/P1`, `long/P0`).** fam2_long has 40 fam2
goals that the short loop left unsolved, run at 3000 given clauses.
Hints are all proof steps of the solved siblings (`p9_long.sh`).

* With hints 18, without 16 (both 13, hints only 5, no hints only 3), at
  the same CPU (9,560 vs 9,490 s). Proofs come late: median 997 givens
  with hints, 583 without. The short loop's 150–220 givens never get
  there.
* Prover9 picks hint matchers in bursts (`(H,` given clauses). Many
  solved runs have gaps of more than 750 givens without one, and a 750
  limit would keep 7 of the 18. The unsolved runs keep matching until
  late (last match at 2,047–2,949 givens). So for Prover9, "still on
  hints" does not separate the runs that will succeed from the rest.

## 2n. Prover9: SFDF reorientation of proofs

Veroff turns each proof into a strictly forward, demodulation-free
(SFDF) proof before using its steps as hints. `p9loop.py` now does this
without search:

* `--convert expand`: `prooftrans expand` writes each rewrite step as its
  own step, so the proof is demodulation-free.
* `--convert direct`: LADR's `directproof` gives a direct, forward,
  expanded proof.

Both are linear time: 9 ms per proof (279 proofs, 2.4 s in all). The
search-based conversion (rerun the problem with its own proof as hints
under `set(restrict_denials)` and no demodulation) converted only 2 of
34 proofs, at about 20 s each.

The loop runs on fam2 (aa1_15 and aK2_eq_aK3_q, 471 problems). Budgets
are in given clauses, so the runs are deterministic. Round 0 (150 givens,
no hints) solves 237 in every version.

| hints | hinted search | round 1 (150) | round 2 (150) | round 3 (220) | total |
|---|---|---|---|---|---|
| original proof steps | default | +26 | +9 | +11 | **283** |
| `prooftrans expand` (2.2× as many) | default | +26 | +9 | +7 | 279 |
| `directproof` (2.6× as many) | default | +26 | +9 | +7 | 279 |
| original proof steps | SFDF settings | +1 | +0 | +0 | 238 |
| `directproof` | SFDF settings | +3 | +0 | +0 | 240 |
| `directproof` | SFDF settings, 1500 givens | +3 | | | 240 |

* **In the default search the extra steps never match.** Round 1 is
  byte-identical in all three versions (same given counts on all 234
  problems). Prover9 matches hints against kept clauses, and with
  demodulation on only the normal form is kept. The intermediate
  equations that expansion adds never appear. In round 3, where the runs
  differ, the longer lists lose 4.
* **The SFDF search can match them, but it is far weaker here:** +3 even
  at 1500 givens (280 s per round, against 81 s for the default round 1).
* What Veroff gets from SFDF proofs our hints already have: only positive
  steps, nothing derived from the denial, skolems generalised. For twee
  this holds by construction (2j). For Prover9 the expanded proof only
  adds steps that the guided search never keeps.

## 2o. Online pools on the unsolved frontier

`sets/u3`: all 996 goals of three originals (R1dist_to_aa1,
aK2_eq_aK3_a, nil3_31) that the 4 s benchmark loop left unsolved (after
round 2 and the fam_long runs). Each run gets 20 abstract s, with rm4t,
3 nearest sibling lemmas and 10 subset-kNN lemmas, and twee-e19, on 5 cores
per variant.

* **Online pools** (`loop.py --online`). Each proof joins the hint pool
  and the sibling-lemma source as soon as it is found, for the runs not
  yet started. Goals run in goal-number order, and only `-j` runs are
  queued. Before this, the pools were fixed for the whole round.
* **Tiered pool** (`--pool tier:K:TOPN:F`). The kNN hints get the full
  boost, and the rest of the original's pool gets the weaker factor F.
  This was meant to avoid the cost of a big pool at short limits (2a).

On the first 189 aK2_eq_aK3_a goals, which every variant ran (all later
goals failed in every variant):

| variant | solved | wall s |
|---|---|---|
| kNN hints (30 neighbours, 100 hints), fixed pool | 44 | 10,744 |
| kNN hints, online | 55 | 9,422 |
| whole-original pool, online | 60 | 9,866 |
| tiered pool (kNN + rest at 0.3), online | 61 | 10,209 |

* **Online pools give +25% (44 to 55) at the same cost.** Proofs of
  earlier goals reach later goals within the round.
* **A whole-original pool adds about 10% more (60–61).** At 20 s, unlike
  2 s (2a), the big pool no longer hurts. The tiered pool is as good as
  the whole pool, but it needs the kNN index rebuilt as proofs arrive.
  So the full-benchmark run uses the whole pool.
* **Whole pool, online, all three originals:** 272 of the first 695 goals,
  against 0 for the 4 s loop.
* **The tail is hopeless at 20 s.** In goal order each original has a
  mixed zone, then only failures. The longest run of failures before a
  later success was 27 (R1dist_to_aa1); elsewhere 17–21. Replayed on the
  online runs, giving up an original after 30 consecutive failures keeps
  every proof and saves 15% (whole pool, cut short) to 50% (kNN variants)
  of the time. After 20 failures it loses 14 of 272. So
  `loop.py --give-up 30`.
* **Frequency-weighted boosts do not help.** A hint from 20 or more
  sibling proofs is right half the time, one from a single proof 0.8%
  (2m). Weaker boosts for rare hints (`--freq-factors 1:0.2,4:0.05`:
  factor 0.2 for hints from 1 proof, 0.05 for 2–4, 0.01 above) solve 60
  of the 189, the same as the uniform pool (+5/−5), in 19% more run time.
* **Hint signals at 5 s do not say which runs need 20 s.** Replayed on
  the whole-pool online runs: of the 517 runs unsolved at 5 s
  (10k critical pairs), 482 had matched a hint within the last 1 s, and
  18–20% of those were solved by 20 s. Runs with longer gaps did no
  worse or better (16% for 2–5k CPs). The number of late matches and
  the pool size do not separate them either (15–26% per quartile). So
  at short limits there is no Veroff stall rule to prune the next round,
  and the 20 s round reruns every unsolved goal (with the give-up rule).

**Full benchmark, Veroff style.** `abs/unleash.sh` runs every
goal the benchmark loop left unsolved: 18,064 of 51,784, starting from
its 33,720 proofs. The loop uses online whole-original pools, gives an
original up after 30 failures, and has rounds of 5 and then 20 abstract s
on 14 cores (twee-e20, kill after 15× the limit, CPU cap 400 s).

* **Round 1 (5 abstract s): +2,337, to 36,057 of 51,784** (holdout
  3,475 to 3,747 of 5,880). The give-up rule ran 10,079 of the 18,064
  goals and skipped the rest. All 129 originals gained (most:
  R1dist_to_aa1 +48, aK2eq_1234 +46). The round took 82 minutes on 14
  cores: 2.1 h of run time on proofs (median 2.4 s wall) and 16.8 h on
  failures (median 7.5 s wall).
* **Round 2 (20 abstract s): +2,951, to 39,008** (holdout 4,196, +449).
  The give-up rule ran 10,405 of the 15,727 unsolved goals. 125 of the
  129 originals gained; the most were R1dist_to_aa1 +113,
  mbol_aa1sqrd_to_aa1 +81 and nslm_to_aa1 +77. The round took 12 h on 14
  cores: 16 h of run time on proofs and 152 h on failures. At 20 abstract
  s a failing run takes about 53 s wall, because the CP rate falls on
  hard runs.
* Round 3 uses the cascade (2p) and runs from 06:03 on 14 Nov.

## 2p. One search for many goals, and the gap to the nearest proof

* **Multi-goal search** (twee-e21 `--multi-goal`, `loop.py --multi W`).
  All goals of an original have the same axioms, and twee's completion
  does not depend on the goal. So one search can serve several goals: the
  goals become skolemised negated conjectures of one problem, twee prints
  `SOLVEDGOAL` for each goal it proves and goes on until all are proved.
  A window of W consecutive unsolved goals gets the union of their lemmas
  and W times the budget.
* **It loses to separate runs.** On the 189 aK2_eq_aK3_a goals (20 s per
  goal, 100 s per window of 5): 21 against 28 for separate online runs on
  the first 33 goals (stopped there). On one window of 10 nil3_31 goals
  at 200 s: 4 against 5. A separate run for goal k+1 starts with goal k as
  an axiom, so its overlaps are among the first critical pairs. In the
  joint search goal k is only joinable. It never becomes a rule, so its
  consequences come late or never. Restarting with the new lemma is what
  makes the sibling chain work.
* **Success falls off with the distance to the nearest proof below.** In
  the full-benchmark round 2 (20 s, after failing at 5 s), by the gap in
  goal numbers to the nearest sibling proven before the run:

  | gap | runs | solved |
  |---|---|---|
  | 1 | 537 | 58% |
  | 2–3 | 176 | 42% |
  | 4–10 | 66 | 26% |
  | more than 10 | 5 | 0 |

  So the loop advances along each original's proof, and a hard goal
  blocks the goals after it. Conditional goals are not a weak spot: 83%
  of them are solved overall, against 68% of the unconditional ones.
* **Lemmas from both sides** (`loop.py --lemma-after`). The nearest
  proven siblings above a goal are lemmas too. They are proven before the
  run, so every proof still expands to one from the axioms. Test set: the
  222 goals of sets/u3 that the online whole-pool run left unsolved and
  that have a proven sibling at most 10 above (20 s, from that run's
  proofs). With lemmas from both sides 67 of 222 are solved. On a random
  74 of them: 26 against 20 for the same rerun with lemmas from below only
  (+6/−0). So most of the 67 come from rerunning with the full set of
  proofs below: with 3 originals on 5 cores, goal k+1 had often started
  before goal k was proved (the full benchmark interleaves 129 originals,
  so this rarely happens there). Lemmas from above add about 30% on top.
* **Cascade scheduling** (`loop.py --cascade T0,T1,...`), written from
  this. In place of rounds, a goal is retried at T0 as soon as a sibling
  at most `--retry-gap` places below it gets proved. Otherwise the goal
  right after a proof (`--frontier 1`) is deepened to the next budget
  level, resuming its saved state. A few workers stay free for the
  retries, so a new proof's consequences run at once.
* **The cascade wins.** The test set is sets/u3: 724 goals left unsolved
  after the online 20 s run, starting from its proofs (loops/U3poI). Both
  schedules get 5 workers for 2 h wall.
  * The cascade (20, 80 and 320 s levels; every goal near a proof first
    gets a 20 s run) proves **90** goals with 336 runs on 248 goals.
  * One online round at 80 s (give-up after 30 failures) proves **69**
    with 117 runs.
  * They share 58 proofs; the cascade alone has 32, the round alone 11.

  Proofs over time:

  | wall s | 600 | 1800 | 3600 | 5400 | 7200 |
  |---|---|---|---|---|---|
  | cascade | 27 | 57 | 64 | 77 | 90 |
  | 80 s round | 10 | 18 | 40 | 58 | 69 |

  The cascade is ahead from the start, and it was still gaining at the
  end (7 proofs in the last 10 min). Short runs on the goals right after
  new proofs pay off more than long runs in goal order. Only 30 of its
  336 runs reached the 80 s level, and 16 of those succeeded. Round 3 of
  the full benchmark therefore uses the cascade (abs/ul3.sh: 20, 80,
  320 and 960 s, with lemmas from above).

## 2q. Ablation: ENIGMA, hints and lemmas

The user asked how far the ENIGMA guidance gets, alone or with hints. The
test set is the 189 aK2_eq_aK3_a goals of sets/u3 (one hard original).
Each goal gets 20 abstract s, in an online loop that starts from the
proofs of loops/V2base and uses 5 workers. Only the guidance changes:

* **ENIGMA** is the rm4t rule filter: LightGBM with the theory block,
  threshold 0.1, penalty 2.
* **Hints** come from the whole-original pool, online.
* **Lemmas** are the 3 nearest proven siblings plus 10 subset-kNN lemmas.

| variant | ENIGMA | hints | lemmas | solved /189 | wall s, all 189 runs |
|---|---|---|---|---|---|
| full (U3po, run with the other two originals of sets/u3) | yes | yes | yes | **60** | 9,866 |
| full (U3xf, these 189 alone, like all rows below) | yes | yes | yes | 58 | 10,506 |
| U3xh | – | yes | yes | 59 | 14,979 |
| U3xm | yes | – | yes | 58 | 10,064 |
| U3xl | – | – | yes | 49 | 16,372 |
| U3yb | yes | yes | – | 49 | 11,805 |
| U3ym | yes | – | – | 42 | 10,501 |
| U3yh | – | yes | – | 37 | 15,063 |
| U3x0 (plain twee) | – | – | – | 28 | 18,151 |

The wall seconds are indicative only, because the machine was shared.
Every run had the same CP budget, so a lower total means that more runs
end early with a proof.

All nine runs together solve 70 goals; U3po misses 10 of them.

**Reading.**

* **Without lemmas, ENIGMA and hints add up.** ENIGMA alone gives +14,
  hints alone +9, and the two together +21 (28 → 49). ENIGMA plus hints
  solves every goal that hints alone solve, and 12 more.
* **ENIGMA is the stronger and cheaper guide.** Alone it beats hints
  alone (42 against 37) at about 70% of the wall time. Its failing runs
  do not pay for hint matching, and its proofs come earlier.
* **Lemma import is worth as much as ENIGMA and hints together**
  (49 = 49).
* **With lemmas, ENIGMA and hints overlap.** Each adds about 10 on top of
  lemmas, but together they add only 9–11: the full system on these 189
  goals alone (U3xf) solves 58, the same as ENIGMA plus lemmas. U3po (60)
  ran them interleaved with two other originals, so on 5 workers goal k+1
  less often started before goal k was proved. That ordering effect is
  as large as the second guide. Hints and lemmas carry the same
  information, the sibling proofs: hints as steps, lemmas as finished
  results. Once the lemmas are there, the hints mostly point to steps
  that are no longer needed. ENIGMA's knowledge is general, learned from
  other problems, so it adds most where sibling information is missing,
  and at less cost.
* The full system is the cheapest of all variants.
* The 10 goals that only some variant solves show the variance at 20 s.
  The search order changes with the guidance, so a cheap portfolio over
  variants could pick up a few of them. Earlier portfolio tests were
  within noise.

Earlier no-lemma data, on other sets, points the same way:

* Hard holdout 300 at 60 s: plain 44, rm4 53, rm4 plus lemmas plus kNN
  hints 56.
* ho3u: rm4 81, rm4t 87.

## 2r. How many sibling lemmas

Twenty abstract s per goal, online from loops/V2base, rm4t plus the
whole-original pool plus 10 subset-kNN lemmas. Only the number of
nearest proven siblings imported as axioms changes.

| siblings | aK2_eq_aK3_a, 189 goals | nil3_31, first 150 unsolved goals |
|---|---|---|
| 3 nearest below | 58 (U3xf) | 62 |
| **6 nearest below** | **64** (+8/−2) | **76** (+16/−2) |
| 10 nearest below | – | 74 |
| 6 nearest on either side (`--lemma-after`) | – | 76 |
| 3 below, 20 subset-kNN lemmas in place of 10 | 59 | – |

Six siblings beat three on both originals, by 10% and 23%, at less time.
Ten are no better than six. Lemmas from above do not change the result
here, where few goals above are proven. The retry test of 2p, where many
were, gave +6/−0. Extra subset-kNN lemmas add nothing.

The full loop's round 3 (cascade, 3 lemmas, from 06:03) found 738 proofs
in 2,481 first-level runs, bringing the total to 39,746. It was then
restarted at 08:35 as round 4, with 6 lemmas from either side
(abs/ul4.sh, `--cascade-start -1`): every unsolved goal near a proof
gets a 20 s run in its new context first.

Two cascade fixes went in with the restart:

* The lemma context is now the N nearest proven siblings on either side,
  the same ones lemma_problem picks.
* A retry starts fresh but saves its state, so a later deepening
  continues that search, not an older one.

**Retrained model rm6t:** rm4t's data plus the full loop's 5,303 proofs,
with the u3 originals held out. Alone (no hints, no lemmas, aK2 189) it
solves 40, against 42 for rm4t, so the new proofs do not improve the
filter. The full-system test is running.

**Which lemmas proofs use (14 Nov, twee-e31 `USEDAXIOMS`).** 60 goals the
full loop solved in round 4 were rerun at 20 s on a snapshot of all
40,961 proofs, offered the 20 nearest proven siblings plus 10 kNN lemmas.
All 60 were solved, each proof using 7.6 lemmas on average. A proof uses
about 20% of the siblings it is offered, almost regardless of distance:

| sibling | offered | used |
|---|---|---|
| before, 1–3 goals away | 120 | 30% |
| before, 4–6 | 132 | 27% |
| before, 7–10 | 173 | 17% |
| before, 11+ | 296 | 19% |
| after, 1–3 | 115 | 20% |
| after, 4–10 | 245 | 20% |
| after, 11+ | 119 | 16% |

All ten kNN ranks are used, 13–28 times each. Lemmas act as shortcuts to
whatever is available, not as a specific needed step. With 6 nearest
siblings instead of 20, on the same snapshot, 58 of the 60 are solved,
median 3.4 s against 2.7 s; 20 lemmas give fewer rules in only 18 of 58.
The large difference is with the original round-4 runs (median 9.7 s):
the same goals are about 3× faster now because more of their neighbours
are proven. More lemmas at a time add little (as with 10 against 6
above); a richer context does, which is what the cascade's retries on
new nearby proofs exploit.

## 2s. Frequent hints as axioms: no gain, and false hints in old pools

`loop.py --hint-axioms K:F` adds the K most frequent pool hints that
occur in at least F sibling proofs to the problem as axioms. Pool hints
are consequences of the axioms and proven lemmas, so the proofs stay
sound.

Test set: nil3_31, 150 goals, at 20 s, on top of 6 lemmas (baseline
76).

| hint axioms | solved |
|---|---|
| none | 76 |
| 10, each from at least 20 proofs | 72 (+1/−5) |
| 45, each from at least 10 proofs, all verified as theorems | 73 (+3/−6) |

The high-precision hints are more useful as hints. As axioms they add
critical pairs from the start and crowd the search.

**False hints in the pools.** The first 45-axiom run solved all 150 goals
in 28 s. One of its "hints" was `X0 = X1`, which occurs in 1,422 proof
hint files of loops/V2base (and so of loops/UL). They are proofs of
conditional goals such as `X0 = X1 ⇒ …`, made before the HINTS-HYP fix
(twee-e14, 2j). There, the hypothesis with its skolems generalised was
logged as a hint.

As a hint this was harmless. Twee matches hints by variant (canonical
form), not by instance, so `X0 = X1` only matches the critical pair
`X = Y`. The other false generalised hypotheses are wasted hint entries
in the same way.

As an axiom it is unsound, so `--hint-axioms` now counts only proofs of
unconditional goals. The 45 top nil3_31 hints from those all prove from
the axioms in under 10 s each.

## 2t. Where twee's time goes, and the rule penalty

**Profile.** twee-e22 built with `-f profile` (Twee.Profile now uses GHC's
monotonic clock instead of rdtsc). The test run is one failing
nil3_1K goal at 20 abstract s (40k critical pairs considered) in the full
configuration. Its share of the time, excluding the profiler's own
overhead:

| phase | share |
|---|---|
| making critical pairs (6,115 new rules against the active set) | 51% |
| … of which normalising both sides of each new pair (8.2M `simplify` calls) | 41% |
| considering the 27k dequeued pairs (normalisation, joining) | 22% |
| the rest | 27% |

Without hints or the model, the same run takes 67 s against 49–53 s. The
model keeps fewer rules, which saves more than it costs. Hint matching
and logging the given rules cost about 8%. Ground joining is cheap here:
limiting it changes nothing.

So the cost per abstract second grows with the square of the number of
rules. Twee normalises every new critical pair at creation, by design,
and changing that would be a large redesign.

**Rule penalty.** Larger deferral penalties would keep low-scored rules
out longer and make the rule set smaller. On nil3_31, 150 goals at 20 s
with 6 lemmas: penalty 2 solves 76, 5 solves 77 and 20 solves 75. Wall
time does not change. Penalty 2 stays.

## 2u. ENIGMA-style looping and a Deepire-style model (user's question, 14 Nov)

**Offline, in the loop setting.** The test set is the 298 proofs of
nil3_31, aK2_eq_aK3_a and R1dist_to_aa1 goals that the full loop found
in rounds 1–4. These are later goals of originals whose earlier goals
are solved. Training gets every other given log, including the other
proofs of the same originals, as an ENIGMA loop would. Mean per-problem
AUC on the proofs' rules:

| model | AUC |
|---|---|
| rm4t (base data: train_only + tr30_g1) | 0.850 |
| **rm7t: LightGBM retrained with the loop's proofs** (negmax 150, 34 GB, 24 min) | **0.882** |
| Deepire-style, derivation only (`deepire.py`, d = 32, 4 epochs, 2 min) | 0.765 |
| rank fusion rm4t + 0.5 × Deepire | 0.861 |

* **Retraining on the loop's own proofs helps offline:** +0.03 AUC on
  later goals of the same originals. rm6t gained nothing (2r), but it
  held these originals out of training entirely.
* **Deepire-style embeddings** (axiom equations as learned leaves; a rule's
  embedding computed from its two parents) are weaker than the ENIGMA
  term features. They are somewhat complementary: fusion adds +0.011.
  Only 6,746 training logs have parent columns; the older train_only
  logs do not.
* **Hybrid neural model** (`deepire.py --feats --goal`): the derivation
  embedding plus hashed bags of the rule's and the goal's ENIGMA
  features, trained on 2,500 problems for 6 epochs. AUC 0.814, still
  rising, against 0.885 for rm7t on the same test. Rank fusion with rm7t
  adds nothing (0.885 at weight 0.1, lower above). At this data size,
  LightGBM on ENIGMA features stays the better model, and the
  derivation history adds no usable signal on top of the retrained
  model.
* **The online ENIGMA loop** (`loop.py --rerun-solved`, abs/el.sh) is
  running on all 1,934 goals of these 3 originals at 5 abstract s, without
  lemmas. Each round retrains on base data plus the loop's shortest proof
  per problem, then reruns every goal. Round 0, with a base-trained model
  like rm4t, solves 920. Round 1, retrained with those proofs, solves 936
  of them on its own (+21 new, −5 lost), bringing the total to 941.

| loop on sets/e3 (1,934 goals), 5 abstract s, no lemmas | round 0 | +round 1 | +round 2 | +round 3 | CPU (wall-sum, rounds 0–2) |
|---|---|---|---|---|---|
| EL: rule model retrained each round, no hints, reruns all | 920 | 941 | 943 | 947 | 6.1 h |
| HL: hints from the loop's proofs, no model | 905 | 944 | 951 | 953 | 7.9 h |
| EHL: both (retrained model + hints), reruns all | 920 | 963 | **971** | (stopped) | 6.5 h |
| FHL: hints + EHL's round-0 model kept fixed (production setting) | 920 | 970 | **987** | (not run) | 6.2 h |

* The ENIGMA loop alone gains little after its first retraining (+21,
  then +2 and +4); the hint loop gains more (+39, +7, +2).
* The combination solves 971 after two rounds, as many as EL and HL
  together (973), with 11 that neither solves, and at less CPU than the
  hint loop (the model makes runs cheaper).
* **Retraining adds nothing online; it loses.** With the round-0 model
  kept fixed and only the unsolved goals rerun, round 1 solves 970 and
  round 2 987, against 963 and 971 with retraining (after round 2: 19
  only in FHL, 3 only in EHL), at 4.40 h of CPU for rounds 1–2 against
  4.79 h. The gain over HL comes from having a model at all, not from
  training it on the loop's proofs. The same was seen with rm6t and rm7t
  (2r), so the full loop keeps the fixed rm4t.

## 2v. Long runs slow down: overlap index and interreduction filter (user's question, 14 Nov)

**How much slower.** `twee --progress N` (twee-e23) prints a PROGRESS line
every N abstract seconds. Each line gives critical pairs, rules, active
rules, queue size and CPU, plus the CPU of the housekeeping tasks. The
test is the profiled nil3_1K goal in the full configuration (rm4t, 2,743
hints), run for 640 abstract s, on the loaded machine (load 35–40 on 112
cores). The nominal rate is 2,000 critical pairs per abstract second.

| abstract s | rules | queued pairs | CPU per abstract s (old twee) | of which interreduction | of which queue renormalisation |
|---|---|---|---|---|---|
| 0–10 | 3.7k | 0.3M | 3.0 s | 0.2 s | 0.5 s |
| 20–30 | 8.2k | 1.4M | 8.4 s | 0.7 s | 2.9 s (one pass) |
| 50–70 | 14k | 4.3M | 6.8 s | 1.2 s | 0 |
| 120–130 | 20k | 6.9M | 26 s | 2.0 s | 17.7 s (one pass, 177 s) |
| 170–190 | 26k | 11.5M | 8.6 s | 2.3 s | 0 |

So a long run costs 3–9 s of CPU per abstract second, against 1–3 s at the
start. On top of that come queue renormalisation passes that each cost
about 25 µs per queued pair. Under the abstract clock two housekeeping
tasks were free and so ran without limit. Interreduction ran every
abstract second over all active rules. The queue was renormalised
whenever the critical-pair sample went stale. Together they took 33% of
the CPU by 130 abstract s; with CPU time, twee caps each at 5%. At 20
abstract s, the wall time of the full loop's runs grows with the rule
count, from 52 s per run (2–4k rules) to 104 s (12–14k rules).

**Profile at 60 abstract s** (12.9k rules): trying overlaps 18%, index
lookups 18%, building terms 15%, `simplify` 13% (profiler overhead
excluded). Twee looked for overlap partners by trying every active
rule at every position, so each new rule cost time linear in the active
set, before any critical pair was normalised.

**What the Prover9 branches suggest, and what was done.** The
Prover9-new long-run work is mostly about memory (compact clause and
passive stores, mmap ancestor stores, about 80% less RAM) and fast
matching against 10^5 hints. Twee's runs do not need either: 0.4 GB at
60 abstract s, and hint matching is a hash lookup. Two indexing ideas do
carry over:

1. **Index the partners for inference** (Prover9's paramodulation
   indexes; here Schulz's fingerprint indexing). twee-e24,
   `Twee/FPIndex.hs`, samples 8 positions of each term. It keeps two
   tries, one of rule left-hand sides and one of the subterms at every
   overlap position. The candidates are sorted back into the old loop
   order, and the renaming bound comes from a multiset of per-rule
   variable bounds instead of a scan over all rules. **The output is
   byte-identical** (given lists and proofs on 6 solved problems, all
   counts on a 30k-pair guided run, and a resumed state).
   `--no-overlap-index` turns it off.
2. **Backward demodulation for interreduction** (Prover9's back-demod
   index). twee-e26 re-checks an old active only if a rule added since
   the last interreduction matches one of its subterms. This is nearly
   exact: `TWEE_DEBUG_FILTER=1` found two misses in a 6k-pair run (a
   ground-joinability and a model change). 4 of 6 test problems stay
   byte-identical; the other two differ by 1 rule in about 3,000.
   `--no-interreduce-filter` turns it off.

| long guided run, CPU | 30 abs s | 70 abs s | 150 abs s |
|---|---|---|---|
| old (e23) | 150 s | 411 s | 1,148 s |
| new (e26) | 87 s | 232 s | 623 s |
| speedup | 1.7× | 1.8× | 1.8× |
| interreduction CPU, old → new | 14 → 4 s | 59 → 10 s | 201 → 24 s |

Continued to 360 abstract s (22.7M queued pairs, 1.4 GB), the new twee
settles at 3.2–3.5 s of CPU per abstract second between 120 and 360 s,
with no further growth. The old run reached 1,837 s of CPU by 230
abstract s; the new one used 911 s there (2.0×). The queue renormalisation passes
(126 s at 80 abstract s, 282 s at 240 abstract s) add about 25% on top.

Six solved problems at up to 60 abstract s: 1.05–2.6× less CPU. Real
workload (sets/u3n150, 20 abstract s, online, 6 lemmas; N3l6 with e22
solved 76): on the first 97 goals e27 solves 69 against 68, in 18% less
wall time, on a busier machine.

The state file format is unchanged; the index is rebuilt on load. Since
13:39 the path `/project/bin/twee-e22` holds the e27 code (the original is
`twee-e22.orig`). The running full-loop cascade and the HL/EHL runs
therefore use it, and the deep cascade levels get the speedup.

**Queue renormalisation** is the remaining long-run cost. One pass
renormalises every queued pair from scratch: twee stores only the
parents and position, so there is no normal form to filter. That makes
it as costly as making all those pairs again. `--queue-cost K` (e27)
charges a pass K critical pairs per queued pair, so that its 5% budget
binds as it does in CPU-time mode. An honest K is about 0.008. Whether
renormalising less often hurts hint guidance (queued pairs can become
hint matches) needs a deep-run test; the default stays 0.

Also tried, no gain: larger GHC allocation areas (`-A16m`/`-A64m` were
slower), and skipping the copy that `simplify` builds of normal forms
together with a lazy overlap top term (exact, but within the ±15% timing
noise of the loaded machine).

## 2w. Veroff's P9loop and Bigloop in twee (user's question, 14 Nov)

**What Veroff does** (AITP 2026 slides). A P9loop reruns the *target*
theorem over and over. At the end of each failed run, every derived
clause that matches a hint (a *hint matcher*) is kept, and all later runs
get these as extra input lemmas. The runs cycle through settings,
mainly term orderings: 36 per P9loop in the NIL3 proof. A Bigloop runs
several P9loops at once, all sharing one lemma pool. In the NIL3 proof,
1,155 of 3,594 steps were Bigloop lemmas, and 25 of 60 output files
contributed.

**In twee.**

* `--print-hint-matchers` (twee-e30) prints every rule that matches a hint
  as a TPTP formula (`HINTMATCHER n fof(...)`).
* `loop.py --p9loop` keeps a goal's matchers in `DIR/p9lem/<goal>` and adds
  them as axioms to its later runs. They are consequences of the problem's
  axioms and lemmas, so they are sound; matchers with a skolem of a
  conditional goal are dropped. `--p9-max N` keeps only the most recent N.
* `--p9-orders N` gives attempt k its own KBO precedence (`--precedence`, a
  seeded shuffle of the problem's symbols; attempt 1 = twee's default).
  Hint matching is by variant in either orientation, so hints and matchers
  carry over between orderings.
* `--p9-parallel P` is Bigloop: P runs of each goal per round at once, each
  with its own ordering, all adding to the one lemma pool.

**Test 1: the 73 nil3_31 goals the 20 s system left unsolved** (sets/u3n73,
from all of N3x6's proofs, production config, 4 rounds of 20 abstract s):

| arm | solved after rounds 1 / 2 / 3 / 4 | wall per goal and round |
|---|---|---|
| P9loop, matcher lemmas only | 1 / 3 / 3 / 3 | 39–43 s |
| P9loop, lemmas + a new ordering each round | 1 / 1 / 2 / 2 | 40–57 s |
| resume (continue the saved run) | 1 / 3 / stopped | 55 s, then 115 s |

The resume arm was stopped after round 2 to stay within the CPU budget.
Its round 2 took 4,418 s of wall time with 2 workers, against 1,413 s
for the lemmas-only arm.

* All arms solve the same goals (400, 323, 341); these goals are hard
  and four 20 s rounds add only 2.
* After round 2, the matcher lemmas reach the same hint coverage as
  resuming: 2,220 of 3,728 hints joined and 1,508 live, against 2,214 and
  1,514. They do it in half the wall time, because a fresh run on a small
  state is cheaper per critical pair than continuing a big one. A resume
  also re-scores the whole saved queue first, which costs 20–55 s here.
* Lemmas pile up: about 880 per goal after round 1 and 1,440 after round
  2. New matchers then dry up (about 115 per run in round 3). Each run
  matches fewer hints itself (945 in round 1, about 730 later), because
  many hints are already joinable from the lemmas.
* Different orderings derive largely different matchers. In a 1 s smoke
  test of one goal, the default ordering found 204 and another found 528.

**Test 2: the cascade's frontier** (sets/fr100: 100 goals the full loop
left unsolved at 20 s whose nearest lower sibling is proven; every arm
starts from the full loop's 40,961 proofs, production config, 2 workers
each):

| arm | solved after rounds 1 / 2 / 3 / 4 | wall (sum over runs) |
|---|---|---|
| resume, saved queue re-scored (BRS) | 9 / 17 / 23 / 26 | 5.3 h for 3, 7.8 h for 4 |
| resume, queue kept as saved (BRSn, `--no-resume-requeue`) | 9 / 18 / 27 / 29 | 4.1 h for 3, 5.3 h for 4 |
| P9loop, matcher lemmas + a new ordering each round (BP9) | 9 / 16 / 18 / 18 | 4.1 h |
| Bigloop, 2 orderings per goal and round (BBL) | 14 / 19 | 4.2 h |

All four arms solved 33 goals together. Four of them only BRSn solved;
BP9 and BBL each solved one goal no other arm did; BRS solved none on
its own.

* **Keep searching, do not restart.** On goals right next to a proof,
  continuing the saved search beats restarting with matcher lemmas: 27
  against 18 at the same 4.1 h. The P9 arm stalls after round 2 (BP9 adds
  nothing in round 4), as in test 1.
* **Skip the re-scoring.** Re-scoring the saved queue against the new hints
  costs 20–55 s per resume and buys nothing: after four rounds BRS
  solves 26 in 7.8 h, BRSn 29 in 5.3 h. The full loop now resumes with
  `--no-resume-requeue` (round 5 continued at 19:35).
* **Orderings do add something.** In BBL's round 1, a second ordering per
  goal solves 14 against 9 for one run, but at twice the wall time. At
  equal time, resume is still ahead (18 at 2.9 h against 14 at 2.6 h).
  Orderings are a candidate for goals whose resume has stalled, not a
  replacement for it.

## 2x. A resume bug that grew one run to 100 GB (14 Nov)

A resumed run of the full loop grew to 100 GB before the user killed it.

**The cause.** Twee numbers its symbols when it interns them, and it
numbers them afresh when it loads a saved state. The saved state also
holds the hint matcher's tables of goal constants, and these are keyed by
the *old* numbers. Resume added the new axioms (lemmas proven since the
save) while those stale tables were still in place, and only then put in
the current run's tables. With the stale tables, a goal constant could
look up a definition that contains itself. Scoring one critical pair
(hint lookup after expanding goal constants) then never stopped.

**The fix** (17ffcd3).

* The current run's hint tables go in, normalised, before the new axioms
  are added.
* Goal-constant definitions whose expansion is cyclic or longer than 1,000
  symbols are dropped from hint matching.
* twee is built with a default heap limit (`-with-rtsopts=-M6g`, 110d93a).
  A run that would grow past 6 GB stops with "Heap exhausted" (exit 251).
  `loop.py` then marks the run HEAP and deletes its saved state.
* A watchdog (`abs/memwatch.py 7 45`) kills any twee over 7 GB and, while
  all twee processes together use more than 45 GB, the largest one.

**Check.** The saved state plus one lemma used to exhaust any heap; it
now proves its goal in 1.9 s at 190 MB. Fresh and resumed hinted runs on
six current goals do the same work as before, counted in critical pairs.

## 2y. Consider-emulation costs a quarter of the CPU (14 Nov)

**Profile.** Twee's stamp profiler (`twee-e32prof`) on one failing
nil3_15 goal, 30 abstract s, production config (3,088 hints). It made 16.4M
`simplify` calls and 202M index lookups. Without consider-emulation
(`--no-eqhint-consider`, 1b) it makes 10.9M calls and the total time drops
by 16%, profiler overhead included. With today's large pools, many critical
pairs have the symbol fingerprint of some hint form, and each of them goes
through `allSteps`.

| consider-emulation | CPU (nil3_15 / lra2aa, 30 abstract s) | hints matched |
|---|---|---|
| on, all hints (default) | 67.9 s / 57.6 s | 973 / 1,608 |
| only for hints no rule has matched yet (`--eqhint-consider-open`, new) | 48.0 s / 50.7 s | 971 / 1,608 |
| off | 46.4 s / 46.4 s | 981 / 1,602 |

With `--eqhint-debug`, it adds 8 and 20 distinct hints over 8,811 and
26,697 plain matches.

**Solving** (sets/u3n150, 20 s, 6 lemmas, online, as N3x6):

| arm | solved | wall (sum over runs) |
|---|---|---|
| on (N3x6) | 77 | 4,405 s (another time, other load) |
| off (N3c) | 76 | 3,023 s |
| open hints only (N3o) | 74 | 3,504 s |

The three arms solve 79 goals between them. Most differences come from
sibling lemmas. For example, N3c and N3o prove goal 341, and its lemma then
gives goal 400 a 4 s proof. Only about three goals differ directly, which
is within noise. On the goals all three solve, the median wall time is
6.1, 4.2 and 4.7 s.

**Decision.** The full loop runs with `--no-eqhint-consider` from 20:15
(round 5 continued). This buys about 30% more runs per hour, at the cost
of at most a few goals per hundred. Rewriting `simplifyOutermost` so that
it does not rebuild unchanged terms was 0–5% slower and was reverted.

## 2z. Distance in proof lines, not goal numbers (user's remark, 14 Nov)

A goal's name gives its position among the goals selected from the
original's Prover9 proof. Its LADR file also gives the proof line
(`% goal_313 line_1531`). The original proofs themselves are not in
AIM60k or Prover9-new, so the parents of a step are unknown. Goals were
picked in stripes 3, 5, 8, 13, 21, 34 and 55 lines apart. A gap of one
goal is therefore anywhere from 3 to 55 proof lines.

The table replays the full loop's round 5 in order and measures each run's
distance to the nearest proven goal below it at the time of the run. Line
distance predicts success much better than the goal-index gap the cascade
used:

| distance to nearest proven goal below | L0 retries (20 s) | L1 (resume to 80 s) |
|---|---|---|
| ≤ 8 lines | 9/29 (31%) | 36/100 (36%) |
| 9–13 lines | 69/216 (32%) | 125/495 (25%) |
| 14–21 lines | 36/172 (21%) | 47/296 (16%) |
| 22–34 lines | 29/219 (13%) | 37/155 (24%) |
| 35–144 lines | 41/356 (12%) | 11/75 (15%) |
| index gap 1 / 2 / 3 | 22% / 12% / 14% | 23% / 17% / 40% (5 runs) |

`loop.py --line-gaps R,F` (6b76a1b) orders the cascade's retries and
deepening by proof-line distance. It also admits goals within R lines for
retries and within F lines for deepening. Every gap-1 goal still deepens:
the late goals, 55 lines apart, block the rest of their chains. The full
loop runs with `--line-gaps 21,13` from 20:58. Admission barely changes
(1,407 goals against 1,406 deepen, because the dense early parts are
solved). The gain is in the order: near goals (36%) run before far ones
(12%).

The full loop's rate (round 5, about 16 workers): 129 proofs/h with
re-scoring off (19:35–20:13), and 203/h with consider-emulation also off
(20:15–20:57).

## 2aa. Stalled goals: run fresh with the new hints, do not resume (14 Nov)

The test set is sets/sg1: 32 gap-1 goals that failed L1 (resume to 80
abstract s) in the full loop's round 5. All arms run from the snapshot
loops/ULsJ (41,473 proofs) in the production config.

| arm | solved | proofs per CPU-hour |
|---|---|---|
| resume to 320 s (+240), as the cascade's L2 (SG1) | 0 of 13 run (stopped) | 0 |
| fresh 80 s, another term ordering (SO) | 8 / 32 | 5.9 |
| fresh 80 s, default ordering (SD) | 4 of 11 run so far | 12 |
| fresh 20 s, default ordering (S20) | 4 / 32 | 14 |
| for comparison: gap-2 goals, L0 state resumed to 80 s (SG2) | 5 / 48 | 2.8 |

None of these goals had a new sibling lemma since its last fresh run, so
the cascade never retried them. Their hint pools had grown, though, by up
to 75%. Success follows that growth:

| pool growth since the last fresh run | S20 | SO |
|---|---|---|
| < 10% | 0/12 | 1/10 |
| 10–25% | 1/11 | 3/13 |
| ≥ 25% | 3/9 | 4/9 |

* **Resuming does not use new hints.** The saved queue was scored without
  them. `--no-resume-requeue` saves the re-scoring (2w), so a resumed run
  only sees the new hints in the critical pairs it creates later.
* **The ordering is not the main effect.** SD solves as well as SO, at an
  equal or better rate.
* **`loop.py --retry-hints G`** (4a34404) also retries a goal, fresh at
  T0, when its original's hint pool has grown by the factor G since its
  last fresh run. On a restart, the growth is read from the `hints=` of
  each goal's last fresh run in the round results. Such goals are retried
  instead of deepened. The full loop runs with `--retry-hints 1.25` from
  22:28. 1,633 unsolved goals qualify, most of them far from a proof.

## 2ab. Sketch climbing (user's suggestion, 14 Nov)

The idea: make a hard goal easy with extra assumptions, then climb the
lattice of assumption sets down to the empty set. Hints from every solved
sketch guide the next ones. The earlier test (2g, sketches) used one
fixed set of assumed siblings below the goal and gained nothing. For a
gap-1 goal, every sibling below it is already proven, so that version
assumed nothing new.

`climb.py` (1e46a74) implements the climb on top of `loop.py`'s
production context: lemmas, kNN lemmas, hint pools and the rule model.

* **Candidate assumptions:** the M nearest unproven siblings of the target,
  by proof line, on either side. They are lines of the same Prover9 proof,
  so they are true.
* **Each sketch run:** the target with an assumption set S as extra axioms.
  twee reports the axioms the proof used (USEDAXIOMS), giving the used
  set U. The proof's steps become sketch hints of the original, shared by
  all its targets and placed before the pool hints. The sets U − {u} are
  queued next, smallest first.
* **End of the climb:** a proof that uses no assumption is a real proof.
  Otherwise the climb ends with a real run that has all the sketch hints.
  If even the full set S fails, its time is doubled.

**First test (CL1, siblings only):** sets/sg1, M = 8, up to 6 sketch runs
of 5 s, then a real run of 20 s. The comparison is S20. CL1 was stopped
after 7 goals and 982 s on 2 threads.

* It found 1 real proof (c_344). S20 solves that goal too.
* There were sketch proofs for 5 of the 7 goals. Often one sibling is
  enough: j_294 follows from goal_292 in 2 s, j_363 from goal_367, c_369
  from goal_353. The 20 s real runs still failed. The steps from the
  sibling to the target are the easy part, and the hints cover only that
  part. The hard part is the sibling itself, which is stalled as well.
* When no sibling set helped, the budget doubling cost a lot: b_364
  reached 547 s in a single run. The doubled budget is now capped at
  4 × the sketch time.

**Laws (user's remark, "frequent extra axioms like commutativity").**
`--laws` adds Veroff-style simplifying laws over the axioms' signature.
They may be false.

* Commutativity of each binary operation.
* Associativity of each binary operation that no axiom defines.
* Each defined operation (an axiom f(X1..Xn) = s) equal to a constant or
  to its first argument.

A law with which twee proves X = Y in 2 s collapses the theory and is
dropped. For the AIM signature, 6 of 18 collapse: t = e, l = e, r = e,
a = x, k = x and comm(t). `--freq K` adds the K most frequent equations of
the original's unconditional proofs. These are true.

The laws make every sketch trivial. A single law, such as l(X,Y,Z) = X or
comm(ld), proves the target in 0.3 s with a dozen hints, and the climb
never reaches the empty set. **The descent alone gives few, short hints.**

**Gap filling (Veroff 2001, "proof sketches").** Veroff does not stop at a
sketch proof. The steps of the sketch that use the extra assumption become
targets of their own. twee-e37's `--print-hints` lists the lemmas that
depend, transitively, on axioms named `assume_*` (HINTS-ASSUMED).
`climb.py --fill S` (b506481) works as follows:

* After each sketch proof, one `--multi-goal` run of S s tries to prove
  those lemmas without the assumptions.
* It uses the true lemmas so far and the sketch hints.
* The proven lemmas become axioms `true_i` of all later runs on the
  original's goals.
* A final proof that uses true lemmas is a chain of real proofs. It is
  also tried once without them.

In the smoke test (b_364), the sketch proofs had 7–27 dependent lemmas.
Each 3 s check proved 0–7 of them, giving 18 true lemmas after 8 sketches.
The 10 s real run still failed.

`--knn K` adds true assumptions: the K unproven goals of other originals
most similar to the target, from problems whose axioms are a subset of
the target's. These are lines of Prover9 proofs, so every lemma that
depends on them is true too.

**Results on sets/sg1** (32 stalled goals; up to 12 sketch runs of 5 s,
then 20 s real; CPU s = the sum of run times, fill runs included):

| arm | solved | CPU s | proofs per CPU-hour |
|---|---|---|---|
| fresh 20 s (S20) | 4 | ~1,000 | 14 |
| fresh 80 s (SD, stopped at 23 goals) | 7 | 3,158 | 8.0 |
| fresh 80 s, ordering 1 (SO) | 8 | 5,898 | 4.9 |
| CL2: siblings + laws + freq, no fill | 4 | 1,458 | 9.9 |
| CL3: CL2 + fill 3 s | 5 | 3,013 | 6.0 |
| CL4: siblings + kNN (true only) + fill 3 s | 6 | 3,618 | 6.0 |

* **CL2 adds nothing.** It solves exactly the S20 four.
* **Gap filling finds a goal no fresh run solved.** That goal is
  mbol_lem1_393, in both CL3 and CL4. CL3's 302 checks proved 369 of
  3,377 dependent lemmas; CL4's 150 checks proved 220 of 1,975.
* **3 of CL4's 6 are chain proofs.** These are t_358, 1243_332 and
  mbol_393. They use 1–4 true lemmas, and one run without the lemmas
  fails at 20 s. With laws, the final proof was always also found
  without them, in 2–10 s; the sketch and fill hints alone carry it.
* **Fresh 80 s solves goals no climb did.** j_294 and t_283 fall to fresh
  80 s runs only. The union of all arms is 9 of 32.
* **The climb is not cheaper than fresh 80 s, but it reaches other
  goals.** In CL4, failing sketches cost 1,257 s, failing final runs
  866 s, fills 677 s and successful sketches 574 s.

**Larger test: sets/sg3.** These are 64 goals of the current loop that
failed L1 (snapshot loops/ULsK, 41,996 proofs).

* CL5, the CL4 config, solved 10/64 in 6,817 CPU s: **5.3 proofs per
  CPU-hour**.
* F3, fresh 80 s, solved 12/64 in 9,919 s: 4.4 per CPU-hour.
* **CL5's 10 are a subset of F3's 12.** On sg3 the climb is only cheaper
  per proof; it reaches no goal that fresh 80 s misses.
* Fresh 20 s was the cheapest arm on sg1 (14 per CPU-hour), and the
  climb ends with a fresh 20 s run. So the right control for the climb
  is fresh 20 s in the same context.

**The loop's own deepening is worse.** After the restart at 23:56, UL10's
runs gave these yields:

| level | runs | proofs | average run | proofs per CPU-hour |
|---|---|---|---|---|
| L0, fresh 20 s | 72 | 8 | 33 s | 12 |
| L1, resume to 80 s | 53 | 17 | 113 s | 10 |
| L2, resume to 320 s | 71 | 21 | 420 s | 2.5 |

L2 took 78% of the CPU. L2 and the climb work on the same goals, those
that failed L1, and the climb yields twice as much per CPU-hour.

**Deployed (15 Nov 00:43).**

* UL11 (`abs/ul11.sh`) runs only L0 and L1 (`--cascade 20,80`) on 12
  workers, with `--sync 60`.
* `climb.py --live loops/UL` (`abs/clive.sh`, 6 workers, 8 once F3 ends)
  takes UL's goals whose last result is a failed L1+ run, nearest proven
  goal below first. Each real proof goes into UL: first the hints file,
  then a solved.tsv row.
* `loop.py --sync S` reads the appended rows every S s and treats them as
  its own proofs: pools, lemmas, and retries of the neighbours. A synced
  cascade with nothing to run waits for such proofs instead of ending
  its round.
* `merge.py` merged the 5 earlier probe proofs (S20, SD, SO, CL3) into UL.

**Control: fresh 20 s beats the live climber on its own targets (01:28).**
The climber's first 102 targets were rerun fresh at 20 s, as UL's L0
(FV). The context was a UL snapshot without the climber's proofs,
loops/ULsL.

| arm | solved | CPU s | proofs per CPU-hour |
|---|---|---|---|
| live climber (CLV) | 29–31 | 7,657 | 15 |
| fresh 20 s (FV) | 36 | 2,861 | 45 |

27 goals were solved by both, 2 by the climber only and 9 by FV only.
The snapshot is 20 minutes newer and includes UL proofs the climber
helped produce, but that cannot explain a 3× gap.

**The cause is in the loop, not the climb.** Round 5 started with
`--cascade-start 0`, which marks every goal as freshly tried. 63 of the
97 targets had no fresh run in round 5 at all; they only resumed states
saved in earlier rounds and contexts. Fresh 20 s proved 28 of those 63
and 8 of the other 34, whatever their pool growth.

The same holds for the sg3 test: CL5's proofs were a subset of fresh
80 s. The climb's apparent advantage was mostly its final fresh run.

**Changes (d2625d2).**

* `loop.py --fresh-first`: with `--cascade-continue`, goals without a
  fresh run in the round get a T0 run first. 8,634 goals qualify; the
  retry gap rules and the line-distance order still apply.
* UL12 (`abs/ul12.sh`) runs it on 16 workers and made 18 new proofs in
  its first 108 s.
* The climber is now a filler (`--cpus 20`, up to 8). It takes only
  goals whose fresh run in the latest round failed as well.

**Fresh runs far from a proof beat resumes near one (UL13, 03:28).**
UL13 ran 2,600 runs in 115 minutes and made 465 new proofs; the climber
added 27. Afterwards I replayed its rows in order. Each run was binned by
its goal's distance, in proof lines, to the nearest goal proven below it
at the time. The proofs-per-1,000 s column uses wall seconds per run.

| level | proof lines | runs | proved | rate | proofs per 1,000 s |
|---|---|---|---|---|---|
| L0 (fresh 20 s) | 0–13 | 613 | 159 | 26% | 8.0 |
| L0 | 14–21 | 491 | 75 | 15% | 4.4 |
| L0 | 22–40 | 515 | 99 | 19% | 5.7 |
| L0 | 41–80 | 527 | 85 | 16% | 4.6 |
| L0 | 81+ | 157 | 6 | 4% | 1.0 |
| L1 (resume to 80 s) | 0–13 | 227 | 36 | 16% | 1.2 |
| L1 | 14–21 | 120 | 21 | 18% | 1.4 |

Fresh runs up to 80 lines away are 3–4× as productive per second as the
resumes. However, with `--line-gaps 21,13` the goals beyond 21 lines came
only from `--far-retry`, after every L1 run. UL14 (`abs/ul14.sh`) uses
`--line-gaps 80,13`, so they now come before the resumes. 7,256 goals
still had no fresh run in round 5.

## 2ac. A learned scheduler for the cascade (15 Nov)

UL14 (`--line-gaps 80,13`) made 258 new proofs in its first 25
minutes, about 610 an hour, against UL13's 243 an hour. Moving the fresh
runs up to 80 lines away ahead of the resumes was worth about 2.5×
(2ab).

The next question was which goals to run fresh first. The loop has run
16,000 fresh runs in rounds 3–5. `schedfeats.py` replays them in order
and records each run's features as they were when it started:

* distances in proof lines to the nearest proven goal below and above;
* failed runs so far, and failed fresh runs with the same nearest proven
  goal below (`nfail_ctx`);
* growth of the original's proven goals since the goal's last fresh run;
* the original's success rate over its last 30 fresh runs;
* the goal's size and number of variables.

**Fresh runs in a new context win.** A fresh run succeeds 43% of the
time when its nearest proven goal below has changed since its last
failure. It succeeds 11–15% when that goal has not changed, at any
distance: 22% even 81+ lines away with a new context. (UL r5, 5,534
fresh runs.)

| failed fresh runs, same nearest proven goal below | runs | proved |
|---|---|---|
| 0 | 1,232 | 43% |
| 1 | 695 | 15% |
| 2 | 776 | 13% |
| 3 | 846 | 14% |
| 4+ | 1,985 | 11% |

**The model.** `schedmodel.py` is logistic regression on one-hot
quantile bins, 61 weights. It was trained on rounds 3–4 and the first
60% of round 5, and tested on the last 40% of round 5 (2,253 runs, 21%
proved).

| ordering | AUC | top 10% | top 25% | top 50% |
|---|---|---|---|---|
| model | 0.737 | 54% | 43% | 32% |
| proof-line distance | 0.599 | 30% | 29% | 25% |

The weights (log-odds) were these:

* a new context: +0.93;
* 1 to 4+ earlier failures in the same context: −0.11 to −0.63;
* growth of the original's proven set above 8%: +0.55;
* a hot original (recent success rate above 35%): +0.49;
* more than 84 lines from the nearest proof below: −0.86.

**In the loop.** With `loop.py --sched-model M.json`, the fresh-run
candidates are the goals whose context or pool changed, at any distance.
They are ordered by predicted success. Goals predicted below
`--sched-pmin` (0.06) wait until slots are idle, after the resumes; an
L1 resume proves about 17% in 3× the time. The history is replayed at
start (2 s). Each finished run and each synced proof updates it, and the
scores of the changed original are recomputed.

A 2-worker check (loops/SMT, a reflink copy of UL) made 16 proofs in 23
fresh runs in its first 5 minutes; these were the model's top picks.

**A/B 1: a tie after an hour.** ABa (distance order) and ABb
(`--sched-model sched/m2.json`, retrained with UL14's runs) ran from the
same reflink copy of UL, 9 workers each, from 04:05 to 05:07.

| minutes | ABa (distance) | ABb (model) |
|---|---|---|
| 8.5 | 11 | 60 |
| 29 | 97 | 128 |
| 43 | 122 | 156 |
| 53 | 166 | 171 |
| 62 | 177 | 180 |

The union was 255; at 29 minutes only 30 proofs were common.

* ABa began with 76 resumes (L1, 16% at 3× the cost of a fresh run).
  Then it worked the near goals in proof order: 35% of its fresh runs
  succeeded, each proof giving a new context to the goal above it.
* ABb ran no resumes. Its fresh runs proved 53, 53, 18, 27, 6 and 14
  per 10 minutes. In the fifth bin, 65 of 132 runs went to one
  original, nslm_to_aa1, at a median of 702 lines from the nearest
  proof: 6 proved, 22 predicted.

**The cause** was the quantile bins: one bin held every distance beyond
84 lines, so 700 lines scored like 100. In rounds 3–5 the gain from a
new context also falls with the distance:

| proof lines | new context | same context |
|---|---|---|
| 0–13 | 59% | 19% |
| 22–40 | 48% | 15% |
| 41–80 | 27% | 11% |
| 81–160 | 16% | 5% |
| 161–320 | 15% | 8% |
| 321–640 | 11% (28 runs) | 6% (16 runs) |

**Fixes.**

* Fixed bins for the distances (13, 21, 40, 80, 160, 320 lines).
* `lg_new`: the distance when the context is new, crossed into one
  feature.
* `--sched-max-lgap 320`: farther goals run only in idle slots.
* `--sched-retrain 200`: retrain on all replayed and new fresh runs.

On ABb's last 515 fresh runs, the fixed bins raised AUC from 0.751 to
0.807. Both arms (251 proofs) were merged into UL, and the climber was
stopped.

**A/B 2: the scheduler with a 10 s first level wins.** Three arms ran
from one copy of UL (43,272 solved), 7 workers each, from 05:16:

* ABc: distance order;
* ABd: `--sched-model sched/m3.json --sched-max-lgap 320 --sched-retrain 200`
  (m3: fixed bins and `lg_new`, AUC 0.736 against 0.671 for distance);
* ABe: as ABd, with a 10 s first level (`--cascade 10,80`).

New proofs (ABc / ABd / ABe):

| minutes | ABc | ABd | ABe |
|---|---|---|---|
| 12 | 15 | 34 | 33 |
| 22 | 19 | 43 | 63 |
| 33 | 22 | 52 | 68 |
| 35 (stopped) | 22 | 52 | 69 |

Union 88. ABe ran twice as many fresh runs for the same CPU (14% proved
against 24% for ABd).

After 25 minutes all three arms ran dry: 5 proofs in 10 minutes on 21
CPUs. A/B 1 and UL14 had taken most of the new contexts. The remaining
candidates had already failed in their current context. With the same
settings, such a rerun repeats a deterministic search, so it can only
succeed if the hint pool has grown.

The arms were stopped at 35 minutes and merged into UL (43,360 solved).

**Next: a portfolio for stalled goals.** sets/st80 holds 80 of the
1,575 goals within 80 lines of a proof whose last fresh run failed with
the same nearest proven goal below (`abs/stalled_set.py`). Each goal gets
fresh 20 s runs in 8 variants of the L0 configuration (`abs/port.sh`,
snapshot loops/ULsM, 2 workers each):

* the base configuration;
* term orderings 1 and 2 (`--p9-orders 4 --p9-order-offset k`);
* no rule model;
* 12 or 2 sibling lemmas;
* the 500 most frequent hints;
* rule threshold 0.3 with penalty 5.

Production (UL15, `abs/ul15.sh`) meanwhile ran the scheduler with
`--cascade 10,80` on 4 workers: 8 new proofs in 100 fresh runs in
7 minutes, about 16 proofs per CPU-hour.

**The portfolio does nothing on stalled goals.** After 35–41 goals per
variant, every variant except the 500-hint one proved exactly one goal,
the same one: com_Ralt__goal_246, whose pool had grown with the merges.
On about 35 stalled goals, 7 variants at 20 s proved nothing beyond it:

* other term orderings;
* no rule model;
* more or fewer sibling lemmas;
* other rule-model settings.

The probe was stopped there (06:00).

So a stalled goal needs new information: a proof nearby, or much more
search. Settings make no difference. Production went to 20 workers
(UL16, `abs/ul16.sh`, 06:01).

**Breakthrough probes.** On sets/st79 (st80 without
com_Ralt__goal_246), from ULsM, 2 workers each, 06:05–06:22:

* the sketch climber as CL5 (8 unproven siblings and 8 kNN goals as
  true assumptions, `--fill 3`; `abs/clst.sh`): 0 of 15 goals;
* fresh 80 s runs (`T=80 V=base abs/port.sh`): 1 of 11.

These goals resist everything tried at these budgets.

> **Correction (15 Nov, 09:40): these probes are invalid.** loop.py
> `--init` imports only the rows of round 0, and the snapshot loops/ULsM
> kept the loop's round numbers. So every probe from it ran with the
> 33,720 round-0 proofs as context (lemmas, pools, kNN lemmas) instead
> of 43,484. This covers the portfolio, the breakthrough probes and the
> stalled-goal probes of 2ad (`--pool tier`, `--pool knn`, rm7t).
> In the full current context, fresh 20 s runs prove about 15% of these
> goals (2ae). The snapshots for the paired model tests (ULsT) and later
> probes (ULsN) have the column set to 0.

**Resumes are now the productive work.** UL16 made 43 new proofs in
20 minutes, about 6.5 per CPU-hour. Its fresh runs proved 27 of 424
(6%, predicted 41). Its resumes (10 s to 80 s) proved about a quarter.

In round 5, resumes succeed equally at every distance: 23% within 13
lines, 19% at 14–21, 23% at 22–40, 23% at 41–80, 29% beyond (24 runs).
However, `--line-gaps 80,13` allowed resumes only within 13 lines.
UL17 (`abs/ul17.sh`, 06:23) uses `--line-gaps 80,80`. It made 26 new
proofs in its first 6.5 minutes, then 5 in the next 9.

**Where the unsolved goals are (06:45).** The 8,335 unsolved goals form
1,006 runs of consecutive unsolved goals within their originals:

* 559 single holes, between two proven goals;
* 95 open tails, from the goal after an original's last proven goal to
  its end, with 4,851 goals (58%);
* the rest are runs closed by a proven goal above.

The 95 tail heads are the best breakthrough targets: a head's proof
gives the goal above a new context (about 50%), and so on up the chain.
They had barely been tried. 93 had never run beyond 80 s, and the
median head had 6 runs and 416 wall seconds in all.

**Changes** (`loop.py --head-first --head-only-from L`, 9cc44be):

* within a cascade level, tail heads deepen first;
* only heads go to levels ≥ L;
* heads deepen at any distance.

UL19 (`abs/ul19.sh`, 06:43) runs `--cascade 10,80,320,1280 --head-first
--head-only-from 3`. The order follows proofs per CPU-second. Resumes
to 80 s go first (about 20%, 150 wall s), then the heads' 320 s runs,
then the others' (about 30% of L1 failures in r5, about 480 wall s).
The heads' 1,280 s runs come last.

That left about 2,185 goals waiting for an 80 s resume (about 4 hours)
before any head ran at 320 s. UL20 (`abs/ul20.sh`, 06:58) therefore put
the heads first for their 80 s and 320 s levels.

**Negative: the heads at 320 s.** In UL20's first 36 minutes the heads'
320 s resumes proved 5 of 62 (8%, not the 30% assumed), about 0.4 proofs
per CPU-hour. There were 4 new proofs in all. The tail heads are the
hardest goals, not the cheapest breakthroughs.

UL21 (`abs/ul21.sh`, 07:36) goes back to level order:
* `--cascade 10,80,320` without `--head-first`;
* the 80 s resumes first (16–20%), then the 320 s runs.

## 2ad. Retraining the guidance on hard proofs, and a GNN (user's questions, 15 Nov)

**Is ENIGMA retrained?** No. Production has used rm4t, fixed, since
round 4, because three earlier tests found no online gain from
retraining:

* rm6t (2r) did not help;
* rm7t (+0.03 offline AUC, 2u) did not help;
* the online ENIGMA loop on sets/e3 lost, 971 against 987 with the
  round-0 model kept fixed (2u).

Those tests used easier goals and short runs. The user notes that the
later long proofs should be worth more for training than the many easy
ones. Rounds 4–5 have 3,274 given logs; round 5's median log is 203 KB,
against 51 KB in round 1.

**Stalled goals again** (INVALID, see the correction in 2ac: ULsM gave
the probes only the round-0 proofs) (sets/st79u: 73 unsolved goals of st79, snapshot
ULsM refreshed at 07:35, fresh 20 s, 2 workers each):

| variant | proved |
|---|---|
| base (rm4t, own original's pool) | 0 of 64 |
| `--pool tier:20:500:0.1` (kNN hints from other originals, then own pool) | 0 of 62 |
| `--pool knn:20:1000` | 0 of 73 |
| rm7t | 0 of 34 |

Neither hints from other originals nor rm7t move these goals at 20 s.

**Offline test set.** The 400 newest round-5 given logs (sets/ultest,
given/ultest) are hard proofs that neither rm4t nor rm7t saw.
rulemodel.py's new `--load M.txt,V --test-only` mode evaluates a saved
model on exactly those. rm4t: AUC 0.846.

* **rm7t** (base data plus loops/UL/given at 14 Nov 11:00, rounds 1–3):
  AUC **0.897**, better than rm4t on 341 of the 400 problems.
* **rm8h** (`abs/rm8h.sh`): rm4t's base data plus the 2,875 other
  round 4–5 logs (given/ul45), negmax 150: AUC **0.894** (26 GB, 22 min).
  The long proofs add nothing over rm7t's in-loop data from rounds 1–3.
  What helps offline is training on proofs of the same originals.

Calibration differs. At threshold 0.1, rm4t keeps 93.2% of proof rules
and defers 35.1% of the others; rm7t keeps 97.7% and defers 24.5%; rm8h
keeps 98.8% and defers 15.4%. At the production threshold the better
models therefore filter less.
* **GNN** (`gnn.py`, after Chvalovský, Korovin, Piepenbrock and Urban,
  LPAR 2023): a name-independent graph network with dynamic samples,
  CPU torch. Each sample is a problem cut at a random point, with the
  axioms, the goal and the last 512 rules added as context, and the next
  128 rules to score.
  * The graph has nodes for equations (axiom, goal, context or query),
    terms, variables and symbols; symbols are typed by arity only.
  * Messages pass along the left-side, right-side, symbol and argument
    edges, with mean aggregation; d = 32, 8 layers.
  * Evaluation scores every added rule of a test problem, chunk by chunk,
    with its preceding rules as context, giving a per-problem AUC like
    rulemodel.py's.
  * A 200-step smoke test reached AUC 0.726 on 5 test problems. The main
    run (6 threads, models/gnn1.log, 08:00) reached AUC **0.809** on 100
    test problems at step 2,000 and **0.802** at step 4,000. Its training
    loss kept falling (0.49 to 0.38), so it was stopped at step 4,000
    (models/gnn1.pt). At this size, 32,000 samples and about 25 CPU
    minutes, it is below both LightGBM models.
    The iProver results came with much longer training, and with the GNN
    scoring every generated clause for given-clause selection. Here a
    model only defers a rule once, at double cost (below).

**Online, paired** (`abs/mab.sh`; snapshot loops/ULsT = UL minus the 400
test goals, so each is unsolved, and the context is the same for every
arm; fresh 20 s, production L0 settings, no `--online`):

| model, threshold | proved of 400 | only this arm | work on shared proofs |
|---|---|---|---|
| rm4t, 0.1 (production) | 271 | 8 | 1 |
| rm7t, 0.1 | 273 | 10 | 0.98 (geometric mean; median 1.00) |

| rm7t, 0.2 (rm4t's proof-rule loss, 47.6% of the others deferred) | 269 | 9 | 1.00 |
| rm4t, 0.2 (control) | 261 | 4 (14 lost) | 1.04 |

`abs/mabcmp.py` compares the arms. The +0.05 AUC gives nothing online:

* at the production threshold, rm7t ties rm4t;
* at its stricter matching threshold, rm7t ties rm4t too;
* the stricter threshold alone loses 10.

| oracle rmO (trained on these 400 goals' own logs: AUC 0.956; at 0.1 keeps 99.3% of proof rules, defers 57.3% of the others), 0.1 | 273 | 9 (7 lost) | 1.03 |

So the better model only cancels the cost of a stricter filter. The
searches are driven by the pools and lemmas. 52 of the 263 shared
proofs have identical work under both models, and the rest differ by a
few per cent either way. **Even a near-oracle model gains nothing
through the defer-once filter** (rmO: 273 against 271, work 1.03).
Production keeps rm4t. Rule-model quality cannot pay off through this
mechanism, whether ENIGMA or GNN. A GNN would need a stronger hook, such
as the passive queue's order, where twee would have to score millions of
critical pairs per run. So the GNN is compared offline only; its twee
integration (a scoring server with batched calls) was not built.

The work ratio on shared proofs is a BliStr-style proxy: abstract time
to the same proofs (Urban 2013, user's remark). Counts of proved goals
stay the main measure, because hints may guide in a roundabout way.

**GNN version 2** (user, about 09:05: the signature is small, so the GNN should
be symbol-aware; mark the conjecture terms; expand the goal constants
from flattening; follow the dynamic data collection; train more on the
harder proofs and clauses).

* twee prints its given rules with the goal constants already expanded
  (`expandGoalConsts`): flattening constants become their definitions,
  and skolem constants become fresh variables. The ENIGMA model scores
  the same expanded forms. So the logs have no goal constants, but they
  also lose any mark that a term came from the conjecture.
* Changes in `gnn.py`:
  * symbol nodes get a learned embedding per name (the vocabulary is 9
    symbols) besides their arity type;
  * the conjecture's variables become skolem nodes, and its terms are
    typed as goal terms;
  * every rule term that is a variant of a conjecture subterm with at
    least two function symbols is typed as marked and linked to that
    goal term by a goal-match edge (about 25% of rule term nodes);
  * the query's index in the run goes into the scoring layer;
  * training draws problems with weight (log size) ** 0.5 and anchors
    samples on proof rule i with weight i + 1. Long proofs and their
    late rules dominate.
* The samples stay dynamic: the rules added so far are the context, and
  the next added rules are the queries. That is the decision twee's rule
  model makes.
* Positives and negatives are balanced, as in Chvalovský et al.:
  * the loss is weighted per batch so that each class carries half the
    weight;
  * half the samples are anchored on a proof rule.
  Both versions do this.
* A 200-step smoke test gave AUC 0.847 on 5 test problems; version 1 gave
  0.726 at the same point. The main run (models/gnn2.log, 8,000 steps,
  6 threads, from 09:14; production on 11 workers) is evaluated on the
  same 100 test problems as version 1.

| on the same 100 test problems | AUC |
|---|---|
| GNN version 1 (names ignored), step 2,000 / 4,000 | 0.809 / 0.802 |
| **GNN version 2**, step 2,000 / 4,000 / 6,000 / 8,000 (final) | **0.864 / 0.879 / 0.876 / 0.887** |
| rm4t (production ENIGMA) | 0.837 |
| rm7t (ENIGMA with in-loop data) | 0.892 |
| oracle rmO (trained on these problems) | 0.958 |

The user's changes add about 0.07–0.08. Version 2 ends at 0.887: well
above the production ENIGMA model, level with rm7t. Online, the oracle
results (above, and with repeated deferral in 2af) mean the filter would
not use it.

**Prover9 on stalled goals** (`p9twee.py`): a LADR problem with
prolog-style variables, so TPTP names and twee hints need no
translation. It holds:

* the axioms, plus 6 proven siblings on either side as assumptions;
* the conjecture;
* the original's whole twee pool as `formulas(hints)`.

The first hit is aK2_eq_aK3_r__goal_241, a goal every twee variant failed
(settings, pools, models, the climber and 80 s runs). Prover9 proved it
in 44 s with 320 given clauses. The proof has 448 steps at level 64, with
clauses up to weight 1027, and 277 of its steps are hint matchers. The
proof's positive steps become the goal's twee hints, minus steps with the
goal's skolem constants.

* On all 72 stalled goals at 60 s (loops/P9T), Prover9 proved only that
  one: 1 in 72 CPU minutes, about 0.8 proofs per CPU-hour, on goals
  where twee gets 0.
* One run crashed inside Prover9-new ("stack smashing detected" after
  3,300 demodulation-limit hits, im2_24_to_25__goal_382), which looks
  like a bug in that build.
* Twee with the Prover9 proof as hints but without the sibling lemmas
  still fails the goal (30 s): the proof leans on the lemmas.
* Veroff's own AIM settings (from the AIM_REDONE `.in` files: kbo,
  `lex_order_vars`, no `back_demod`, `restrict_denials`, `para_from_small`,
  no `cac_redundancy`, `max_weight` 5) fail both goals Prover9 has proved
  so far.
  * `max_weight` 5 exhausts the search in 4 s, and 40 times out.
  * These settings depend on hint lists from earlier attempts at the
    same goal, so the defaults stay for our sibling pools.

**In production since 08:56:** `p9twee.py --live loops/UL loops/P9L -j 3
--timeout 60` (`abs/p9live.sh`), a Prover9 side worker.

* Targets: the loop's stalled goals within 80 proof lines (957 at the
  start), nearest first.
* A goal is retried only when its nearest proven goal below changes or
  its pool grows by 25%.
* Proofs go straight into loops/UL (hints file, then a solved row; the
  loop reads them with `--sync 60`).
* Its first proof came after 3 minutes: nslm_to_aa1__goal_688, in 53 s,
  with a pool of 15,182 hints.

Production runs beside it on 17 workers (UL24).

## 2ae. The stall was partly an artefact: kNN lemmas the cascade did not see (15 Nov)

**Control in the full context.** Snapshot loops/ULsN is UL at 09:30
with every row imported. On sets/st79u (goals whose fresh run and resume
failed in round 5 with an unchanged nearest proven goal below), fresh
20 s runs prove **7 of 71 goals without the lemma change and 10 with it**
(`abs/unit_probe.sh`, PU_0 and PU_1; +3/−0; work on shared proofs 0.99).
That is 18–25 proofs per CPU-hour, against production's 2.

* Some are now easy: nil3_24__goal_356 takes 1.7 s, nil3_32__goal_380
  1.4 s and nil3_29__goal_388 1.9 s.
* nil3_24__goal_356 had failed twice on 14 Nov, the last time a 141 s
  resume, and was never retried.
* **All six proofs of the first 35 use kNN lemmas**, proven goals of
  other originals with the same or a subset of the axioms
  (`--lemma-knn 10 --lemma-subsets`), proven after the goal's last run.
  For example nil3_24__goal_356 used TLRproperties_2__goal_314 and
  nil3_26__goal_372.

**Two leaks in the cascade:**

1. The retry gate looks only at the sibling context and the pool's
   growth. A change in a goal's kNN lemmas never made it eligible. The
   scheduler ranked these goals near the top (p 0.12–0.26, above its
   0.06 cutoff), but they were never candidates.
2. The kNN lemma index was built once, when the cascade started, so new
   proofs reached other goals' kNN lemmas only at a restart.

**Fix** (`loop.py --retry-knn`, 3f05146):

* the kNN index is rebuilt every 30 minutes or 300 proofs;
* each fresh run's kNN lemma set is recorded (DIR/knn_at.tsv);
* a goal whose current set differs from its recorded one is eligible for
  a fresh retry;
* the scheduler's order is walked best first, and the kNN check (27 ms
  a goal) runs only as far as free slots need;
* goals with no record count as changed. The first run after deployment
  is therefore one fresh pass in the full current context, best-scored
  goals first.

A smoke test from ULsN (sets/st79u, `--cascade 10,80`, 2 workers) proved
5 of these goals in 16 runs and 135 s. **Production since 09:44: UL26**
(`abs/ul26.sh`, 11 workers). Its first 100 fresh runs made **41 new
proofs in 132 s**, against about 2 proofs per CPU-hour before. The cap
on kNN checks per scheduling pass (b4c5cb5) arrives with the next
restart.

**Unit forms of conditional lemmas** (`lemmas.lemma_form`). A conditional
goal `~ s = X | C = D` whose hypothesis binds a variable X that does not
occur in s is equivalent to the unit equation `C = D` with X replaced by
s.

* That is 6,235 of AIM60k's 9,052 conditional goals (12% of all
  goals), and lemma import had skipped them all, as siblings and as
  kNN lemmas. The other 2,817 stay out: they are genuine Horn clauses.
* Prover9 had used such a sibling. Its proof of aK2_eq_aK3_d__goal_405,
  the goal twee failed 9 times, uses
  `-m(k(A,B),t(t(B,C),D)) = E | m(t(t(B,C),D),k(A,B)) = E`.
* The change gives 2,234 of the 8,270 unsolved goals a different set of
  sibling lemmas. On st79u: +3 (10 against 7 of 71).
* `TWEE_LEMMA_UNITIZE=0` turns it off.

## 2af. Repeated deferral, and definitions that twee folds (15 Nov)

**Repeated deferral** (`twee-e38 --rule-defer-max K`, 239245f). The
oracle rule model gained nothing online with the defer-once filter (2ad:
273 against 271). Could a stronger filter let a better model matter? A
critical pair below the threshold is now deferred up to K times, its
score multiplied by the penalty each time.

* With the default K = 1, e38 gives the same runs as e22 (20 of 20
  identical in rules and deferral counts).
* Paired test, fresh baseline (sets/ultest, the current lemma code,
  `abs/defer_test.sh`): rm4t with defer-once against the oracle rmO with
  K = 3 and penalty 5. **270 for the oracle against 269 for the
  baseline** (of 400; +8/−7), and 11% more work on shared proofs.
* So a better model does not pay through a stronger filter either. The
  GNN (2ad) stays offline: wiring it into twee is not worth it while the
  oracle itself gains nothing.

**Prover9's side worker partly races twee.** Of its 9 proofs, 4 are
short (1, 3, 10 and 130 steps). Rerun fresh at 20 s in today's context,
twee proves 2 of the 9. aK2_eq_aK3_r__goal_212 is a 1-step proof for
Prover9 (0.2 s) from sibling 209, which twee had too. Twee fails it in
20 s with 12,880 rules.

**The cause: twee folds definitions, Prover9 unfolds them.**

* AIM's defined operations are `a, k, l, r, t`, for example
  `t(A,B) = ld(B,m(A,B))`.
* Twee's KBO orients each definition right to left, since the defining
  term is bigger: `ld(X,m(Y,X)) -> t(Y,X)`. Prover9's default LPO in
  `p9twee.py` unfolds them (Veroff's own runs used KBO and folded, which
  is why the goals contain t and r).
* In goal 212 Prover9 unfolds t, and sibling 209 then rewrites the goal
  in one step. Twee needs the critical pair of 209 with the t rule, a
  pair of weight about 58, and never selects it.
* Twee has no option for this. `--kbo-weight0` and `--precedence` cannot
  make `t(A,B)` bigger than `ld(B,m(A,B))`, because B occurs twice.

**`unfold.py`** substitutes a problem's definitions away and drops them:
axioms, lemmas, conjecture and hints are then over m, ld, rd and e.
`loop.py --unfold` does this for every run. Hints are unfolded with the
problem's definitions. Folded runs normalise unfolded pool hints back,
because hints are kept normalised by the rules (`--eqhint-normalise`, on
by default).

* Goal 212 unfolded: **1.2 s, 2,755 critical pairs**.
* Unfolded terms are bigger. Unfolded runs take about 4.5 times as long
  in real time for the same abstract time (plain twee on 200 frontier
  goals, stopped after 14 runs: unfolded 1, folded 0). Most failed
  unfolded runs stop at `--max-cpu 200` before 20 abstract seconds.

**Results** (fresh 20 s runs in the production context: 6 sibling
lemmas, 10 kNN lemmas, the original's pool, rm4t; snapshots of UL at
10:24 and 10:44):

| goals | folded | folded + lemma instances | all unfolded | only t unfolded |
|---|---:|---:|---:|---:|
| the 9 Prover9 proved (sets/p9l9) | 2 | 3 | **7** | 3 |
| the first 10 of 231 that Prover9 failed (sets/p9no40) | 0 | 0 | **3** | |
| random frontier goals (sets/unf80), first 28 | 1 | 1 | 1 (0 of 25 without rm4t) | |
| sets/lf116 (p9no40 + unf80), 111 run | 4 | 4 | | |

The folded column is a control in the same snapshot (loops/LF_ctl).
Without it, "stalled" overstates the gains: the 4 folded proofs on
lf116 come from context that has arrived since production's last try
of these goals.

* Unfolding is not a better representation in general: on random
  frontier goals it gains nothing.
* It works on the goals Prover9's worker picks: the stalled goals
  nearest to a proof, in proof lines. There it proves goals both Prover9
  and folded twee fail.
* Unfolding everything beats unfolding only t (7 against 3).
* **Folded lemma instances** (`loop.py --lemma-fold 8`,
  `unfold.lemma_fold_text`) add, for each lemma subterm that unifies
  with a definition's body, the lemma under the unifier, folded. Goal
  212's missing critical pair is one of these, and 212 then takes
  2,000 critical pairs. Elsewhere they gain nothing: the same 4 of 111 on
  lf116 as the control, with 1.5 times the work. Most unfolded proofs
  need more than one such step.
* The 4 new proofs were merged into UL.

**In production since 11:18: an unfolded-twee side worker**
(`uflive.py`, `abs/uflive.sh`, 4 workers). It replaces the Prover9
worker, which was stopped at 10:24 after 9 proofs in 283 tries. Each
cycle:

1. syncs UL's proofs into loops/UFL;
2. takes 24 of p9twee's targets, nearest first;
3. runs one `loop.py --unfold` round on them;
4. merges the proofs into UL.

Its first two cycles proved 8 of 48 goals in 27 minutes on 4 workers,
about 4.5 proofs per CPU-hour. Production makes about 4 per CPU-hour
(UL27: 54 in 79 minutes on 10 workers).


## 2ag. Tail heads, and the cutoff between fresh runs and resumes (15 Nov)

**Tail heads** are the first unsolved goal after an original's last
proof. There are 92, with lines gaps 13–68 (median 34), and most
unsolved goals sit behind them. On 30 random heads (sets/heads30,
snapshot ULsV at 11:57, fresh 20 s, production context):

| arm | heads proved |
|---|---:|
| folded (control) | 0 of 30 |
| cross-original pool (`--pool tier:20:500:0.1`) | 0 of 30 |
| unfolded (2af) | 0 of 28 |

This also retests the tier pool, whose earlier negative came from the
invalid snapshot.

* **20 sibling lemmas** instead of 6: 0 of 30.
* **Later goals as hints** (`loop.py --hint-after 10`): the statements of
  the next 10 unsolved unit goals of the original. They are unproven, so
  hints only. 0 of 30 heads.
* **Twee settings on stalled goals, retested** (`abs/var_test.sh`, from
  ULsV, 36 goals Prover9's worker failed). The earlier portfolio
  negative also came from the invalid snapshot. Every arm proves 0:
  * the control;
  * `--no-flatten-goal`;
  * `--flatten-goal-lightly`;
  * `--flip-ordering`;
  * `--kbo-weight0`.

  On these goals only unfolding (2af) has proved anything.

**Fresh runs against resumes.** The last 1,500 UL27 runs:

| level | proved | runs | rate | CPU-hours | proofs per CPU-hour |
|---|---:|---:|---:|---:|---:|
| fresh (10 s) | 54 | 1,039 | 5.2% | 5 | 10.8 |
| resume to 80 s | 47 | 461 | 10.2% | 20 | 2.4 |

* A resume now costs 9 fresh runs (156 against 17 wall seconds). The
  0.06 cutoff, below which fresh candidates wait behind the resumes,
  assumed 3.
* The scheduler also overpredicts, 2.3 times (33 proofs against 77
  predicted).
* So a fresh run predicted at about 0.025 or more pays better than a
  resume.

**UL28 from 12:17** (`abs/ul28.sh`): `--sched-pmin 0.025`, 12 workers.
UL27's rate, for comparison: 93 proofs in 129 minutes on 10–11 workers,
plus 18 synced from the side workers.

**A 5 s first level?** Of the last 194 fresh proofs, 84% came within
10,000 critical pairs (5 abstract s), 69% within 5,000. The median is
3,390. A 5 s run costs 7.8 wall s against 17.8 for a 10 s run (8
failing goals). That is about 1.9 times the fresh proofs per CPU.

* **A/B from 12:48** (`abs/lvl_ab.sh`): reflink copies UA and UB of UL
  at 16,416 r5 rows, 6 workers each. UA uses levels 10,80,320, UB
  5,80,320.
* UB first ran with the 0.025 cutoff. After its scheduler retrained on 5
  s outcomes, the fresh candidates fell below it, and UB went to resumes
  after 360 fresh runs. The break-even scales with the fresh run's cost
  (0.44 × 0.025), so UB restarted at 13:08 with `--sched-pmin 0.011`.
* **Result after 62 minutes (13:50): 5 s 33 proofs, 10 s 20**, with 15
  in both (UB 18 alone, UA 5 alone).

  | arm | fresh proved / runs | resumes proved / runs |
  |---|---:|---:|
  | UA, 10 s, cutoff 0.025 | 13 / 476 | 7 / 91 |
  | UB, 5 s, cutoff 0.011 from 13:08 | 19 / 1,254 | 14 / 77 |

  Both arms were merged into UL (37 new).
* **UL29 from 13:55** (`abs/ul29.sh`): `--cascade 5,80,320`,
  `--sched-pmin 0.011 --sched-pmin-auto 400`, 12 workers.
* **`--sched-pmin-auto W`** (loop.py) sets the cutoff online from the
  last W fresh runs and W resumes: resume proofs per wall second, times
  the mean fresh wall seconds, divided by the scheduler's calibration
  (fresh proofs over predicted). With UL27's numbers it gives 0.026.

**Sibling lemmas in unfolded runs** (`abs/ufl_lem.sh`, sets/p9no_v, ULsV,
fresh 20 s, unfolded): 6 lemmas 3 of 36, 12 lemmas 4 of 36. The 12-lemma
arm proved all three of the 6-lemma arm's goals, plus one more. One goal
is within noise, so the side worker keeps 6.

**Long budgets on heads (15 Nov 18:15–19:05; `abs/heads_long.sh`, sets/heads_u,
the 30 heads still unsolved, fresh 160 abstract s, snapshot ULsW).**

* **Unfolded (HLU), stopped after 8 heads: 0.** Every unfolded run hit the
  800 s CPU cap (797–1,123 s) before 160 abstract s. Unfolded terms are
  bigger, and at long budgets the runs become CPU-bound.
* On the same 8, folded (HLF) proved 1 (aK2_eq_aK3_q__goal_270, 500 s).
  HLF continues; at 12 of 30 it has 3.
* So unfolding, which proved stalled goals at 20 s (2af), does not
  scale to the long budgets heads need.

**What a head proof is worth.** Replaying production's round 5
(loops/UL/r5/results.tsv, 21,784 runs, 2,751 new proofs), 69 proofs
were of the goal right after an original's furthest proof.

| proofs of the same original after a head proof | within 500 runs | 2,000 | 8,000 |
|---|---:|---:|---:|
| mean | 3.2 | 3.6 | 4.6 |
| median | 1 | 1 | 2 |
| none | 30 | 28 | 22 |

Other proofs are followed by 5.3 within 2,000 runs. So a head proof does
not unlock a chain; the goals behind a head are each hard. At about 0.4
proofs per CPU-hour for heads at 320 s, a head is worth about 2 proofs
per CPU-hour counting what follows. That is below production's current
3.5, so the scheduler's equal weighting of proofs does not starve the
heads.

## 2ah. A hint generator (user's suggestion, 15 Nov)

The user asked whether the GNN2Seq model of Chvalovský, Suda and Urban
("Neural Conjecturing for Saturation Theorem Provers", IWIL 2026;
github.com/JUrban/E_conj_dev1, branch vampire4) could be trained here
to propose hints from a run's current situation: generate new hints
rather than rank clauses.

* **No GPU is needed.** Their model has about 3M parameters and trained
  on a GPU in 48 minutes per 100 epochs. Ours is smaller (0.58M) on
  small AIM graphs and trains on 4 CPU threads at about 1.7 s per step.
* **Why it might help where ranking stopped helping.** The ranking
  models (2ad) can only reorder what twee produces. Stalled goals lack
  hints for steps that no sibling proof contains. Of the future proof
  steps of 188 solved test goals (cut halfway through each proof), the
  original's hint pool holds 63% (median pool 4,774 hints); the other
  37% must come from somewhere else.
* **Generated hints cost little when wrong.** Twee matches hints by
  variant, and every critical pair is a theorem, so a false generated
  equation never matches anything.

**Model** (`hints/gen.py`):

* **Encoder:** gnn.py's symbol-aware graph (version 2: symbol nodes,
  goal skolems, goal-term marks) over the axioms, the goal and the last
  256 rules before a cut; 6 message-passing layers, dimension 64.
* **Decoder:** a causal Transformer (2 layers, 4 heads) with
  cross-attention to all the sample's nodes. It writes an equation in
  prefix order with three actions: SYM points at one of the sample's
  symbol nodes (pointer decoding, as their PointerTreeDecoder), VAR
  picks a variable slot numbered by first occurrence, EOS ends. An
  arity count keeps every sample a well-formed pair of terms, as their
  arity-constrained decoding.
* **Training samples:** a given log cut just before a proof rule (later
  cuts likelier); the targets are up to 16 of the proof rules from the
  cut on, in random orientation; logs weighted by size^0.5 (hard
  proofs). Data: given/train_only, ul45 and loops/UL/given (17,725
  logs), with the 400 newest r5 logs (sets/ultest) held out.
* **Sampling** decodes incrementally (cached self-attention; memory
  keys and values computed once for all samples): 200 equations in
  about 2 s on one thread.

**Online use** (`loop.py --gen-model M --gen-n N`): a failed run saves
the axiom rows and its last 256 rules (`genctx/`). twee-e39 adds
`--print-given-unsolved` for this; before, the given rules were printed
only with a proof. When the goal's next level resumes the saved state,
the run gets N sampled equations on top of its pool hints.

**Sanity check:** trained on one problem for 300 steps, the model
reproduces 4 of that problem's 8 proof steps after the halfway cut.

**Training speed.** The first version took 2.4 s per step. Two fixes
brought it to about 0.5 s:

* Dropout on the attention weights alone took half the time.
* Cross-attention was run per sequence over a copy of its sample's
  memory. It now runs once per sample over all its targets' queries.

**Offline results** at the halfway cut of held-out solved goals (exact
variant recall of the future proof steps; n samples per cut; T is the
temperature):

| model, step | n, T | recall | generated, derived later in the run | hits not in the pool |
|---|---|---:|---:|---:|
| gen1, 1000 | 200, 1.0 | 1/2,891 | 0.1% | |
| gen1, 1000 | 200, 0.7 | 4/2,891 | 0.2% | |
| gen2, 3000 | 200, 0.7 | 13/2,891 | 0.7% | |
| gen2, 3000 | 400, 0.7 | 24/2,891 | 0.6% | 2 (of 1,251 missing) |
| gen4 (novel targets), 4000 | 400, 0.7 | 9/2,025* | 0.3% | 3 (of 1,040 missing)* |

\* gen4 is evaluated in its own training run, on a different 29 test
goals.

The generator learns the common lemmas, which the pool already holds:
22 of its 24 hits are pool hints. The steps that matter are the 1,251
the pool lacks, and it finds 2 of them.

So gen4 fine-tunes gen2 at step 3000 on novel targets only
(`--novel loops/UL/hints`): the cuts and targets are proof steps that no
other goal of the original has as a hint. After 1,000 steps it finds 3
of 1,040 novel steps, about the same as before.

**A copy action** (`hints/gencopy.py`). Novel steps are long (median 18
symbols). On each side, the largest subterm already in the context
covers typically 40–70% of the step. So COPY points at a term node of
the sample, then one VAR action per distinct variable of the copied term
maps it to the equation's variable slots. Copies make about 22% of the
target tokens.

* The encode-decode round trip is exact.
* Overfitting one problem recovers 3 of its 8 future steps.
* gc1 trains on novel targets from gen2's encoder. On the same 29 goals
  as gen4 it finds:
  * step 1000: 10 of 1,040 novel steps (gen4: 3), 37 of 2,025
    future steps (gen4: 9);
  * step 2000: 12 of 1,040 novel steps, 32 of 2,025 future steps;
  * step 2000 with n 1,600: 19 of 1,040 novel steps (1.8%), 51 of 2,025
    future steps. Four times the samples gives 1.6 times the hits;
  * step 3000: 12 novel; step 4000: 11 novel. A plateau, so training was
    stopped at 18:13 (models/gc1_4000.pt).

**Online test** (`abs/gen_test.sh`, sets/gen200, snapshot ULsW):

| arm | fresh 5 s | resume +15 s |
|---|---:|---:|
| GC, control | 0/200 | 4/200 |
| GG, gen2 at 3000 (n 400, T 0.7), re-queued | 0/200 | 2/200 |
| GC1A, copy model gc1 at 1000 (n 400, T 0.7), re-queued | 0/200 | 4/200 |
| GQ, re-queue alone (no generator) | 0/200 | 2/200 |

GC1A proved one goal the control did not, `Ka1_eq_Ka2__goal_403`, and
missed one the control proved. None of the 280 hints it generated for
that goal is among the proof's 234 lemmas. GQ (re-queue alone) proved
2 of the control's 4 and nothing else, so neither the re-queue nor the
generated hints gain; GC1A's +1 is search perturbation.

* GG proved 2 of the control's 4 and nothing else.
* Its hints do steer the search. On one goal, of 353 generated hints,
  243 became joinable and 117 were matched by new rules (boosted
  critical pairs get selected).
* None of that is on a proof path.

**Instance matching of hints (negative).** Of the future proof steps
missing from the pool, 637 of 1,866 looked like instances of a pool
hint. Most of those came from false hints in the pools:

* `X0=X1` (783 matches);
* `m(X0,X1)=m(X2,X3)`;
* `X0=m(X0,X1)`;
* `ld(X0,X1)=rd(X1,X0)`.

They are generalised conditional facts: skolems of hypotheses become
variables. Under variant matching they are inert, because no critical
pair is false. Under instance matching they flood the queue: one hint
matched 270,716 critical pairs in a 5 s run.

twee-e41 has `--eqhint-instances` (a term index over the hints' sides;
`--eqhint-instance-factor`, default 0.1). It leaves out hints whose two
sides have different variables. It is off by default, and without it
the output is identical to e22.

With clean hints only (equal variable sets, no flat or variable
sides), instances cover 142 of 2,480 missing steps (3%), and the run
is 1.6–5 times slower in wall time. Dropped.

## 2ai. Conjecture cuts (user's suggestion after IWIL 2026, 15 Nov)

The IWIL 2026 paper (Chvalovsky, Suda, Urban) proves generated
conjectures separately and uses them as cuts. On Mizar60 that gave
+582 of 11,881 hard or unsolved problems, with the first useful
conjecture at median rank 3.

**Implementation** (`loop.py --gen-cuts K`, 1128103). Before a
goal's resumed level:

1. The generator (gencopy.py, `--counts`) samples equations from the
   goal and the last 256 rules of its failed level.
2. The K most often sampled ones become cut candidates, leaving out
   variants of the goal.
3. The candidates are proved in one `twee --multi-goal` run of
   `--gen-cut-time` abstract s, on the goal's axioms and lemmas, with
   its hints and rule model.
4. Those proved after at least one considered critical pair become
   axioms of the resumed level.

`--gen-cut-sep` proves each cut in its own run instead. That run uses
the kNN lemmas of the cut's own statement (`LemmaIndex.select(eq=)`) and
the rule model's goal block of the cut (`write_goalfile(lits=)`).
`cutoracle.py` supplies oracle candidates instead: rules of the goal's
later production proof.

**Results** on sets/cut9 (9 gen200 goals that production proved later,
in 5–128 s), snapshot ULsW, fresh 5 s then resume +15 s:

| arm | cuts proved | goals proved |
|---|---:|---:|
| control GC, +15 s | – | 1/9 |
| control, +20 s | – | 1/9 |
| oracle, 40 rules spread across the proof, one shared 5 s run | 14–27 of 40 | 1/9 |
| oracle, the 40 rules nearest the goal, shared | 2–22 of 40 | 1/9 |
| oracle, the 20 nearest the goal, each alone with its own guidance (5 s each) | 3–15 of 20 | 1/9 (7.3 s against 21.5 s) |
| generator gc1_4000, top 40, shared (3 gen200 goals) | 0 of 120 | 0/3 |
| generator, top 10 at T 0.7, each alone | 8 of 90 | 1/9 |

* **A shared cut run is uninformative.** Twee's completion barely
  depends on the goal: only the rule model's goal features and the
  lemma and hint selection do. A cut proved in a fresh 5 s run on the
  goal's own problem is essentially in the state of the goal's own
  failed 5 s level. In the IWIL setting, E and Vampire are
  goal-directed, so a separate proof of a cut searches elsewhere.
* **Separate runs with the cut's own guidance do differ.** Of the 20
  proof rules nearest the goal, they prove 69 against 35 for the
  shared run (34 only there). But they cost 20 runs instead of one.
* **Even oracle cuts gain nothing at this budget.** Up to 15 true proof
  lemmas as axioms made no new proof in +15 s; one goal went 3× faster.
  The proofs are 110–700 rules long, and the cuts that can be proved
  are the easy part.
* **The generator's cuts** are mostly small identities (for example
  `t(k(X0,X1),k(X0,X1)) = k(X0,X1)`).
* **AIM60k already has the strong form of cuts.** Its goals are
  Prover9's intermediate goals, and the sibling-lemma chain imports
  them as axioms once proved (section 3, item 1). That is the oracle
  conjecture-cut mechanism, and it is the loop's largest gain.

Not pursued further. Cut generation in the middle of a run (the user's
question) has the same limit: a cut proved by the run's own saturation
is already in its state. Only a cut proved by a differently guided
search adds information.

## 2aj. Sketches in stronger theories, climbing up and down (user's suggestions, 15 Nov evening)

The user's points:

* Assume stronger theories instead of laws. They are mathematically
  relevant (Bol loops for loops) and should not trivialise the sketch.
* Dream up new axioms with the generator.
* When a sketch is still too hard, make the theory stronger or the goal
  weaker. Climb both up and down, and learn from the climbs.
* This follows the over- and under-approximation of Hernandez and
  Korovin, IJCAR 2018.

**What `climb.py` now does** (04617bc–493f9cd):

* `--min-sketch-steps N`: a law, theory or generated equation whose
  sketch proof has fewer than N steps is banned for the target.
* `--theories K`: the extra axioms of up to K stronger theories, one
  theory at a time.
  * A stronger theory is the axiom set of another original that
    strictly contains the target's. 74 of the 129 originals have one;
    the 17-axiom base theory has 115.
  * Theories are ranked by the similarity of their solved goals to the
    target.
  * `--theory-lemmas 10` adds the stronger theory's proven goals most
    similar to the target (`LemmaIndex.select_in`). They are true in B,
    not in A.
* `--gen-assume K`: the generator's most sampled equations, one at a
  time.
* `--updown` (`climb2`): when no sketch proves the target, go up.
  * Up: unions of the theories, and weaker goals, which are instances
    of the conjecture (two variables merged first, then a variable set
    to e). They go in through `loop.py`'s new `goal_override` hook.
  * Down, from every proof: drop a used assumption, or restore the goal.
  * Every proof's steps become hints of the original.
* `--chain`: a proof in the climb is a sibling lemma and hints for the
  original's later targets at once.

**sets/gen48** (the first 48 of gen200: unsolved, each with one failed
fresh 5 s run; snapshot ULsW, 1 worker each):

| arm | proved | CPU s |
|---|---:|---:|
| fresh 20 s (control) | 1 | 1,589 |
| fresh 20 s `--backwards-goal 1` | 1 (the same, 35.68 against 35.69 s) | 1,545 |
| fresh 20 s `--hint-goal` | **2** | 1,822 |
| CL6A: siblings + kNN goals + gap filling (CL5's config) | 2 | 4,903 |
| CL6L: laws only, trivialising laws banned | 2 | 4,168 |
| CL6T: 6 stronger theories + their lemmas | 2 | 4,546 |
| CL6U: CL6T + up/down | 2 | 4,051 |
| CL6G: 6 generated equations | 2 | 4,483 |

* Every 2 is aK2_eq_aK3_d__goal_462 (the control's) plus
  Ka1_eq_Ka2__goal_403.
* `--hint-goal` alone proves 403 too, so 403 falls to any change in the
  search. On gen48 the sketches gain nothing beyond perturbation.
* **Sketches are trivial on these goals** whatever the assumption:
  * a nearby unproven sibling or kNN goal proves the target in 0.3–2 s;
  * so does a stronger theory's proven goal (one lemma, 1.7 s);
  * so does a generated equation (0.3–2.8 s; the generator writes
    near-restatements of the goal);
  * so does a weaker goal (an instance, 0.5–1.4 s).

  The assumptions that help are as hard as the target, so the sketch
  covers only the easy last steps.
* gen48 spreads its goals over many originals, so sketch hints and true
  lemmas, which are shared within an original, barely accumulate.

**Family test** (`abs/fam.sh`): sets/fam24 holds the first 12 unsolved
goals, in proof order, of aK2_eq_aK3_1243b (66 stronger theories) and of
nsmr_to_aa1 (3). Snapshot loops/ULsX is UL at 20:15. Goals run in
order with `--chain`, 1 worker.

* **The full up-down climb (FUD) proved 3/24 in 2,652 s:** 1243b
  goals 441, 445 and 448, none of nsmr_to_aa1.
  * 441: the final run used 17 true lemmas proved by gap filling (a
    chain of real proofs); without them it fails.
  * 445 and 448: the runs with the hints alone also prove them, in
    14.2 s and 2.7 s.
* **Final numbers:**

  | set | arm | proved | CPU s | proofs per CPU-hour |
  |---|---|---|---:|---:|
  | fam24 | full climb (FUD) | 3 (1243b 441, 445, 448) | 2,652 | 4.1 |
  | fam24 | control: the same climb without assumptions, one fresh 80 s run per goal (F80) | 3 (1243b 446, nsmr 614, 616) | 6,032 | 1.8 |
  | fam24 | climb without stronger theories (FUDnt) | 1 (448) | 1,738 | 2.1 |
  | next 24 unsolved 1243b goals | full climb (FUD2) | 1 (455) | 2,904 | 1.2 |
  | next 24 unsolved 1243b goals | control (F80b) | 1 (455) | 4,981 | 0.7 |
  | fam24 | full climb + one-axiom up steps (FUDs, `--up-single`, 24 runs per goal) | 3 (the same as FUD) | 3,402 | 3.2 |

* The climb and long fresh runs prove different goals: 6 distinct
  between them on fam24.
* The stronger theories are what the climb adds on the base-theory
  family: 3 against 1 without them.
* Per CPU the climb is at least as productive as long fresh runs on
  goals production has stalled on.

* Adding one axiom at a time when going up (FUDs, the user's
  suggestion) proved the same goals as FUD at 28% more CPU.
* `--hint-goal` on the other 152 goals of gen200 (fresh 20 s from
  ULsW): the same 3 proofs as the control, at 13% more CPU. Dropped.
* The 12 proofs of today's probes that production lacked were merged
  into UL at 22:50 (`merge.py`; among them the heads
  aK2_eq_aK3_q__goal_270, mbol_12lemmas__goal_528 and
  mbol_nil3_a__goal_500 from the 160 s probe HLF).

**Deployed as a live side worker (22:07, `abs/clu.sh`, loops/CLU).**

* It runs the FUD config with `--up-single` (one more axiom when going
  up).
* It takes production's stalled goals and fills idle CPUs (`--cpus 20`,
  at most 6 climbs).
* Its proofs go into loops/UL.
* It saves every sketch's proof steps (loops/CLU/sketches). These are
  the data for learning the lattice moves, which the user asked for
  (15 Nov): which step, up or down, to take for a given problem, as a
  randomized policy.
* In its first 50 minutes, 73 climbs gave 2 proofs:
  aK2_eq_aK3_1243b__goal_445 and aK2_eq_aK3_gen__goal_495, the first
  unsolved goal of its original.
* `latticedata.py` turns climb directories into one row per move. The
  features describe the target (goal size, variables, axioms, number of
  stronger theories) and the move (assumptions by kind, theories and
  their rank, weakened goal, step). The labels are proved, nontrivial
  (an assumption used, at least 30 proof steps) and credit (the share of
  the target's real proof found in the sketch's proof).
* In its first 1.6 hours (to 23:43), 202 climbs gave 6 proofs:
  1243b_445, gen_495, 1243_342, aa1_45_c_285, aa2_12_355 and
  aa_instances_4_289.

## 2ak. Learning the lattice moves (user, 15 Nov: "what are the best steps in the lattice given a problem")

The climb walks a lattice of (assumptions, goal) nodes. Going up adds
assumptions: a stronger theory's axioms and lemmas, siblings, kNN goals
of other originals, one more axiom, or a weaker goal (an instance of the
conjecture). Going down drops assumptions from the sketch's used set.
Until now the order of the queued moves was fixed by hand: the real goal
before weaker ones, fewer assumptions first.

**What the logged moves say** (climb.tsv of the FUDs arm and the live
climber, 1,346 moves on 100 targets):

| move (assumption kinds) | moves | proved | nontrivial |
|---|---:|---:|---:|
| theory + siblings + kNN | 552 | 43% | 9% |
| siblings + kNN, weaker goal | 203 | 100% | 11% |
| theory + siblings + kNN, weaker goal | 139 | 100% | 11% |
| siblings + kNN | 116 | 30% | 16% |
| theory + kNN | 71 | 52% | 41% |
| kNN | 61 | 51% | 25% |
| kNN, weaker goal | 53 | 100% | 40% |
| siblings only | 45 | 4% | 0% |
| theory only | 43 | 28% | 28% |

* Nontrivial = proved, used an assumption, at least 30 steps.
* Weaker goals always prove. Siblings alone almost never help.
* A stronger theory with kNN goals but without the siblings gives the
  most nontrivial sketches.

**The pieces (commits 57a0b00 to 25d0e6c):**

* `latticedata.py` gives one row per move. Its features are shared
  with climb.py (`move_features`).
* Labels:
  * nontrivial;
  * credit, the share of the target's real proof found in the sketch
    (only when the target is proved);
  * realized, the share of the sketch's non-axiom steps that the real
    final run derived as given rules, proved or not. Realization is the
    dense one: Korovin's concretisation measured on the search.
    climb.py saves the final run's given rules (`realized/<t>`) for it.
* `latticepolicy.py train` fits a logistic model with a split by
  target. On nontrivial: held-out AUC 0.654. The largest weights are
  siblings (negative), the number of stronger theories (positive) and
  theory lemmas (negative).
* `climb.py --move-model M` samples the next move by softmax over the
  scores (`--move-temp`, default 1), with `--move-eps` (0.1) uniformly
  random moves.

**First test** (abs/fam4.sh, FUD2's config on the next 24 unsolved
1243b goals, policy lattice1): 1 of 24 (goal 455) in 2,410 CPU s,
against the fixed order's 1 of 24 (the same goal) in 2,498 CPU s. A
draw: one proof per arm can't tell them apart. 4 of the 24 targets were
in the policy's training rows; the live climber had visited them.

**A/B in the live climber (23:50, abs/clu2.sh).**

* `--move-ab`: targets with an odd crc32 of the name sample by the
  policy, the others take the fixed order.
* The comparison is proofs per CPU over many stalled production goals.
* The policy is retrained on the realization labels as they accumulate.

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
| long-run-scalability, mature-back-index-cpu, adaptive-back-index-crossover (indexing side) | paramodulation and back-demodulation indexes that stay cheap as the clause set grows | ported in twee's terms (2v): a fingerprint index for overlap partners (exact, 1.8× on long runs) and a backward-demodulation filter for interreduction. |

## 3. Assessment

*Rewritten 13 Nov evening, updated 14 Nov morning; earlier conclusions are corrected where noted.*

* **Overall.** On all 51,784 public problems at 4 s per problem, the
  first loop (rule model + kNN hints, then lemma import) solves 33,249
  against 31,060 for plain twee (+7.0%), with 13% less CPU (holdout 3417
  vs 3203). The Veroff-style online loop then runs everything left in goal
  order: its first round (5 abstract s) brings the total to 36,057 (+16.1%
  over plain; holdout 3,747), its second (20 s) to 39,008 (+25.6%;
  holdout 4,196), and a cascade round is running (2o, 2p). On the
  hardest goals of two families, long runs with whole-original pools
  solve 64 of 68 over four rounds (2m).
* **Where the gain comes from**, largest first:
  1. **The sibling chain: lemma import, run online.** Proven sibling
     goals become axioms (sound, CASC LTB-style, reported separately). In
     goal order, each proof feeds the next runs at once (+25% over fixed
     pools). Success depends on how near the last proof is: 58% at a gap
     of 1 goal at 20 s, 26% at 4–10, 0 of 5 beyond (2p). The loop advances
     along each original's proof.
  2. **The ENIGMA-style rule filter** (+5–6% at 2 s, +36% on hard dev
     goals at 8 s, +11 of 300 hard holdout goals at 60 s). In the 20 s
     ablation (2q) it is the strongest single guide: 42 of 189 against
     37 for hints and 28 for plain twee, at about 60% of plain's time.
     Without lemmas, ENIGMA and hints add up (49). With lemmas they
     overlap, and either one alone gives the full gain (58–59).
  3. **Hints from all of an original's proofs.** At 20 s and longer, the
     whole-original pool beats kNN-selected hints (60 vs 55 of 189 online;
     48 vs 40 of 68 at 300 s, against 36 without hints).
* **Hints in long runs: corrected.** The earlier negative result came
  from small hint lists (kNN, 100 hints): those runs stop matching after a
  few seconds because the list is used up. With pools of 2,000–6,000 hints
  the runs keep matching until late, and the pool adds 12 of 68 over no
  hints at 300 s. A hint's precision rises with the number of sibling
  proofs it comes from (0.8% from one proof, 51% from 20 or more), but
  weaker boosts for rare hints do not help (60 = 60).
* **What did not help** (each within noise or worse): sketches and
  chained sketches; kNN/goal-statement/ProofWatch hints on top of the
  model; more model data or capacity (rm5, rm4b); portfolios; P9 SFDF
  reorientation (2n); multi-goal search, which lacks the restart with the
  new lemma (2p); a stall rule at short limits (hint signals at 5 s do not
  predict 20 s success, 2o).
* **Engineering.**
  * Abstract time (critical pairs) makes runs deterministic and
    comparable. Real CP rates fall to 50–300 per CPU second on runs with
    40k–110k rules, so long runs cost far more than their abstract time.
  * Checkpoints: resuming now takes new lemmas (the signature bug fixed in
    twee-e20). A resume of a big state costs minutes, mostly re-scoring the
    saved queue against new hints (2m).
  * Giving an original up after 30 failures in a row lost no proofs in
    replays of the sets/u3 runs. In the full 5 s round, which used it,
    giving up after 10 would have kept 84.5% of the proofs for 46% of the
    time.

## 4. Next steps

*Updated 15 Nov, 12:10.*

* **Since 09:05:**
  * The cascade's retry gate now sees kNN lemma changes (2ae): about
    +160 proofs in 30 minutes, then the rate fell back to 40–60 an hour.
  * Model quality cannot pay online. The oracle model gains nothing,
    with defer-once or with deferral repeated 3 times (2ad, 2af). The
    GNN reaches AUC 0.887 offline and stays there.
  * Twee folds AIM's definitions and Prover9 unfolds them (2af).
    * Unfolded twee proves 7 of Prover9's 9 proofs, and 3 of 10 goals
      Prover9 failed. On random frontier goals it gains nothing.
    * It now runs as the side worker, instead of Prover9.
  * Controls in the same snapshot matter: without them, fresh context
    looks like a method's gain (the folded lemma instances, 2af).
* **Next:**
  * Watch the side worker's rate as it moves away from the nearest
    targets.
  * Tail heads (92 originals, 58% of the unsolved goals behind them):
    folded 0 of 30 at 20 s.
  * Production and side worker use 14 CPUs. The rest is for tests.

*Earlier (15 Nov, 09:05):*

* **Since 04:35:**
  * The learned scheduler with a 10 s first level is in production
    (2ac).
  * Stalled goals resist every twee variant: settings, cross-original
    pools, rm7t, the climber, heads at 320 s.
  * Retraining on the late, long proofs raises offline AUC (0.846 to
    0.894–0.897) but not online results, even with a stricter filter.
    The GNN plateaued at AUC 0.80 (2ad).
  * Prover9, given twee's pools and the sibling lemmas, proves stalled
    goals twee cannot, at about 0.8 per CPU-hour. It now runs as a live
    side worker.
* **Next:**
  * Measure the side worker over a few hours: its proofs, and twee's
    follow-up proofs on goals whose context it changed.
  * If it holds up, try Prover9 settings (max_weight, hint ratios) on
    the P9L failures. Try twee with the Prover9 proofs as hints on their
    neighbours.

*Earlier (15 Nov, 04:35):*

* **Since 14 Nov 22:30:** sketch climbing (2ab) works but is beaten 3× by
  fresh runs on its own targets. The cause was stale round-start
  semantics, fixed by `--fresh-first`. The retry line gap went from 21 to
  80, worth about 2.5× (UL14: 610 proofs an hour). A learned scheduler
  (2ac) orders the fresh runs by predicted success; in an A/B from one
  snapshot it led 60 to 12 after 8.5 minutes.
* **Next:** put the scheduler into production if the hour-long A/B holds.
  Then test a 10 s first level against 20 s with it (77% of fresh proofs
  come within 10 s, 59% within 5 s). Stop the climber, which makes under
  8 proofs per CPU-hour against about 47 for the learned loop.

*Earlier (14 Nov, 22:30):*

* **Done since the last update:** 6 sibling lemmas won (2r) and run in
  the full loop's cascade round 4. rm6t and rm7t brought no online gain
  (2r); the planned rm7t online test was cancelled because its training
  data held proofs of the test goals. Long runs are 1.8–2.0× cheaper in
  CPU (2v).
* **P9loop / Bigloop against resume** (2w, test 2): resume wins on the
  frontier (27 against 18–19 at equal time), and resuming without
  re-scoring the queue beats re-scoring (27 against 23). The full loop
  now resumes without re-scoring. Orderings are kept in reserve for goals
  whose resume has stalled.
* **A resume bug** grew one run to 100 GB; it is fixed, and every run now
  has a 6 GB heap limit (2x).
* **Consider-emulation off** (2y): about 30% less CPU, 76 against 77 on
  u3n150. The full loop runs without it from 20:15.
* **Proof-line distance** (2z): it predicts success (32% within 13 lines
  against 12% beyond 34; by goal gap 22% / 12%). The cascade orders its
  work by it from 20:58.
* **Stalled goals** (2aa): a fresh run with the current hints beats a
  longer resume (20 s fresh 14 proofs per CPU-hour, resume to 320 s 0 of
  13). The cascade retries goals whose hint pool has grown 25%
  (`--retry-hints 1.25`, from 22:28).
* **Sketch climbing** (2ab): `climb.py`. Laws alone add nothing; gap filling (`--fill`) plus true assumptions (siblings, `--knn`) matches fresh 80 s per CPU-hour and reaches other goals. A 64-goal test is running.
* **In-loop retraining** adds nothing online (2u): with the model kept
  fixed, FHL solves 970 after round 1, against 963 for EHL, which
  retrains. The full loop keeps rm4t fixed.
* **Next:** watch the full loop's deepening (round 5, 80 s by resume,
  without re-scoring the queue). For goals whose resume stalls at
  320–960 s, try a restart with a new ordering plus matcher lemmas
  instead of a longer resume. Also look at the hardest originals,
  where the frontier is far from any proof (gap > 3).

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
5. **The production loop as of 15 Nov 17:31** (`abs/ul31.sh` in
   /project/hintwork). It is a cascade of fresh 5 s runs ordered by the
   learned scheduler (2ac), with resumes to 80 and 320 s. Proofs that
   other processes append are synced in. Since 07:36 it has gained
   `--retry-knn` (2ae) and unit forms of conditional lemmas (2ae). It
   now uses `--cascade 5,80,320 --sched-pmin 0.011 --sched-pmin-auto
   400` (2ag) on 14 workers. The command below is the 12:17 version
   (`abs/ul28.sh`); `abs/ul31.sh` has the current one:

       loop.py sets/all loops/UL --start 5 --cascade 10,80,320 --cascade-start 0 \
         --cascade-continue --fresh-first --far-retry --retry-gap 3 \
         --sched-model sched/m4.json --sched-max-lgap 320 --sched-retrain 200 \
         --line-gaps 80,80 --retry-hints 1.25 --sync 60 \
         --model --model-fixed rm4t.bin,rm4t.vocab --model-theory \
         --lemmas 6 --lemma-knn 10 --lemma-subsets --lemma-after \
         --twee twee-e22 -j 12 --reserve 0 --pool original --wall-factor 15 \
         --sched-pmin 0.025 --retry-knn \
         --args="--abstract-time 2000 --no-resume-requeue --no-eqhint-consider"

   Beside it ran the unfolded-twee side worker (2af, `abs/uflive.sh`),
   stopped at 15:17 when it fell to 0–1 proofs per 24-goal cycle:

       uflive.py loops/UL loops/UFL -j 4 --batch 24 --loop-args "--pool original \
         --wall-factor 15 --model --model-fixed rm4t.bin,rm4t.vocab --model-theory \
         --lemmas 6 --lemma-knn 10 --lemma-subsets --lemma-after --twee twee-e22 --timeout 20" \
         --twee-args "--abstract-time 2000 --max-cpu 200 --no-resume-requeue --no-eqhint-consider"

   The model comes from `schedfeats.py loops/UL sets/all F.tsv` and
   `schedmodel.py train F.tsv M.json --drop hints,ofrac,ggap,nfail_c6`.
   The live climber (`climb.py --live`, 2ab) was stopped at 05:10.
   For a new round, use `--cascade-start -1`, so that every goal gets a
   fresh run in the new context first (2ab). Watch memory with
   `abs/memwatch.py 7 45`; twee itself stops at 6 GB (`-M6g`).
   A/B arms (reflink copies of UL) go back with `abs/merge_ab.sh`.
   `merge.py UL DIR...` adds proofs from probe dirs.
6. **Hint generator** (2ah, CPU torch in `venv`):

       venv/bin/python3 hints/gencopy.py train given/train_only,given/ul45,loops/UL/given,given/ultest \
         --test-names sets/ultest --save models/gc1.pt --init-enc models/gen2_3000.pt \
         --novel loops/UL/hints --steps 6000 --threads 4 --batch 8     (abs/gc1.sh)
       venv/bin/python3 hints/gencopy.py eval GIVENDIRS --test-names NAMES --load models/gc1.pt \
         --n 400 --temp 0.7 --pool-dir loops/UL/hints

   In a loop, `loop.py --gen-model models/gc1.pt --gen-script
   gencopy.py --gen-n 400 --gen-temp 0.7` with `--twee twee-e39` (or
   later) and `--resume-requeue` in the twee arguments. A failed level
   saves its context, and the resumed level gets the generated hints.
   `abs/gen_test.sh` is the paired online test.

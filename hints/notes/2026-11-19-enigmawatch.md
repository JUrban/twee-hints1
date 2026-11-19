# ENIGMAWatch for twee: the paper's recipe, and an offline test first (exp31)

Written 19 Nov 2026, 13:35 UTC. The user, 13:30: "I have now also added the EnigmaWatch paper -
project/1905.09565v2.pdf ; might be interesting to try (again, don't forget to really read the paper instead of
doing some guesswork)". Read in full (14 pages) before this note.

## The paper (Goertzel, Jakubův, Urban: ENIGMAWatch: ProofWatch Meets ENIGMA, arXiv 1905.09565v2, TABLEAUX 2019)

**ProofWatch (their section 2.3, from ITP 2018).**
* There are several watchlists W_1..W_n, one per related proof. A generated clause C matches W_i if C subsumes some
  D in W_i.
* progress(W_i) is the number of W_i's clauses matched so far, and the completion ratio is
  c_i = progress(W_i) / |W_i|.
* A clause's dynamic relevance is the largest c_i over the watchlists it matches. Higher relevance gives higher
  priority (E's PreferWatchlistRelevant).
* With many proofs E slows down, so only some proofs are loaded (k-NN chose 32 a problem in ProofWatch).

**ENIGMAWatch (section 3).**
* The proof-state vector phi = (c_0..c_N) of completion ratios is an evolving, vectorial description of the proof
  state. Each given clause is printed with phi at the time it was selected. phi becomes added features when
  ENIGMA's classifier is trained and when it is used.
* The watchlists must be **globally fixed** across the library, so that c_i means the same in every problem.
* **Data construction (3.2).**
  * A strong E strategy proves 14,882 of 57,897 Mizar40 problems.
  * E with ProofWatch and all 14,882 proofs loaded is then run on all problems (T60-G10000).
  * This gives, for each given clause, its proof-state vector: (conjecture, given clause, proof-state vector).
* **Dimension reduction** to a fixed set of 512 watchlists. For each problem, the mean of phi over its given clauses
  (mean-proof-vector) is a row of the matrix M. The selections are:
  * Mean: the 512 columns of M with the highest mean;
  * Var: the 512 columns with the highest variance;
  * Corr: a relatively uncorrelated set (from the Pearson matrix);
  * Rand: 512 at random.
* **Model:**
  * XGBoost, depth 9, 200 rounds;
  * clause and conjecture features hashed into 2^15 buckets each, plus the 512 completion ratios (66,048
    features);
  * probability >= 0.5 gives weight 1, else 10.

**Multi-index subsumption (section 4).** One feature-vector index per clause code (the set of signed predicate
symbols), since C subsumes D only if code(C) is a subset of code(D). Average 2.9x faster, 44x fewer subsumption calls.
For twee this does nothing: every clause is a positive unit equality, so all have the same code {+=}.

**Results (section 5)** on 5,000 random Mizar40 problems, 60 s or 30,000 generated clauses:

| system | solved |
|---|---|
| ProofWatch: baseline / Mean / Var / Corr / Rand | 1140 / 1357 / 1345 / 1337 / 1352 |
| ProofWatch union of the five | 1483 |
| ENIGMA against ENIGMAWatch Mean, loop 0 | 1557 against 1694 (+8.8%) |
| loop 3 | 1931 against 1954 (+1.2%) |
| ENIGMA with ENIGMAWatch Mean, union, loop 3 | 2110 |

* Over 13 loops ENIGMA and Mean converge, and their union stays about 150 above either: complementary.
* About 62% of the watchlist features are used in the trees, and the root of the first tree is a watchlist feature.

## What twee has already

* ProofWatch itself (twee `--eqhint-watch F`, 12-13 Nov; REPORT 2b):
  * each hint carries its source proofs (groups) as a 4th column of the hints file;
  * twee keeps each group's completion ratio (eh_gsize, eh_gdone);
  * a hint's boost moves from F toward its own factor as its best group completes.
  * On 345 problems at 8 s with rm2: 67 against 69 (+2 −4), not adopted.
* The ENIGMA-style rule model (rm4t, LightGBM, a binary forest in twee). Its row (src/Twee/Enigma.hs
  ruleModelRow):
  * 4 fixed columns (goal overlaps, log rule index);
  * the rule's hashed features (c:), optionally its parents' (p:);
  * the goal block and the theory block (g:).
* Missing for ENIGMAWatch:
  1. watch-only groups, which count completion but do not boost;
  2. the completion vector of a fixed set of groups as row columns;
  3. that vector printed in the given log, for training;
  4. the selection of the fixed set.

## Plan

**Step 1, offline (exp31): do completion features carry information for twee's rule model?** No twee change is
needed for this. From the given logs (loops/UL/given, 12,244 runs, rules in the order they were added, labelled
proof or not):
* Canonical keys: variables renamed by first occurrence, the smaller of the two orientations. A rule matches a
  watchlist step if their keys are equal. This is an under-approximation of ProofWatch's subsumption matching.
* Candidates: all proven goals' proofs (loops/UL/hints).
* M: for sampled logs, each candidate's mean completion over the run's rules. Select 512 by Mean, as the paper does.
* Training rows: rulemodel.py's rows plus the 512 completion ratios before each rule.
  * Train on training originals, evaluate on held-out originals (AUC, positives kept at a threshold), against the
    same model without the 512 columns.
  * Leakage: the problem's own proof is zeroed in its vector. A variant zeroes every proof of its original.
* LightGBM with 2 threads.

**Step 2, if step 1 shows a clear lift:**
* twee: watch-only groups and completion columns in ruleModelRow;
* the given log prints the vector;
* retrain, then online tests at 5 s against rm4t, and as a portfolio member.

## The ceiling from the record (read before launching)

* ENIGMAWatch makes the rule model better. twee's rule model acts only through the defer-once filter, and REPORT 2ad
  and 2af tested that filter's ceiling.
  * A near-oracle model rmO was trained on the test goals' own logs (AUC 0.956; at 0.1 it keeps 99.3% of proof rules
    and defers 57.3% of the others).
  * rmO: 273 against rm4t's 271 of 400 (defer once), and 270 against 269 with deferral up to 3 times at penalty 5.
  * Ordering the queue by the model (2ao, `--cp-model-factor`) costs about 10x the wall time.
* (Correction, 16:40, after the user's question.) There is a second, cheap hook: parental guidance (2av, production
  since 17 Nov). Each rule keeps rm4t's score of the pair it came from. A new rule's pairs with the active rules
  are not made at all when sigmoid(q1 + q2) < 0.25. That paid: +577 on half1 at 2 hours. Through PG, every better
  learned model (dense, ENIGMA pcat as in the paper, additive) lost online to the untrained sum of rm4t's scores
  (36-39 against 52 of 200), though each was better offline. The near-oracle rmO was tested only through deferral
  (15 Nov, before PG). So an oracle through PG is untested.
* So even a large AUC lift is unlikely to pay through today's hooks. The offline test measures whether the
  proof-state vector carries information twee's model lacks. An online test follows only if the lift is large, and
  through a hook the oracle has not closed.
* **ProofWatch's own part** (the hints' boost follows their source proofs' completion) acts on hints, which do pay in
  this system. The 13 Nov test was +2 −4 at F = 0.3: two goals no other setting proved. Under the portfolio rule
  that is a member to measure, not a negative. So:
  * **`--variants pw`** (loop.py, commit 3362943): each pool hint lists the solved siblings whose proofs contain
    it (4th column of the hints file), and twee runs with `--eqhint-watch F`.
  * `--pw-factor` defaults to 0.05: hints of unstarted proofs get a factor of 0.05, moving to the default 0.01 as
    their proof completes. All hints stay boosted, and relevance orders them, as E's PreferWatchlistRelevant
    orders matched clauses.
  * Smoke test (exp/pw_smoke.sh, 13:40): all 4,679 pool hints of nil3_15 328 carry groups (352 sibling proofs, a
    median of 13 steps each), and the runs ended normally.
  * It joins production's explored members at the restart after exp30 (ul65).

## exp31 setting (launched 13:45)

* `venv/bin/python3 exp/ew_offline.py loops/UL/given loops/UL/hints exp31/ew_mvr.jsonl --ntrain 1000 --ntest 300
  --nsel 800 --rounds 200 --threads 2` in /project/hintwork, log exp31/ew_mvr.log.
* Split: rulemodel.py's default, seed 1, a third of the 129 originals held out (43). Training and test problems are
  random given logs of their originals (seed 1).
* Watchlists: 32,127 proofs of the 86 training originals' proven goals (median 17 steps).
* Rows: rm4t's features (theory block). Training uses all positives and 200 sampled negatives a problem; testing
  uses every rule of the test problems.
* LightGBM: rulemodel.py's parameters (63 leaves, rate 0.1, 200 rounds), 2 threads; the same rows with and without
  the 512 columns.
* **Smoke test finding (40 problems): Mean selection degenerates on AIM.**
  * 98% of (problem, watchlist) pairs are partly matched.
  * The 512 highest-mean proofs are tiny (median 5 steps) and complete early (mean completion 0.97). They are
    nearly constant, and the trees used 53 of them.
  * AIM's theories share their basic steps, where Mizar's proofs are diverse.
  * So the run tests the paper's three selections: Mean, Var (mean completion 0.39, median 14 steps) and Rand
    (0.53, median 16).

## Results (13:45 - 14:09)

Log: [exp/exp31_ew_mvr.log](../exp/exp31_ew_mvr.log); per-problem rows /project/hintwork/exp31/ew_mvr.jsonl.

* Training: 1,000 problems of the 86 training originals, 356,944 rows (160,259 proof rules). Test: 300 problems
  of the 43 held-out originals, every rule of each run.
* The completion vectors are dense: 511 (Mean), 439 (Var) and 495 (Rand) of the 512 entries are nonzero on an
  average row.

| arm | watchlist features used | their gain share | AUC (mean) | paired dAUC | better / worse | t = 0.1: proof rules kept / others rejected | t = 0.2 |
|---|---:|---:|---:|---:|---:|---|---|
| base (rm4t's features) | | | 0.9004 | | | 0.941 / 0.437 | 0.854 / 0.643 |
| + 512 by Mean | 111 | 0.108 | 0.9013 | +0.0008 | 139 / 159 | 0.942 / 0.433 | 0.857 / 0.642 |
| + 512 by Var | 370 | 0.287 | 0.9016 | +0.0012 | 146 / 153 | 0.944 / 0.451 | 0.859 / 0.658 |
| + 512 by Rand | 406 | 0.343 | 0.9020 | +0.0015 | 152 / 146 | 0.944 / 0.454 | 0.858 / 0.657 |

## Reading

* **The trees use the proof-state vector, as in the paper** (62% of its features there; 79% and a third of the gain
  here for Rand). **But it adds almost nothing on held-out originals:** +0.001 AUC, with test problems split about
  50/50 better and worse. At threshold 0.1, Var and Rand reject 1.4-1.7 points more non-proof rules while keeping
  slightly more proof rules. That is the whole gain.
* So the vector carries little that rm4t's features (rule, goal, theory, log rule index) lack. The high in-sample
  use is the trees taking it as a proxy for what they already know: how far the run has gone (completion grows
  with time) and which theory it is in.
* Mean degenerates on AIM, as the smoke test showed: its 512 tiny proofs complete early, and the trees use 111 of
  them. The paper also found Rand competitive (ProofWatch 1352 against Mean's 1357). Here Rand is best by a hair.
* Not tested: the loop setting, with watchlists from the test problems' own originals (proven siblings). That would
  measure more information, but it is the information the sibling pool already gives as hints.
* With the oracle ceiling above (a near-oracle model gains nothing through the deferral filter), even the in-original
  version could not pay online through today's hooks.

## Decision

* **The ENIGMAWatch model features are not built into twee.** The offline lift is +0.001 AUC, and the oracle
  ceiling (2ad, 2af) says model quality does not pay through the defer-once filter anyway.
* **ProofWatch's part goes on as a portfolio member:** `pw@0` in ul65 from exp30's end, explored for 1 CPU h. Read
  its yield and its conditional proofs (exp/condvar.py) after that.

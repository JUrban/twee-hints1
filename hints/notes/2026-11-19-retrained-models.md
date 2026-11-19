# Retrained rule models as portfolio members (exp37)

Started 19 Nov 2026, 19:50 UTC. User, 19:35: "ok - go ahead with the retrained rule model member, subsampling sounds
good (using the shortest 3 proofs for each problem, or some random proofs, or training more on the longest proofs,
subsampling the negatives rather than positives, etc etc) - go and read the enigma and Mizar60 and related papers to
see all the tricks tried".

## What the papers tried for training data and models

Read 19 Nov 19:30-19:50; PDFs and text in /project/hintwork/papers/<arXiv id>/.

* **ENIGMA (CICM 2017) and Enhancing ENIGMA (CICM 2018):**
  * positives = processed clauses in the proof, negatives = the other processed clauses;
  * imbalance: first repeated positives 10×, then "accuracy-balancing boosting" (repeat the misclassified positives
    until positive accuracy exceeds negative);
  * directed looping: train, run, add the new proofs, retrain.
* **ENIGMA-NG (CADE 2019, 1903.03182):**
  * XGBoost handles the imbalance with the positive/negative ratio (scale_pos_weight), which is what rulemodel.py does;
  * feature hashing.
* **Hammering Mizar (ITP 2019, 1904.01677):**
  * loops M0..M3 each train on all proofs so far, from all earlier strategies;
  * deeper trees paid much: 200 trees at depth 9 / 12 / 16 gave +58% / +65% / +70% over the base strategy;
  * the cooperative mode loses fewer problems than the model alone.
* **ENIGMA Anonymous (IJCAR 2020, 2002.05406):**
  * a hyperparameter grid each loop, with every model evaluated on a fixed random 10% of the problems;
  * LightGBM depth × leaves over {10, 20, 30, 40} × {1200, 1500, 1800}; the best in loop 3 was depth 30 with 1800
    leaves. LightGBM is 10× faster to train than XGBoost, so more models can be tried.
* **MizAR 60 for Mizar 50 (ITP 2023, 2303.06686), 6.4:**
  * "the training data might start accumulating many proofs for some (easier) problems solved by many strategies.
    From loop (2) on, we, therefore, use only a limited number of proofs per problem. We either select randomly up to
    6 proofs for each problem, or we select only specific proofs (e.g., the shortest, longest, and one medium-length
    proof)";
  * several models with different hyperparameters (leaves, depth, features), and a greedy cover of the models, i.e. a
    portfolio of models;
  * only data from strategies with compatible term orderings, incompatible ones "in reasonably small amounts".
* **The Isabelle ENIGMA (ITP 2022, 2205.01981):**
  * compatible strategies only (same term ordering and literal selection);
  * for parental guidance, "the ratio of negative to positive examples is a valuable hyperparameter";
  * the test split is by problem name, so that all proofs of a problem are on one side;
  * proofs grow faster than problems: duplicate proofs of easy problems.
* **Suda, Learning from History (CADE 2021, 2102.13564):**
  * the loss is weighted so that each derivation (one run) counts equally, and within it positives and negatives
    contribute evenly;
  * "positive bias": err on the side of false positives (our deferral threshold 0.1);
  * "negative mining": add the failing base-strategy runs of problems only the guided one solved, for the typical
    wrong decisions of the base strategy;
  * keep one proof per problem in that experiment.
* **Suda, Vampire with a Brain (FroCoS 2021, 2102.03529):** loops with more axioms revealed, and different modes of
  using the model in a loop's runs to get more varied proofs.
* **Fast and Slow Enigmas (FroCoS 2021, 2107.06750):** read on 17 Nov (REPORT 2av). Parental guidance from the
  parents' concatenated features, plus the freezer.

## Our data

* **One log per goal in production** (loops/UL/given, 12,302 logs): the loop keeps the shorter proof's log. That is
  138 positives and 2,785 negatives on average (sample of 400), with a median of 82 and a 90th percentile of 324
  positives.
* The base data's copies are the same proofs. given/train_only, tr30, r0 and r0p share goals, with identical
  positive and row counts.
* **But about 100 other loops kept given logs:**
  * the A/B arms ABa–ABe (about 9,300 each);
  * the from-zero runs Z0–Z4 (21,000–31,000), ORA–ORH (about 15,600 each), PGA–PGD, P2A/P2D, UA/UB and SMT, with
    their .xfer transfer loops;
  * ALL (32,377), the holdout loops H1/H2 and HO8*, and the paired tests.
  * Every config read uses twee's default ordering (p9_orders 1) and no unfolding: compatible data.
  * Goals therefore have up to about 20 proofs, mostly the easy ones.
  * givenindex.py (19:48) indexes them all into models/given_index.tsv (name, loop, bytes, positives, negatives,
    mtime), so that a training set can select proofs per goal.

## Set and setting

* **Test:** the 400 newest production logs (sets/ul400n, 08:14–19:27 today), held out of every model's training.
  * Offline: per-goal AUC on them (`rulemodel.py --test-names sets/ul400n --test-only`), and rm4t and rm7t on the same
    logs.
  * Online: a paired test on the 400 at fresh 20 s, PG 0.25, from the snapshot loops/ULsN19. That is production's
    solved rows before the first of the 400, 46,800 goals, none of the 400. All arms have the same settings, rm4t
    the control. Measures: +/−, union, unique per CPU h.
* **Models** (theory block, 200 trees, abs/rm9.sh):
  * rm9a: rm7t's recipe on today's data: base (train_only, tr30_g1) + production's logs, 150 negatives per log,
    63 leaves.
  * Planned, after the index:
    * up to 3 shortest proofs per goal over all loops;
    * the shortest, a medium and the longest;
    * up to 6 random;
    * Suda's per-log weighting;
    * long proofs weighed up (`--long-exp`);
    * negatives proportional to positives (`--negratio`);
    * bigger trees (leaves 255–1023), as in Anonymous and Hammering Mizar.
* rulemodel.py (19:45-19:50):
  * the matrix is built from numpy parts (rm7t's 34 GB came from Python lists);
  * `--weighting log`, `--negratio`, `--long-exp`, `--max-depth`, `--min-data`, `--lr`;
  * `--list` for several proofs per goal (NAME@K).
  * Defaults unchanged: the old flags give the old model.
* **Members:** models that prove goals the control does not become production variants `mX@0`
  (`rmX.bin/.vocab` beside rm4t). They get the exploration hour, then CPU by their measured yield.

## The selections (20:08)

* **The index** (20:08): 643,782 logs with a proof, 47,482 goals.
  * Distinct proofs per goal: 1 for 5,722 goals, 2–9 for 26,980, and 10 or more for 14,756.
  * Proofs are mostly short: the median goal's shortest proof has 4 positives, its longest 19.
  * The 100 originals that still have unsolved goals hold 42,353 of these goals, so a tail-only model would keep
    almost everything. Not trained.
* givensel.py over the index, with the 400 test goals excluded:

| list | logs | from production | positives | rows at 100 / 150 negatives per log |
|---|---:|---:|---:|---:|
| short3 (the 3 shortest) | 129,293 | 7,714 | 3.0 M | 12.0 / 15.0 M |
| slm (shortest, medium, longest) | 129,293 | 9,840 | 4.6 M | 13.9 / 17.2 M |
| rand6 (up to 6 random) | 240,091 | 10,450 | 6.1 M | 24.4 / 30.7 M |
| long3 (the 3 longest) | 129,293 | 10,029 | 5.6 M | 15.7 / 19.4 M |

* So the multi-proof models take fewer negatives per log (32–64), and rand6 is left out for memory.
* rulemodel.py `--jobs N --vocab-from V` (20:05): forked feature workers over a frozen vocab (rm9a's). On the smoke
  set it gives the same rows and positives as the serial path.

## Models and arms

abs/rm9wave2.sh, started 20:09:41 (its header says 20:11, written before checking the clock):
* It waits for rm9a, then starts rm9a's paired arm.
* Then it trains, one at a time on 4 workers, each model followed by its arm on 1 worker:

| model | data | negatives per log | weighting | leaves |
|---|---|---|---|---:|
| rm9a | base + production (one proof per goal) | 150 | none | 63 |
| rm9b | short3 | 64 | none | 63 |
| rm9d | short3 | 64 | Suda: per log, half positives | 63 |
| rm9c | slm | max(32, positives) | long proofs up (exponent 0.5) | 255 |
| rm9e | long3 | 64 | none | 255 |

* rm9a → rm9b is the data effect (all loops, 3 proofs per goal), rm9b → rm9d the weighting effect, and rm9c and
  rm9e the long-proof and tree-size variants.
* The control arm loops/MR_rm4t_20 has run since 19:52.
* Offline baseline on the 400 test logs: rm4t AUC 0.835, keeping 93.5% of proof rules at 0.1. rm7t AUC 0.874,
  keeping 98.4%.
* CPU: production 13 + climber 4 + training 4 + arms 1–5. When the arms pile up, production goes down
  accordingly.

### Revised at 20:23: memory

* rm9a's process reached 21.5 GB for about 5 M rows. Per row (5 test logs, rm7t's vocab):
  * the theory block takes 121–132 nonzeros;
  * the goal block 34–42;
  * the rule's own features 36–45.
* So about 85% of the matrix repeats per-problem constants. Only 47 of the 247 theory features are constant over all
  129 originals, and there are 60 distinct theory blocks, so pruning would save only about a quarter.
* The first driver (abs/rm9wave2.sh, which would have given rm9b 9.6 M rows) was stopped at 20:23 before it trained
  anything. abs/rm9wave2b.sh keeps every model at 7 M rows or fewer:
  * rm9b: short3, 32 negatives per log (6.9 M rows);
  * rm9d: short3, 32 negatives, Suda's weighting (6.9 M);
  * rm9c: slm, 16 negatives, long-exp 0.5, 255 leaves (about 6.6 M);
  * rm9e: the 2 longest proofs per goal (list_long2: 89,155 logs, 4.6 M positives), 16 negatives, 255 leaves
    (about 6.0 M).
* rulemodel.py now builds LightGBM's dataset first and then frees the CSR copy.

## Results

**Offline, on the 400 held-out newest production proofs:**

| model | rows, positives, logs | AUC | at 0.1: proof rules kept | other rules deferred | train | peak memory |
|---|---|---:|---:|---:|---:|---:|
| rm4t (production) | | 0.835 | 93.5% | 30.0% | | |
| rm7t (14 Nov) | | 0.874 | 98.4% | 14.3% | | |
| rm9a | 4.76 M, 2.10 M, 21,125 | **0.876** | 99.5% | 6.6% | 39.5 min | 22.7 GB |
| rm9b (short3, 32 negatives) | 6.90 M, 3.01 M, 129,293 | 0.740 | 98.8% | 3.0% | 26.5 min | 28.7 GB |
| rm9e (long2, 16 negatives, 255 leaves) | 6.03 M, 4.64 M, 89,155 | 0.854 | 99.3% | 6.5% | 27.0 min | 24.9 GB |
| rm9c (slm, 16 negatives, long-exp 0.5, 255 leaves) | 6.57 M, 4.55 M, 129,293 | 0.842 | 99.9% | 1.7% | 28.9 min | 27.3 GB |
| **rm9f (rm9a's data, Suda's per-log weighting)** | 4.76 M, 2.10 M, 21,139 | **0.892** | 99.4% | 13.2% | 19.8 min | 20.3 GB |

* rm9a ranks as well as rm7t, and is calibrated higher: at production's thresholds it defers and freezes much
  less. A threshold matched to rm4t's deferral share would differ. That is the same caveat as exp33's rmO.
* **rm9b is much worse: the 3 shortest proofs of every goal over all loops hurt.** 122,000 of its 129,293 logs come
  from the from-zero and A/B loops, mostly easy goals at 2 s (median shortest proof 4 positives). With 32 negatives
  per log it sees few of the negatives a hard search makes. A model trained on easy proofs ranks the rules of hard
  ones badly. That fits what the user said on 15 Nov: later long proofs are worth more than many easy ones.
* So rm9d (the same data, Suda's weighting) was stopped at its start (20:57), and abs/rm9wave3.sh (20:58) runs, in
  order:
  * rm9e: the 2 longest proofs per goal, 255 leaves;
  * rm9c: shortest, medium and longest, long proofs up, 255 leaves;
  * rm9f: rm9a's data with Suda's weighting;
  * rm9g: rm9a's data with 255 leaves.
* rm9b's paired arm runs anyway: a weak model can still prove other goals (portfolio rule).
* **rm9e: the longest proofs recover most of it** (0.854: above rm4t, below rm9a). Over the same loops, the 2 longest
  proofs per goal are far better training data than the 3 shortest. Production's own logs with more negatives per
  log (rm9a) are better still.
* Interim paired counts (21:25, replay design): rm9a +5 −3 against the control on 98 goals, rm9b +3 −6 on 78.
* Interim at 21:54: rm9a +5 −8 on 165, rm9b +5 −7 on 141, rm9e +5 −3 on 102. Every model proves goals rm4t
  misses. Production's m9a@0 ended its explore hour with 0 proofs in 1.05 CPU h (the 5 s tail).
* **Suda's weighting is the best offline** (rm9f 0.892, against 0.876 for the same rows unweighted). Every log weighs
  the same, so the many short proofs no longer dominate the positives, and the many negatives of a long search no
  longer dominate one log.
* Interim at 22:14: rm9a +9 −11 on 213, rm9b +5 −14 on 182, rm9c +2 −5 on 67, rm9e +5 −3 on 143.
* CPU: 5 arms + training 4 + climber 4: production restarted at 21:54 with J=8 (rows from 179,422; earlier log loops/UL71a.log).
* **The first paired design was broken (found 20:58).** The snapshot loops/ULsN19 (production's solved rows before
  the first test goal, all 400 removed) gave the rm4t control 2 proofs in 122 goals.
  * Production had proved these 400 easily: median 3.5 s, 99% within 20 s, mostly at L0 and the 5 s kNN members.
  * Today's newest proofs are long sibling chains in few originals (aK2rev, aK2_eq_aK3_*, nil3_23_32_to_*), each
    goal proved with its just-proven predecessors as sibling lemmas. Removing all 400 removes the stepping stones.
    exp33's ultest set (15 Nov) was spread over many originals and lost little this way.
  * Stopped at 21:01: MR_rm4t_20 (2 of 126), MR_rm9a_20 (0 of 50), MR_rm9b_20 (0 of 5). The directories stay as the
    record.
* **Replay design (21:01, exp/modelreplay.py, abs/mabrm.sh rewritten, arms in loops/MQ_<model>_20).** As exp36:
  * each test goal runs in production's context as of its own proof (solved rows before its row);
  * kNN lemmas come from the 47,000 goals before the first test goal;
  * fresh 20 s, PG 0.25, 6 sibling and 30 kNN lemmas (production's L0);
  * smoke test: 2 of 3 goals proved in 1–2 s.
  * Arms rm4t (control), rm9a and rm9b started at 21:01. The queue's later models get their arms from the new
    abs/mabrm.sh.
* **Member:** ul71 (20:30, production rows from 174,090) = ul70 + `m9a@0`, J=10 while exp37 trains and runs its
  arms. Its arm on the 400 (loops/MR_rm9a_20) started at 20:30 beside the control.

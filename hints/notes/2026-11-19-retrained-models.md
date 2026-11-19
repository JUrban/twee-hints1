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

(running)

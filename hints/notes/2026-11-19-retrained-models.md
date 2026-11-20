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
| rm9g (rm9a's data, 255 leaves) | 4.76 M, 2.10 M, 21,140 | 0.886 | 99.0% | 14.4% | 20.8 min | 20.0 GB |
| rm9h (long2, 16 negatives, 255 leaves, Suda's weighting) | 6.03 M, 4.64 M, 89,155 | 0.891 | 98.7% | 20.7% | 29.6 min | 24.9 GB |
| **rm9i (rm9a's data, Suda's weighting, 255 leaves)** | | **0.900** | | | | |

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
* Bigger trees help too (rm9g 0.886 against 0.876), less than the weighting. Wave 4 (abs/rm9wave4.sh, 22:14)
  combines them: rm9h = long2 + weighting, rm9i = rm9a's data + weighting + 255 leaves.
* Interim at 22:34: rm9a +9 −14 on 245, rm9b +7 −18 on 216, rm9c +5 −5 on 113, rm9e +6 −10 on 185, rm9f +5 −2
  on 96.
* The weighting rescues the multi-proof data: long2 goes from 0.854 (rm9e) to 0.891 (rm9h).
* **Interim at 23:04: online, the deferral share matters, not the ranking.** Against the control:

| model | goals | + | − | deferred at 0.1 (offline) |
|---|---:|---:|---:|---:|
| rm9a | 295 | 11 | 23 | 6.6% |
| rm9b | 246 | 7 | 23 | 3.0% |
| rm9c | 171 | 5 | 10 | 1.7% |
| rm9e | 236 | 9 | 14 | 6.5% |
| rm9f | 177 | 5 | 4 | 13.2% |
| rm9g | 102 | 4 | 4 | 14.4% |

  * rm4t defers 30.0%. Production's thresholds (deferral 0.1, PG 0.25) were tuned to rm4t's calibration. The new
    models score rules higher, so they prune less, and those that prune least lose most.
  * **Calibration shift:** adding a constant to every leaf of a model's first tree shifts every raw score by it.
    Deferral (sigmoid ≥ 0.1) and PG (q1 + q2 ≥ logit 0.25) then both move consistently, without changing the
    ranking (AUC) or the thresholds.
  * The shift is set so that the model defers rm4t's share of all rules in the test logs, using no labels.
  * rmshift.py (23:08), on 60 test logs: rm4t defers 29.6% of all rules at 0.1. Shifts to match:

| model | unshifted | shift |
|---|---:|---:|
| rm9a | 5.8% | −1.121 |
| rm9f | 13.1% | −0.630 |
| rm9g | 14.5% | −0.685 |
| rm9h | 19.7% | −0.369 |

  * The LightGBM text's `tree_sizes` header has to go, as the leaf values change size. The check gives the exact
    shift on 5 logs.
  * Arms (23:10): rm9aC and rm9fC. rm9gC and rm9hC follow when the control and rm9a arms end
    (abs/rm9calarms.sh). To make room, the rm9b arm (+7 −23 on 246) and the rm9c arm (+5 −10 on 171) were stopped
    at 23:10; their rows stay.
* **The control ended at 23:30: rm4t proves 202 of 400 at 20 s (2.45 CPU h).** Against it at 23:30:

| model | goals | + | − |
|---|---:|---:|---:|
| rm9a | 335 | 11 | 27 |
| rm9aC (rm9a shifted) | 76 | 1 | 7 |
| rm9b (stopped) | 253 | 7 | 23 |
| rm9c (stopped) | 181 | 6 | 12 |
| rm9e | 272 | 9 | 19 |
| **rm9f** | 246 | **9** | **5** |
| rm9fC | 91 | 2 | 2 |
| rm9g | 156 | 4 | 6 |
| **rm9h** | 106 | **5** | **1** |
| rm9i | 27 | 1 | 0 |

  * The weighted models (f, h, i) gain, the unweighted ones lose.
  * The calibration shift has not helped rm9a so far (76 goals), so the deferral share is not the whole story. The
    weighted models rank differently.
* **ul72 (23:30, production rows from 183,986) = ul71 + m9f@0, m9h@0, m9i@0**, J=8.
* **20 Nov 00:54: the full arms.** rm4t 202 of 400 (2.45 CPU h), rm9f 204 (+16 −14, 2.63 CPU h), rm9a 184 (+15 −33,
  3.20 CPU h). On the 131 goals every arm had then run, the union of all arms proves 94 against the control's 88.
* **The calibration shift does not help; it hurts or is neutral:**

| shifted model | goals | + | − | unshifted at that time |
|---|---:|---:|---:|---|
| rm9aC | 274 | 4 | 29 | rm9a +15 −33 on 400 |
| rm9fC | 315 | 8 | 14 | rm9f +16 −14 on 400 |
| rm9gC | 226 | 7 | 8 | rm9g +10 −19 on 308 |
| rm9hC | 131 | 3 | 3 | rm9h +11 −9 on 292 |

  * Pruning as much as rm4t does not make the new models better; the weighted models gain by their ranking. The
    shifted arms were stopped at 00:54; their rows stay.
  * Production back to J=12 at 00:55 (rows from 188,375; earlier log loops/UL72a.log).
  * At the restart, ul72 had 41 proofs in 4.0 CPU h since 23:30 (34 of them L0, over many originals), against about
    0.5 per CPU h before. m9f@0 had 1 proof in 0.58 CPU h; m9h@0 and m9i@0 none in 0.6 each.

## Final paired result (20 Nov 02:12)

All arms on all 400 goals, fresh 20 s each, as of each goal's proof:

| model | proved | + | − | CPU h | unique among all arms |
|---|---:|---:|---:|---:|---:|
| rm4t (control) | 202 | | | 2.45 | 7 |
| rm9a (production's logs) | 184 | 15 | 33 | 3.20 | 0 |
| rm9e (2 longest proofs per goal) | 181 | 15 | 36 | 3.59 | 2 |
| **rm9f (rm9a's data, Suda's weighting)** | **204** | 16 | 14 | 2.63 | 0 |
| rm9g (rm9a's data, 255 leaves) | 187 | 13 | 28 | 3.24 | 0 |
| **rm9h (2 longest, weighting)** | **203** | 14 | 13 | 2.77 | 1 |
| **rm9i (weighting, 255 leaves)** | **204** | 17 | 15 | 2.72 | 0 |

* **Union of all arms: 226 of 400, against rm4t's 202 (+12%).**
* **Greedy cover (exp/mqcmp.py):** rm9f 204, then rm4t +14, rm9e +5, rm9h +2, rm9a +1, then rm9i and rm9g +0 (226).
  rm9f and rm4t together prove 218.
* **Reading:**
  * Suda's per-run weighting is what makes a retrained model pay: all three weighted models match or beat rm4t.
    The unweighted ones lose 18-21 goals, even rm9g with bigger trees.
  * The models are complementary. Each weighted model has 13-15 goals rm4t lacks and loses about as many.
  * rm9e is a weak model alone (181) but the third in the cover. Its training on long proofs makes it different.
* **Members (portfolio rule):** m9f, m9h, m9e and m9a add proofs in the cover. m9i adds none (it proves the same
  goals as rm9f) and had 0 in its 1.0 CPU h exploration, so it is dropped. ul73: ul72 − m9i@0 + m9e@0.
* **Not yet known:** whether two models at 20 s beat one at 40 s. Time-matched control: rm4t at 40 s on the same
  400 (loops/MQ_rm4t_40). If it proves fewer than 218, an L0 run with a second model is worth more than a longer
  rm4t run.
* **The time-matched control, final (20 Nov 07:20, loops/MQ_rm4t_40):** rm4t at 40 s proves **225 of 400** in 5.09
  CPU h. rm4t and rm9f at 20 s prove 218 together in 5.08 h. 14 goals are proved only at 40 s, 7 only by the pair;
  all three runs prove 232. So at equal CPU, twice the time for one model beats two models by 7 (3%), and both
  have goals of their own. For production: keep the members (portfolio rule), and the longer single-model runs (the
  40 s chain level) deserve their share too. At 225 goals the order had been the other way (147 against 149), so
  this difference is about the size of the noise.
* **ul73 at 02:17** (production rows from 196,111, J=12), and the rm4t 40 s arm at 02:17. CPU: production 12, the
  climber 4, the transfer loop 2, the arm 1.

## Production's burst of 19-20 Nov was the transfer loop, not a model

* My count at 23:30 ("ul71: 10 proofs in 13 CPU h") was wrong. ul71 made 454 proofs in 11.8 CPU h (375 at L0),
  and production made 783 new proofs from 22:20 to 02:13. On 19 Nov it made 1,986 in all.
* **The trigger (22:20):** L1 (40 s, the chain hints of the 10 nearest proven siblings: 269 hints) proved
  aK2_eq_aK3_1243b goal 506. Four 5 s members with about 6,800 pool hints had failed on it. Its siblings 507-518
  followed within 2 minutes.
* **At 22:23 the transfer loop** (loops/XFL, transfer.py live, every 300 s) found 22 unsolved goals of other
  originals that are steps of those proofs (same or weaker axioms). It proved all 22 in 24 s and wrote them to
  production's solved.tsv with time 0. production's log shows synced 2 → 24 at that point.
* Each transferred goal then started sibling chains in its own original. The transfer loop kept feeding:
  28, 17, 19, 19 new candidates in the next 20 minutes.
* So the big gains come from chain reactions across originals: one hard proof, its siblings, the transferred steps,
  their siblings. The rule models act inside single runs.
* Unsolved: 3,733 of 51,784 at 02:13.
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

## rm10f: rm9f's recipe on all data (20 Nov 03:49)

* abs/rm10.sh: rulemodel.py `--all`, with no held-out goals. It trains on the 400 test logs and every production proof
  since 19 Nov 19:50: 22,163 logs against rm9f's 21,143.
* The same data sources, 150 negatives per log, Suda's weighting, rm9a's frozen vocab. 3 threads, 3 feature workers.
* As in Mizar60's deployment, the retrained model would replace m9f@0 as m10f@0. It has no held-out test; the replay
  measured the recipe.

# ENIGMA in twee: a learned filter on new rules

*Reconstructed on 17 Nov from REPORT 2b, commits 1189d04–ff4c1c6 (12 Nov 20:56–23:01) and the session's
commands. CPU-time limits (before abstract time), so differences of a few problems are noise.*

**Question.** The user, 12 Nov 20:35: "you may also look at the various ENIGMA featurizers — they got pretty
advanced in the latest versions". Can an ENIGMA-style model of which rules end up in proofs guide twee, with
or without hints?

**Setup.**
* **Features:** a port of E's "enigmatic" featurizer (ai4reason `enigma` branch, `che_enigmaticvectors.c`)
  to unit equations:
  * vertical walks of length 2–3 from the `=` root, variables as `*`;
  * horizontal features `f.head(arg1)...`;
  * symbol counts and maximal depths;
  * length statistics;
  * a separate block for the conjecture;
  * rule–goal overlap counts and log(rule number).

  Python (enigfeats.py) and Haskell (src/Twee/Enigma.hs) compute the same features; on test rules twee's raw
  scores equal LightGBM's exactly.
* **Labels:** `--print-given` logs every rule added. given.py labels a rule 1 if it is a proof lemma, 0
  otherwise, and −1 for axioms.
* **Data and models:**
  * rm1: dev10's round 0 (given/r0: 1,771 runs; 26.7k positive and 605k negative rules) on the 7 originals
    other than the held-out aa1_45_c, mbol_com and nil3_15. Command: `rulemodel.py given/r0 --ntest 300`.
  * rm2: + 30 more originals. sets/tr30 is the train.names problems of 30 originals drawn with seed 7 from
    those not in dev10: 12,414 problems, 7,059 solved at 2 s by given.py with twee-e5 (given/tr30).
  * rm3 (for the holdout run, 2026-11-12-holdout.md): given/tr30 + given/r0 without any holdout problem
    (given/train_only, 12 Nov 21:28).
* **In twee** (`--rule-model M --rule-vocab V --rule-goal G`): a critical pair about to become a rule is
  scored. Below the threshold it goes back into the queue once, its score times the penalty (default 2).
  Hint-boosted pairs come back at once, since their scores are tiny.
* **Test "345":** sets/ho3_unsolved, the goals of the 3 held-out originals that plain twee leaves unsolved at
  2 s (from dev10_unsolved_r0), run at 8 s, -j 10. Goal files: `rulemodel.py goalfiles`.
* **Tuning "dev":** all 818 goals of the same 3 originals, at 2 s, rm2.

**Results.**

On the 345 at 8 s:

| system | solved |
|---|---:|
| twee, no guidance | 42 |
| hint loop, all rounds (2 s ×3 + 8 s) | 46 |
| rm1, threshold 0.1 | 57 |
| rm1, threshold 0.2 | 40 |
| rm1 + kNN hints (100) | 68 |
| rm2 + kNN hints, threshold 0.1 / 0.2 | 65 / 69 |
| rm2 + kNN hints + ProofWatch F = 0.3 | 67 (+2 −4 against 69) |
| union of all runs | 93 |

Tuning on dev (818 goals, 2 s, rm2):

| setting | solved |
|---|---:|
| plain | 473 |
| threshold 0.1, penalty 2 | 498 (+27 −2) |
| threshold 0.1, penalty 3 | 499 (+29 −3) |
| threshold 0.2, penalty 1.5 / 2 | 490 / 488 |
| threshold 0.05, penalty 2 | 488 |
| threshold 0.5, penalty 1.2 | 476 |

Offline on the 3 held-out originals (253 problems):
* rm1: AUC 0.969. At 0.1 it keeps 97.9% of proof rules and rejects 68.5% of the others; the rules up to
  the proof shrink to 36%.
* rm2: AUC 0.975. At 0.1 it keeps 99.5% and rejects 61.6%.
* Parent features: AUC 0.971 against 0.969, so they were left off.

**Fixes found on the way.** These came from the first holdout loop H1 (rm3, 0.2, penalty 2, text model),
which lost 123 problems plain twee solves, many in under 0.1 s:
* Loading the text model took 0.25 s per run (Haskell `read` on about 100k numbers). lgb2bin.py writes a
  binary forest: it loads in 0.07 s, with identical predictions.
* The same equation, reached through different pairs, was deferred up to 18 times. Each equation is now
  deferred at most once.
* Then a dense feature array and hashed feature names (FNV-1a) brought the model's overhead to about 6% of
  throughput.

**Reading.**
* The model is worth more than hints at 8 s (57 against 46), and the two add up (68).
* The model fails on a theory unlike its training originals: mbol_com got 0 with it against 4 without, and
  more training originals did not fix that (0–2).
* The threshold behaves differently offline and online: 0.2 was worse than 0.1 with rm1 and better with
  rm2 + hints. With differences of 2–4 at CPU limits, the choice between them is noise.
* The tuning set holds 22 of AIM60k's holdout problems (late goals moved out of training originals), and
  rm1's dev10 data includes two whole holdout originals; see 2026-11-12-holdout.md.
* ProofWatch as set up here (a hint's factor eases from 0.3 to 0.01 as its source proof gets matched) did
  not help.

**Decision and next.** Threshold 0.1, penalty 2, binary model. The model is retrained later on more and
harder proofs (rm4t, REPORT 2ad). REPORT 2b.

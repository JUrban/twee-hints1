# Semantic guidance, offline: are proof steps false in relevance models? (20 Nov)

Written 20 Nov 2026, 12:14 UTC, at launch.

## Question

* Slaney's SCOTT and later semantic guidance in Otter and Prover9 prefer clauses that are false in a chosen model.
  Such clauses cannot follow from the axioms that model satisfies, so they use the rest.
* Here every original is the 17 base axioms (loops with the inner mappings, and AIM) plus 0–11 extra axioms. A
  **relevance model** is a finite model of the base axioms in which some extra axiom fails. A rule derived in the
  full theory that is false there depends on the extras.
* **Hypothesis:** proofs need the extras, so proof steps are more often false in relevance models than the other
  given rules. If so, that falsity is a feature the syntactic rule model lacks, and twee could compute it per rule.

## Method

* **exp/semguide.py:**
  * models: for each original with extras, Mace4 with the base axioms as assumptions and the conjunction of the
    extras as the goal; up to 10 models, sizes 2–8, 30 s;
  * data: 10 random given logs (seed 1) of its solved goals, from loops/UL/given, the rule model's training logs
    (label 1: a proof step, 0: a given rule not in the proof);
  * measure: each rule is checked against the models (numpy, at most 500k cells). Reported per original and in
    total: false proof steps over all, false other rules over all, and P(step | false) / P(step | true).
* **First look, aK2_eq_aK3_s** (one extra axiom, the anti-automorphic inverse property; 10 models): 94 of 551 proof
  steps are false in a model (17%), against 5,628 of 23,335 other given rules (24%). That is the wrong way round.

## Commands

    python3 exp/semguide.py loops/SEMG --logs 10 --models 10 -j 2

## Results (12:36)

* **Relevance models:** 62 of the 116 originals with extras have some, 10 each (620). For the other 54, the extras
  hold in every model of the base up to size 8, or Mace4 found none in 30 s.
* **Over the 62:** proof steps are false in a relevance model 36,301 of 111,964 times (32.4%); the other given rules
  495,783 of 1,629,586 times (30.4%). **P(step | false) / P(step | true) = 1.09.**
* **By original:** proof steps are false clearly more often (by a factor of more than 1.2) in 18 originals, and
  clearly less often in 11. The strongest enrichments:

  | original | proof steps false | other rules false |
  |---|---|---|
  | ns_to_aa1_b | 32.2% | 19.1% |
  | gbol_to_aK1 | 44.2% | 31.4% |
  | gbol_to_osb | 43.8% | 32.4% |
  | ns_to_aa1_c | 41.2% | 27.4% |
  | mbol_com | 78.0% | 62.9% |

  On the other side: aK2_eq_aK3_s 17% against 24%, raa2a 11% against 15%.
* **Reading:** proofs need the extras, but so does most of what the search derives from them. A run's given rules
  are mostly consequences of the extras too, so falsity there hardly separates steps from the rest. A proof must
  contain at least one step false in each model of the base where the goal fails. That is one step in a hundred, too
  few to move the rates.
* **Decision:** not worth evaluating models per rule inside twee for a lift of 1.09. Closed as a weak negative. A
  per-original feature for the rule model (the falsity bit, with the original's own lift learned) stays possible.
  The 18 enriched originals are where it could pay.

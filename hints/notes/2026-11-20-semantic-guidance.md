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

## Results

(pending)

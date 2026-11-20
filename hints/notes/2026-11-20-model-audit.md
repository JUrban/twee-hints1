# Soundness audit by finite models (20 Nov)

Written 20 Nov 2026, 10:54 UTC, at launch.

## Question

Are there unsound proofs in production besides the p9twee negation bug's
([notes/2026-11-20-p9-negation-bug.md](2026-11-20-p9-negation-bug.md))? The trust fixpoint takes everything before
15 Nov 08:56 on faith and only follows that one bug. A check independent of every proof path is needed.

## Method

* **exp/modelcheck.py:**
  * 68 distinct theories (axiom sets) over the 129 originals;
  * for each, Mace4 (`/project/bin/mace4`) finds up to 40 models of sizes 2 to 8 in at most 120 s;
  * every step of every solved unit goal's proof (production's hints file) is evaluated in each model, under all
    assignments of its variables (numpy, at most 2M cells per model).
* A step that fails in a model of the axioms is not a theorem, so the proof that logged it is not a proof. It may
  also have used an unsound lemma axiom.
* The steps of conditional goals' proofs may use the hypothesis, so they are skipped.
* **Self-tests:**
  * on one theory, the axioms hold in all 40 models, and commutativity and x·x = e fail in some;
  * in the run, every AIM60k goal statement (a step of a real proof, so a theorem) must hold in every model. A
    failure there means a bad model or evaluator.
* The check is one-sided: a false step can hold in all the small models. Commutativity and x·x = e, the false facts
  of the p9 bug, both fail at sizes 4–6.

## Commands

    python3 exp/modelcheck.py loops/MODELCHECK -j 3

Outputs:

* loops/MODELCHECK/models/<theory>.out
* false_steps.tsv
* false_goals.tsv
* false_step_goals.txt

## Results

(pending)

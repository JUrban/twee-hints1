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

## Results (done 11:17)

* **68 theories, 2,504 models** (13 to 40 each; every theory has some), **2,400,297 step checks** (unique steps per
  theory, each solved unit goal's hints file).
* **Self-test:** 0 of the AIM60k goal statements fail in a model.
* **217 false steps, in 71 goals.** All 217 have different variables on the two sides, e.g. `X0 = X1` (15 times),
  `X0 = m(k(X1,X2),rd(X3,m(X2,X3)))`, `m(r(X0,X1,X2),X3) = m(r(X0,X1,X2),...)`.
  * 191 have a side that is a bare variable not on the other side.
  * They are printed goal terms, not derived equations. In aa1_45_b__goal_301 the first hints line is
    `X0 = m(k(X1,X2),rd(X3,m(X2,X3)))`, the goal's left side with a fresh variable.
  * As hints they are harmless: twee matches hints by variant.
  * As axioms or rewrite rules they are false. The live path from hints to axioms was exp/stepjoin.py, now
    filtered: each step axiom must hold in the models. All 64 step axioms of its 23 proofs hold. loop.py
    `--hint-axioms` has been used only in hax.sh (14 Nov, REPORT 2s), not in production.
* **No false step with the same variables on both sides**, which is the shape of a wrong derived equation.
* **Positive control:** the hints of the 16 quarantined unsound Prover9 proofs. 13 of 16 have a same-variable false
  step, e.g. `ld(X0,e) = X0` (every inverse equal to itself) and `rd(e,X0) = X0`. The other 3
  (aK2eq_1234__goal_392, aK2_eq_aK3_j__goal_425, nil3_23_32_to_28__goal_401) show none in their hints.
* **Verdict:** with this check's recall on known-bad proofs (13 of 16), production's 48k unit-goal proofs show no
  sign of another unsoundness. Conditional goals' proofs and false steps that hold in all small models stay
  unchecked.

## Routine (12:37)

* exp/modelcheck.py writes OUTDIR/alarm.tsv: the false steps with the same variables on both sides, the shape of
  a wrong derived equation. It prints an ALARM line if there are any.
* abs/auditlive.sh (exp/auditlive.sh) runs the audit every 6 hours into loops/AUDIT/<stamp>, reusing the models,
  from 15:37 (pid in loops/AUDIT.pid). It costs about 15 minutes on 3 CPUs.


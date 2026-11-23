# Model audit, second pass: production's proofs since 20 Nov

Written 23 Nov 2026, 02:49 UTC, at the launch.

## Question

Does every proof step of production's solved unit goals still hold in finite models of its theory? The first audit
(notes/2026-11-20-model-audit.md, 20 Nov 10:54-11:17) found no false goal and no wrong derived equation: its 217
false steps in 71 goals were all printed goal terms with different variables on the two sides. Production has since
added proofs from new paths (the derived-rule transfer with `--lemma-ax`, the head class, the given-rule retry), so
the check runs again on all of production's proofs.

## Setup

* `exp/modelcheck.py loops/MODELCHECK2 -j 2` (nice 10, CPUs 21-27,49-55, production's set), after the realproofs
  packing ends; loops/MODELCHECK2/models is a copy of the first audit's Mace4 models (the same theories, cached).
* Input as before: loops/UL/solved.tsv and loops/UL/hints (production's proofs), up to 40 models of sizes 2-8 per
  theory.
* Log loops/MODELCHECK2.log; outputs false_steps.tsv, false_goals.tsv (self-test), alarm.tsv.

## Reading

The number of false goals (self-test, must be 0), false steps and their goals against the first audit's 217 in 71,
and any alarm (a false step with the same variables on both sides: a wrong derived equation).

## Result (03:32)

Run 03:09:10-03:31:33. `modelcheck: 2504 models, 2442229 steps, 0 skipped, 0 false goals, 217 false steps, 0 theories without models; 71 goals with a false step`

* False goals (self-test): 0. Alarms (a false step with the same variables on both sides): 0.
* False steps: 217 in 71 goals, the same set as the first audit's (all printed goal terms with different variables on the two sides).
* Production's hints newer than the first audit (20 Nov 11:16): 378. None of them has a false step.
* The audit reads loops/UL's solved list and proofs. Production syncs every loop's proofs into it: all 48,372 goals
  of the 22 Nov 21:39 trusted list are there (and 4 more that are not trusted), so the audit covers every trusted
  unit goal.

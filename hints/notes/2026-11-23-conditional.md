# Conditional proofs of the unsolved goals: hard steps or blocked ones? (exp: COND1)

Written 23 Nov 2026, 05:00 UTC, at the launch.

## Question

The 3,412 goals not in the trusted list (22 Nov 21:39) sit in the tails of 93 of the 129 originals, mixed with
solved ones (in 90 of the 93 the tail from the first unsolved goal has solved goals too). AIM60k's goals are steps of
Prover9's proofs, so each is true and follows from the steps before it. Is an unsolved goal hard in itself (twee
cannot bridge it even from its predecessors), or only blocked (it falls once some unsolved predecessors are given)?
If most are blocked by a few, those few are where long runs should go, ranked by how many goals they unblock; if most
are hard steps, the frontier has no such keystones.

## Setup

* exp/condprove.py, run by abs/cond1.sh (exp/cond1.sh), 6 threads, into /project/hintwork/cond/COND1, outside
  loops/: no loop, proofq, trust.py or the packer reads it, so no conditional proof reaches production or the totals.
* Each unsolved goal (sets/all minus loops/TRUSTNOW/t2139.trusted) with its 10 nearest earlier goals of its original
  as axioms lemma_goal_J, proved or not (lemmas.lemma_problem with every goal counted), and the 30 nearest trusted
  goals by kNN (lemmas.LemmaIndex, subsets) as lemma_knn_I_<goal>.
* One plain /project/bin/twee-pg61 run: --max-time 5 --abstract-time 2000 --no-resume-requeue --no-eqhint-consider,
  --quiet --no-proof; no rule model, no hints. A proved run is rerun with the proof printed (COND1/proofs/<goal>); its
  used lemma_goal_J split into unproved and proved.
* Smoke (12 random unsolved goals, 05:00): 3 proved, each using unproved siblings (goal_524; goal_272; 468, 473, 475).

## Readings

* Hard steps: no proof even with the predecessors assumed (at 5 s, plain).
* Blocked: proved using unproved siblings; the blockers, and a goal's reach through the blocking graph.
* Unconditional: proved using no unproved sibling (a new proof; checked by hand before anything uses it).

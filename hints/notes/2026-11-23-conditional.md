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
* One plain twee run: /project/bin/twee-pg61 with TWEE_PG_ARGS unset, so twee-e61 without production's PG threshold
  and ground-joining branch limit; --max-time 5 --abstract-time 2000 --no-resume-requeue --no-eqhint-consider,
  --quiet --no-proof; no rule model, no hints. A proved run is rerun with the proof printed (COND1/proofs/<goal>); its
  used lemma_goal_J split into unproved and proved.
* Smoke (12 random unsolved goals, 05:00): 3 proved, each using unproved siblings (goal_524; goal_272; 468, 473, 475).

## Readings

* Hard steps: no proof even with the predecessors assumed (at 5 s, plain).
* Blocked: proved using unproved siblings; the blockers, and a goal's reach through the blocking graph.
* Unconditional: proved using no unproved sibling (a new proof; checked by hand before anything uses it).

## Result (05:26; COND1 ran 05:00:45-05:23:10)

exp/condgraph.py cond/COND1 (exp/condgraph.py adds the Prover9 proof-line gap from abs/goal_lines.tsv):

* **3,412 unsolved goals: 2,826 hard (83%), 585 blocked (17%), 1 unconditional.** Most unsolved goals
  are hard steps: even with their 10 earlier siblings given, a plain 5 s run does not bridge them.
* The blocked goals' blockers, by class: hard 843, blocked 285. Unproved siblings used per blocked goal: 1: 293, 2: 143, 3: 89, 4+: 60.
  354 blocked goals have only hard blockers.
* **No keystones.** Reach (blocked goals that fall, to a fixpoint, once one goal is proved): hard goals >=1 184, >=5 5, >=20 0; the top 10: [10, 7, 6, 5, 5, 4, 4, 4, 4, 4];
  blocked goals >=1 58, >=5 3, >=20 0; the top 10: [7, 6, 5, 4, 3, 2, 2, 2, 2, 2]. All hard goals proved would free the 585 blocked ones, and no single goal frees more than 10.
* **The hard steps are the long ones.** AIM60k samples each Prover9 proof every 3 lines at first, then every 5, 8,
  13, 21, 34 and 55 (REPORT 2z); every unsolved goal is 8 or more proof lines after the previous goal. Proved
  (blocked or unconditional) by lines from the previous goal: 0-1: 0/0; 2-3: 0/0; 4-7: 0/0; 8-15: 58/177 (33%); 16-31: 107/451 (24%); 32-: 421/2784 (15%).
* Hard goals by original, the top 10: nslm_to_aa1 354, nsmr_to_aa1 168, R1dist_to_aa1 111, aK2_eq_aK3_a 82, aK2_eq_aK3_gen 82, aK2_eq_aK3_d 75, com_Ralt 74, ns_to_aa1_b 74, nsmr_to_aK1 73, aK2_eq_aK3_b 68.

| goal | class | reach | blockers |
|---|---|---:|---|
| com_Ralt__goal_254 | hard | 10 | - |
| com_Ralt__goal_338 | blocked | 7 | 331,335 |
| im2_24_to_25__goal_471 | hard | 7 | - |
| com_Ralt__goal_261 | blocked | 6 | 254 |
| nsmr_to_aa1__goal_738 | hard | 6 | - |
| aK2_eq_aK3_j__goal_430 | hard | 5 | - |
| nil3_1K_e__goal_466 | hard | 5 | - |
| nil3_23_32_to_26__goal_502 | blocked | 5 | 495,496 |
| aK2_eq_aK3_h__goal_316 | hard | 4 | - |
| aK2_eq_aK3_j__goal_457 | hard | 4 | - |
| nil3_23_32_to_26__goal_510 | blocked | 4 | 502 |
| nil3_32__goal_466 | hard | 4 | - |
| nslm_to_aa1__goal_1013 | hard | 4 | - |
| nslm_to_aa1__goal_964 | hard | 4 | - |
| nsmr_to_aa1__goal_706 | hard | 4 | - |
| KK_Kcom_to_aK1__goal_284 | hard | 3 | - |
| aK2_eq_aK3_1243b__goal_588 | hard | 3 | - |
| aK2_eq_aK3_gen__goal_539 | hard | 3 | - |
| aK2_eq_aK3_gen__goal_616 | hard | 3 | - |
| aK2_eq_aK3_o__goal_493 | hard | 3 | - |

* **The one unconditional proof**, nil3_30__goal_473 (2.05 s; siblings 464 and 468, both trusted, and 9 kNN lemmas of
  trusted goals; cond/COND1/proofs/nil3_30__goal_473), is a goal production never proved. loop.py does not reproduce
  it: abs/cu2.sh (exp/cu2.sh) in the trusted context (loops/ULT.ctx: the 48,372 trusted goals as round 0, hints ->
  loops/UL/hints), the same 10 sibling and 30 kNN lemmas, plain twee, no rule model, 5 s: NO, with 8,504 hints, which
  COND1's run did not have. (abs/cu1.sh took --init loops/UL, which imports only round-0 rows, 33,720 goals; abs/cu3.sh
  with --max-hints 0 ran nothing.) Not entered into production: one goal, and it has no loop record for trust.py.
* A smoke check on 9 of the hard goals at 40 s (instead of 5 s), the same problems: 1 proved.

## Decision

No keystone targeting: the frontier is about 2,800 hard steps, 2,784 of the 3,412 unsolved goals 32 or more Prover9
proof lines after the previous goal, and none frees more than 10 others. "Hard" here is at 5 s, plain twee, without
the rule model, hints or variants; with those some would fall from their siblings, but that does not make keystones
of them. Progress there needs stronger single-step proving (longer runs, better lemmas and hints
for one step), not a different order. COND1's proofs stay in cond/COND1, outside loops/.

# Learning the lattice moves of the climber

*Reconstructed on 17 Nov from REPORT 2ak (15 Nov 23:00 – 16 Nov 04:30). Live climber on production's stalled
goals; abstract time per run.*

**Question.** The user, 15 Nov: "what are the best steps in the lattice given a problem". The climber walks a
lattice of (assumptions, goal) nodes, with a hand-fixed order of moves. Can a learned policy pick better moves,
and better stronger theories?

**Setup.**
* **Data:** climb.tsv of the FUDs arm and the live climber (1,346 moves on 100 targets at first; 5,714 moves on
  478 targets by 16 Nov 01:00). latticedata.py makes one row per move (features shared with climb.py,
  `move_features`).
* **Labels:**
  * nontrivial: proved, an assumption used, at least 30 steps;
  * credit: the share of the target's real proof found in the sketch (only for proved targets);
  * realized: the share of the sketch's steps the real final run derived (Korovin's concretisation).
* **Policy:** latticepolicy.py, logistic, split by target. `climb.py --move-model M` samples moves by softmax
  (`--move-temp` 1, `--move-eps` 0.1).
* **Theories:** `--theory-explore 2` offers random others; `--theory-ts` uses Thompson sampling with a Beta
  posterior of each theory's nontrivial rate (prior Beta(0.4, 1.6)).
* **Tests:**
  * abs/fam4.sh (the next 24 unsolved 1243b goals, policy lattice1 against the fixed order);
  * live A/Bs by crc32 bits of the target name (abs/clu2.sh: move policy; abs/clu4.sh: theory sampling);
  * `--reclimb-heads 4` (abs/clu5.sh, 02:22).

**Results.**

| move (assumption kinds) | moves | proved | nontrivial |
|---|---:|---:|---:|
| theory + siblings + kNN | 552 | 43% | 9% |
| siblings + kNN, weaker goal | 203 | 100% | 11% |
| theory + siblings + kNN, weaker goal | 139 | 100% | 11% |
| siblings + kNN | 116 | 30% | 16% |
| theory + kNN | 71 | 52% | 41% |
| kNN | 61 | 51% | 25% |
| kNN, weaker goal | 53 | 100% | 40% |
| siblings only | 45 | 4% | 0% |
| theory only | 43 | 28% | 28% |

* Policy on nontrivial: held-out AUC 0.654 at 100 targets, 0.757 at 478 (models/lattice2n.json).
* Realization overrates weaker goals (0.5–0.76: their steps are theorems of the real theory). Where credit and
  realization both exist they agree (0.96 over 18 sketches).

| offered theories | moves | proved using an assumption | nontrivial |
|---|---:|---:|---:|
| the heuristic's (similar solved goals) | 625 | 50% | 20% |
| random others | 152 | 73% | 36% |

* fam4: 1 of 24 for the policy (goal 455) against 1 of 24 for the fixed order (the same goal).
* Live A/B after 205 climbs: 3 proofs, no difference (p = 0.60 and 1.0).
* Heads: 8 proofs in the next 150 climbs, then 2 in 213. The theory bit split 0 against 8 (p = 0.007), but
  targets without stronger theories split 0/21 against 3/25, and three of the 8 were one chain.

**Reading.**
* The policy's signals are real offline: siblings hurt, a stronger theory with kNN goals and no siblings helps
  most, and random theories beat the similarity ranking.
* **Online nothing is measurable.** At a 1.5% proof rate, a 2× gain needs more than a thousand climbs per arm.
* **Two of my readings were wrong.**
  * The heads burst was not the heads' doing: 3 of its 8 proofs were heads, and heads had half the slots.
  * "First unsolved" is not the tail head: in 109 of 111 originals later goals are proved past it, so
    `--reclimb-heads` targeted holes.
* Proofs cluster by original, so tests should count originals, not targets.
* The yield follows the supply of targets whose context changed (chains, production's new proofs), not the
  ordering.
* A bug in the exploration code stopped the climber from 00:02 to 00:19; failed climbs are now logged as ERROR.

**Decision and next.** The policy and theory sampling stay in the live climber as A/Bs. No conclusion; the climber
was later stopped (REPORT 2an). REPORT 2ak.

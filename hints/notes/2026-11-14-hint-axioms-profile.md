# Frequent hints as axioms, a false hint in old pools, where twee's time goes, and the rule penalty

*Reconstructed on 17 Nov from REPORT 2s–2t (14 Nov morning). Abstract time.*

**Questions.** If some hints are right half the time (those from 20+ sibling proofs, REPORT 2o), do they help
more as axioms? Where does twee spend its time in a full-configuration run? Do larger deferral penalties
help?

**Setup.**
* `loop.py --hint-axioms K:F`: the K most frequent pool hints that occur in at least F sibling proofs go
  into the problem as axioms. Pool hints are consequences of the axioms and proven lemmas, so this is sound,
  given that the pools hold no false hints.
* Test: nil3_31, the first 150 unsolved goals, 20 s, 6 sibling lemmas (baseline 76).
* Profile: twee-e22 built with `-f profile` (Twee.Profile switched to GHC's monotonic clock from rdtsc). One
  failing nil3_1K goal, 20 abstract s (40k pairs), full configuration.
* Penalty: the same 150 nil3_31 goals with penalty 2, 5 and 20.

**Results.**

| hint axioms | solved |
|---|---:|
| none | 76 |
| 10, each from ≥ 20 proofs | 72 (+1 −5) |
| 45, each from ≥ 10 proofs, all verified as theorems | 73 (+3 −6) |

The first 45-axiom run solved all 150 in 28 s. One of its "hints" was `X0 = X1`, in 1,422 hint files of
loops/V2base and so of loops/UL. These were proofs of conditional goals made before the HINTS-HYP fix
(twee-e14), where the hypothesis was logged as a hint with its skolems generalised.

Profile, share of time without the profiler's overhead:

| phase | share |
|---|---:|
| making critical pairs (6,115 new rules against the active set) | 51% |
| … of which normalising both sides of each new pair (8.2M simplify calls) | 41% |
| considering the 27k dequeued pairs | 22% |
| the rest | 27% |

* Without hints or the model the same run takes 67 s against 49–53 s: the model keeps fewer rules, which
  saves more than it costs.
* Hint matching and given-rule logging cost about 8%. Limiting ground joining changes nothing.

Penalty: 2 solves 76, 5 solves 77, 20 solves 75; wall time the same.

**Reading.**
* High-precision hints are better as hints. As axioms they add critical pairs from the start and crowd the
  search.
* **The false hint was a soundness risk only as an axiom.** As a hint it was harmless: twee matches by
  variant, so `X0 = X1` only matches the pair `X = Y`. `--hint-axioms` now takes only proofs of
  unconditional goals, and the 45 top nil3_31 hints from those each prove from the axioms in under 10 s.
* The old pools still hold such false generalised hypotheses as wasted entries. This also matters for the
  17 Nov expansion (2026-11-17-expanded-proofs.md): expanded hint sets inherit them, which is harmless for
  hints and would not be for axioms.
* **The cost per abstract second grows with the square of the number of rules.** Twee normalises every new
  pair at creation. This later motivated the parental filter (2026-11-17-pg-sum-filter.md), which skips
  pairs before normalisation.

**Decision and next.** No hint axioms; penalty 2 stays. REPORT 2s, 2t.

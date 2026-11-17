# Conjecture cuts, generated and oracle

*Reconstructed on 17 Nov from REPORT 2ai (15 Nov evening). Abstract time.*

**Question.** The user, after IWIL 2026: Chvalovský, Suda and Urban prove generated conjectures separately and use
them as cuts (+582 of 11,881 hard or unsolved Mizar60 problems, the first useful conjecture at median rank 3).
Does that work in twee on AIM?

**Setup.**
* `loop.py --gen-cuts K` (1128103), before a goal's resumed level:
  1. gencopy.py (`--counts`) samples equations from the goal and the failed level's last 256 rules;
  2. the K most often sampled, minus variants of the goal, become candidates;
  3. one `twee --multi-goal` run of `--gen-cut-time` abstract s tries them on the goal's axioms, lemmas, hints
     and model;
  4. those proved after at least one considered pair become axioms of the resumed level.
* `--gen-cut-sep` proves each cut in its own run, with the cut's own kNN lemmas and goal block.
* cutoracle.py gives oracle candidates: rules of the goal's later production proof.
* sets/cut9: 9 gen200 goals production proved later (in 5–128 s). Snapshot ULsW, fresh 5 s then resume +15 s.

**Results.**

| arm | cuts proved | goals proved |
|---|---:|---:|
| control, +15 s | – | 1/9 |
| control, +20 s | – | 1/9 |
| oracle, 40 rules spread over the proof, one shared 5 s run | 14–27 of 40 | 1/9 |
| oracle, the 40 nearest the goal, shared | 2–22 of 40 | 1/9 |
| oracle, the 20 nearest, each alone with its own guidance | 3–15 of 20 | 1/9 (7.3 s against 21.5 s) |
| generator gc1_4000, top 40, shared (3 goals) | 0 of 120 | 0/3 |
| generator, top 10 at T 0.7, each alone | 8 of 90 | 1/9 |

Separate runs prove 69 of the 20-nearest oracle rules against 35 shared (34 only there), at 20 runs instead of
one.

**Reading.**
* A shared cut run is uninformative: twee's completion barely depends on the goal, so a cut proved on the goal's
  own problem is in the state of its own failed level. E and Vampire are goal-directed, so there a separate cut
  proof searches elsewhere.
* Even oracle cuts gain nothing at this budget. The proofs are 110–700 rules long, and the cuts that can be
  proved are the easy part.
* **AIM60k already has the strong form of cuts:** its goals are Prover9's intermediate goals, and the sibling
  lemma chain imports them once proved. That is the oracle cut mechanism, and the loop's largest gain. It is
  also why the totals are lemma-assisted (2026-11-17-lemma-circularity.md).
* 9 goals: this rules out a large effect, not a small one.

**Decision and next.** Not pursued. Mid-run cuts have the same limit: only a cut proved by a differently guided
search adds information. REPORT 2ai.

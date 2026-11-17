# Proven sibling goals as axioms, resumed runs with lemmas, and sketches

*Reconstructed on 17 Nov from REPORT 2g and the session's commands (13 Nov 00:56–03:00). CPU-time limits.*

**Question.** Every goal of one original has the same axioms (checked), so a proven sibling goal is a theorem
of the theory and a sound extra axiom for the others. That is what CASC LTB allows within a batch. Do such
lemmas help, and do they add to the rule model? Do Veroff's sketches (proofs under extra assumptions, used
as hints) add more?

**Setup.**
* **lemmas.py** NAMES SOLVED OUTDIR -m M: adds up to M proven siblings with the nearest goal numbers below N,
  unit equations only. `--after` (later the default, `lemma_after`) also takes those above N.
* **loop.py `--lemmas M`:** at first lemmas came only from earlier rounds, so the chain of lemma proofs was
  well-founded by construction. Online pools later (13–14 Nov) made it "proven so far". Why that stays
  well-founded, and the check on 67k proofs: 2026-11-17-lemma-circularity.md.
* In the training logs, lemma axioms are labelled as axioms.
* **The 59** (sets/hard_near, 12 Nov 20:57): per dev10 original, the 6 goals unsolved by L2 and by plain 8 s
  that are nearest, by line in the original proof, to an earlier solved goal. One original had fewer
  than 6.
  * So they are picked to have solved goals just before them: a favourable set for lemmas.
  * Lemmas come from the 1,966 dev10 problems solved at 2–8 s.
  * twee-e12 at 20 s, -j 2.
* **The 345** at 8 s: lemmas from the 473 goals plain twee solves at 2 s, three per goal.
* **Resume with lemmas** (`--load-state` adds the problem's new axioms): three goals of aK2_eq_aK3_d that
  13 lemmas solve, from 2 s states (4k critical pairs).
* **Sketches** (sketch.py): the nearest siblings below N assumed, proven or not; the sketch proof's steps
  become hints. This is unsound as a proof and sound as a source of hints.
  * chainhints.py: the hints for goal N are the sketch hints of N and of the sketched siblings in
    [N−30, N], nearest first, at most 400.

**Results.**

On the 59 at 20 s:

| setting | solved |
|---|---:|
| plain (the 60 s run, solved within 20 s) | 12 |
| plain + 10 lemmas | 21 |
| rm4 | 19 |
| rm4 + 3 lemmas | **28** |
| rm4 + 10 / 30 lemmas | 27 / 26 |
| rm4 + 10 lemmas + kNN hints | 27 |
| rm4 + 3 lemmas + sketch hints | 28 (the 6 sketch-only goals stay unsolved) |
| chained sketches | 29 (+2 −1) |

* Sketch problems proven at 5 s: 15 with 3 assumed siblings, 19 with 10. For chained sketches, 389 of
  1,204 unsolved dev10 goals were sketched, 154 hints on average.
* On the 345 at 8 s: rm4 63, rm4 + 3 lemmas 68 (+10 −5), + 6 lemmas 70 (+6 −4 against 3).
* Used lemmas: 46 of 56 proofs that had lemmas use at least one (hard holdout set). The third nearest is
  used most often (29).

Resumed runs:

| goal | resumed, old binary | resumed, e20 | fresh with lemmas | fresh without |
|---|---|---:|---:|---|
| aK2_eq_aK3_d__goal_353 | fails (+40k) | 134 | 288 | fails at 40k |
| aK2_eq_aK3_d__goal_354 | fails (+40k) | 55 | 456 | fails at 40k |
| aK2_eq_aK3_d__goal_357 | fails (+40k) | 13.6k | 12.9k | fails at 40k |

**Reading.**
* Lemmas and the model add up (19 → 28 on the 59). The 59 favour lemmas by construction; on the 345 the gain
  is smaller (+5 net).
* **My first resume test was wrong.** On 13 Nov it said lemmas do not work in resumed runs, but that was a
  bug. A saved state stores each symbol with its precedence and id, which depend on the problem text, so a
  problem with new lemmas got a second signature under the same names. twee-e20 reuses the saved symbols and
  recognises new axioms by equation.
* Sketches cover only the stretch from the assumed siblings to the goal. Deriving the assumed siblings is
  the hard part, and they do not cover it.
* The user's later question (17 Nov) about these "simple proofs": lemma-assisted totals are a different
  measure from standalone proofs.

**Decision and next.** Lemmas on (3, later 6, siblings on both sides); sketches parked, to come back as
climbing (REPORT 2ab). REPORT 2g.

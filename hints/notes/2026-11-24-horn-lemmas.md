# Horn sibling lemmas (exp82, 24 Nov)

**Question.** Lemma import (lemmas.lemma_form) offers a proved sibling only when it is a unit equation or has a unit
form (REPORT 2ae, 15 Nov: 6,235 of AIM60k's 9,052 conditional goals unitize; "the other 2,817 stay out: they are genuine
Horn clauses"). Today 2,771 of them are proved and none has ever been offered as a lemma. They are laws a rewriting
prover cannot state as rules, for example aa1_12 goal 10, a cancellation law:
`l(l(x,y,z),u,w) = l(v,y,z) => l(x,u,w) = v`. Twee takes Horn axioms through its ifeq encoding (Jukebox HornToUnit).
Do the frontier's plain runs prove more with them?

**Context (24 Nov 07:26).**
* The unsolved goals: 3,187, of them 2,662 holes (a later goal of the same original is proved) and 525 tails; local
  heads 1,018, of them 955 holes. HLW1's proofs so far are all 22-55 proof lines past the last proven goal below.
* Proved Horn siblings near the heads: 846 of the 1,018 heads have at least one in their window (100 proved before, 30
  after), about 1.4 on average among the 100 before, beside about 81 unit ones. By count (5 = 5 or more): 0: 172,
  1: 296, 2: 229, 3: 181, 4: 71, 5: 69.
* Earlier work: REPORT 2j and 2ae on conditional goals (solved as often as unit ones; unit forms imported). No note
  has tried Horn lemma axioms (grep "horn", "ifeq" in notes/, REPORT, JOURNAL, exp/).

**Code.** `TWEE_LEMMA_HORN=1` (lemmas.HORN; 9b82b8f): lemma_problem adds the genuine Horn siblings it meets in its
window on top of the M unit ones, as clause axioms `lemma_goal_J` (the goal's own statement); condprove's later
siblings likewise. The unit lemmas stay the same. Off by default; off gives byte-identical problems. Twee's proof
names the axiom (`Axiom 26 (lemma_goal_10): ifeq(...) = X5`), so trust.py and condimport need no change.

**Set.** cond/EXP82.set (exp/sets/exp82.set): 60 unsolved local heads with at least 2 proved Horn siblings in the
window and not in exp81's set, random with seed 82 from 515; mean 3.1 Horn siblings, 36 originals.

**Arms** (abs/exp82.sh, exp/exp82.sh): plain 60 s runs as HLW1 (100 before and 30 after, 400 kNN), one thread each,
the same context snapshot cond/EXP82.trusted.
* H82H: TWEE_LEMMA_HORN=1.
* H82C: the same problems without the Horn axioms.

**Measures.** Proofs in each arm, +/−, union, per CPU h. Each arm's proofs are imported and merged at its end.

**Decision.** Proofs only with the Horn lemmas (+2 or more, −0) make TWEE_LEMMA_HORN=1 the default for plainlive6 and
production's lemma problems (after a check of loop.py's other lemma paths); a tie leaves it off.

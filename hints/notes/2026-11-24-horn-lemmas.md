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
* Scripts: exp/frontier_shape.py (distances, holes), exp/horn_count.py (Horn counts), exp/exp82_set.py (the window
  counts and the set; `--write` rewrites cond/EXP82.set).
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

## Encoding (24 Nov 08:11)

H82H's first two runs hit condprove's 600 s wall limit (aa3_45 359 and 486); the control H82C proved 486 in 48 s.
On aa3_45 486's Horn problem (3 Horn axioms beside 500 unit ones), 10 abstract s, twee-e61 (CPU s, peak memory):

| Jukebox `--conditional-encoding` | CPU s | memory |
|---|---:|---:|
| none needed (H82C's problem, no Horn axioms) | 11.6 | 114 MB |
| if-then-else (the default) | 91.3 | 350 MB |
| if-then | 295.4 | 697 MB |
| fresh | 9.8 | 117 MB |
| if | 9.9 | 119 MB |
| `--passivise` (default encoding) | 10.0 | 119 MB |
| `--passivise` with fresh | 9.1 | 100 MB |

The default run printed 7,130 lines with ifeq: each conditional rule is rewritten by the unit lemmas and overlapped
with `ifeq(X,X,Y,Z) = Y`. At 60 abstract s: fresh proves 486 in 29.8 CPU s (the control problem 42.5), `--passivise`
runs out at 600 s. Without Horn axioms the flag changes nothing: byte-identical outputs on 486's control problem and on
aa3_45 359's (a Horn goal: its negation is unit facts, no encoding).

H82H was stopped at 07:53 (2 runs, both over the limit). **H82F** (abs/exp82b.sh, exp/exp82b.sh): TWEE_LEMMA_HORN=1 and
`--args "--conditional-encoding fresh"` for the runs and condimport's reruns, the same set, snapshot and settings, one
thread, against the control H82C, which still runs.

**Elsewhere.** 7 of the 814 problems in the climber's loops/CLS71/tmp have a Horn axiom (assumptions such as
`assume_knn_4`, from Horn goals of other originals) and run with the default encoding; production's 259 in loops/UL/tmp
have none. The flag would change only those runs; it goes into the climber at its next restart.

## Result (24 Nov 09:32)

| arm | proved of 60 | timeouts | wall h |
|---|---:|---:|---:|
| H82F: Horn siblings, `--conditional-encoding fresh` | 2 (aa3_45 486, aK2rev 444) | 0 | 1.36 |
| H82C: the same problems without them | 1 (aa3_45 486) | 0 | 1.41 |

* +1 −0. **aK2rev 444's proof uses a Horn lemma:** both equations of lemma_goal_450 (aK2rev 450, a proved Horn goal) are
  among the proof's axioms (Axioms 32 and 34 of the printed proof, `fresh2(m(m(X0,X1),X2),X0,X1,X2,X3,X4) = X2` and its
  partner). It is in production (condimport 1 of 2; aa3_45 486 came with H82C).
* With the fresh encoding the Horn problems cost the same (1.36 against 1.41 wall h for the 60).
* The decision rule (+2 or more, −0) is not met by one proof. The mechanism is real and the cost neutral, so the test
  is extended rather than closed: exp82c, 60 more heads with at least 2 Horn siblings (seed 821, not in exp81's or
  exp82's sets), the same two arms, on exp81's two threads when it ends. The rule then applies to the 120.

**exp82c started 24 Nov 11:24:18** (exp/sets/exp82c.set): context 48,953, 60 heads from 498 candidates (seed 821, not in
exp81's or exp82's sets), mean 3.07 Horn siblings, 32 originals. First problem aa3_45 497: H82G 106 sibling axioms (3
Horn) and 400 kNN, H82D 103 and 400; only H82G's twee runs have `--conditional-encoding fresh`.

## exp82c result and decision (24 Nov 12:59)

| batch | Horn arm | control | + | − | wall h (Horn / control) |
|---|---:|---:|---|---|---|
| exp82 (seed 82) | 2 (H82F) | 1 (H82C) | aK2rev 444 | – | 1.36 / 1.41 |
| exp82c (seed 821) | 9 (H82G) | 10 (H82D) | – | nil3_31 546 | 1.36 / 1.40 |
| **both, 120 heads** | **11** | **11** | 1 | 1 | 2.72 / 2.81 |

exp82c's heads were picked at 11:24, after the climber's chains had changed many contexts, so both arms proved far more
than exp82's. **Decision: TWEE_LEMMA_HORN stays off** (the rule, +2 or more and −0 over the 120, is not met). The Horn
lemmas are usable (one proof used one, at no extra cost with the fresh encoding) but their net effect at 60 s is nil:
the one gain is matched by one loss, a perturbation. `--conditional-encoding fresh` stays in the climber (cls71d.sh):
no change without Horn axioms, 8x cheaper with them. **exp82 is closed.**

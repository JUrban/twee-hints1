# Sketches in stronger theories, climbing up and down

*Reconstructed on 17 Nov from REPORT 2aj (15 Nov evening – 16 Nov 01:30). Abstract time.*

**Question.** The user, 15 Nov evening:
* assume stronger theories instead of laws (Bol loops for loops), which are mathematically relevant and should
  not trivialise the sketch;
* dream up new axioms with the generator;
* when a sketch is too hard, make the theory stronger or the goal weaker, climbing both up and down and
  learning from the climbs (after Hernandez and Korovin, IJCAR 2018).

**Setup.**
* **climb.py** (04617bc–493f9cd):
  * `--min-sketch-steps N` bans an assumption whose sketch proof has fewer than N steps.
  * `--theories K`: a stronger theory is the axiom set of another original that strictly contains the target's
    (74 of 129 originals have one; the 17-axiom base theory has 115). Ranked by the similarity of their solved
    goals. `--theory-lemmas 10` adds the stronger theory's most similar proven goals (true in B, not in A).
  * `--gen-assume K`: the generator's most sampled equations.
  * `--updown`: up = unions of theories and weaker goals (instances of the conjecture, via loop.py's
    `goal_override`); down = drop a used assumption or restore the goal.
  * `--chain`: a proof is a sibling lemma and hints for later targets at once.
* **sets/gen48:** the first 48 of gen200 (unsolved, one failed fresh 5 s run each), snapshot ULsW, 1 worker each.
* **Family test** (abs/fam.sh): sets/fam24 = the first 12 unsolved goals, in proof order, of aK2_eq_aK3_1243b
  (66 stronger theories) and of nsmr_to_aa1 (3). Snapshot loops/ULsX (UL at 20:15), in order with `--chain`.
  The control F80 is one fresh 80 s run per goal.
* **Live** (abs/clu.sh, loops/CLU, from 22:07): the FUD config with `--up-single`, on production's stalled goals,
  idle CPUs only (`--cpus 20`, at most 6 climbs). Every sketch's steps are saved in loops/CLU/sketches.
  latticedata.py makes one row per move for learning.

**Results.**

| gen48 arm | proved | CPU s |
|---|---:|---:|
| fresh 20 s (control) | 1 | 1,589 |
| fresh 20 s `--backwards-goal 1` | 1 | 1,545 |
| fresh 20 s `--hint-goal` | 2 | 1,822 |
| CL6A siblings + kNN goals + gap filling | 2 | 4,903 |
| CL6L laws, trivialising ones banned | 2 | 4,168 |
| CL6T 6 stronger theories + their lemmas | 2 | 4,546 |
| CL6U CL6T + up/down | 2 | 4,051 |
| CL6G 6 generated equations | 2 | 4,483 |

Every 2 is the control's goal plus Ka1_eq_Ka2__goal_403, which `--hint-goal` alone also proves.

| set | arm | proved | CPU s | proofs per CPU-hour |
|---|---|---|---:|---:|
| fam24 | full climb (FUD) | 3 (1243b 441, 445, 448) | 2,652 | 4.1 |
| fam24 | fresh 80 s per goal (F80) | 3 (1243b 446, nsmr 614, 616) | 6,032 | 1.8 |
| fam24 | climb without stronger theories (FUDnt) | 1 (448) | 1,738 | 2.1 |
| next 24 1243b goals | FUD2 | 1 (455) | 2,904 | 1.2 |
| next 24 1243b goals | F80b | 1 (455) | 4,981 | 0.7 |
| fam24 | FUD + one-axiom up steps (FUDs) | 3 (the same) | 3,402 | 3.2 |

* 441's final run used 17 true lemmas from gap filling; 445 and 448 also fall to their hints alone.
* Live: 202 climbs gave 3 proofs in the first 1.6 hours. By 01:30 there were 9, all in production, after which
  production proved 9 later goals of the same originals.
* A misreading to note: at 23:43 I first wrote 6 proofs, reading three names from a directory listing whose
  climbs had failed. Corrected in REPORT 2aj.

**Reading.**
* **Sketches are trivial on these goals whatever the assumption.** A nearby sibling, a stronger theory's goal, a
  generated near-restatement or a weaker instance proves the target in 0.3–2.8 s. The assumptions that help are
  as hard as the target, so the sketch covers only the easy last steps.
* On gen48 nothing gains beyond perturbation. gen48 spreads over many originals, so sketch hints, which are
  shared within an original, do not accumulate.
* On a family run in order, the climb is at least as productive per CPU as long fresh runs, and proves
  different goals (6 distinct between FUD and F80). Stronger theories are what it adds (3 against 1).
* Small numbers: 3 against 3, 1 against 1. The per-CPU difference is the robust part.

**Decision and next.** The live climber as a side worker; the lattice-move data for learning
(2026-11-16-lattice-moves.md). `--hint-goal` dropped (the same 3 on the other 152 gen200 goals at 13% more
CPU). 12 probe proofs merged into UL at 22:50. REPORT 2aj.

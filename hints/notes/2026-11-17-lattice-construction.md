# Building a lattice with reasonable steps: strengthenings, weaker goals and conjectures (design and stage 1)

**Question.** The user, 17 Nov 20:10–20:25:
* Try the theory up-down ladders for the hard goals, and conjecture intermediate goals between the chain and the
  target.
* On "the assumptions that helped were as hard as the target": that means we have no good lattice with
  reasonable steps. Learning to climb (2026-11-16-lattice-moves.md) cannot fix that.
* If there is no good lattice of stronger theories and weaker goals, create one by various methods. For example,
  generate intermediate lemmas that might be useful for the goal with a conjecturer, or run deductions from the
  goal and the axioms. See Korovin's paper (/project/978-3-319-94205-6_43.pdf), and add more climbing moves to
  Korovin's.

**What the old lattice was** (climb.py, 14–16 Nov). Its nodes were the target plus whole statements as
assumptions:
* the M nearest unproved sibling goals;
* the generator's most sampled equations;
* the entire axiom set of another original that strictly contains the target's;
* instances of the target as weaker goals.

Down moves dropped one used assumption whole. On the goals tried, every assumption that made the target provable
gave a sketch of 0.3–2.8 s: the assumption carried the whole difficulty (2026-11-15-sketches-stronger.md). The
lattice had a top and a bottom, and nothing between.

**Korovin and Hernandez, IJCAR 2018 (read in full 17 Nov 20:15).**
* Over-approximations: abstractions under which a provable problem stays provable (a stronger theory, in our
  terms):
  * signature grouping: identify symbols of the same type. Grouping only Skolem constants and constants gives
    instances of the goal;
  * argument filtering: a symbol ignores some arguments;
  * generalisation: subterms of axioms replaced by variables;
  * subsumption grouping of clauses.
* An abstract proof's unsat core is concretised. If the concrete core fails, the abstraction is refined one step
  (one group split, one argument restored), so each rung is one small change.
* Under-approximation: fewer axioms, refined by axioms that the countermodel violates.
* On the CASC-26 large-theory batch, grouping was the best single abstraction (716 of 1,500), and combining them
  gave 826.

**Moves for us** (Korovin's plus ours). Up moves, each one small step:
1. Grouping: identify two symbols of the same arity (`ld`≡`rd`, `l`≡`r`), i.e. the axiom f(x̄) = g(x̄).
2. Argument filtering: f(…, x, …) = f(…, y, …) for one argument of one symbol.
3. Natural laws of the theory's algebra (as the 14 Nov "frequent extra axioms"): commutativity, associativity,
   flexibility, the inverse properties, Moufang and Bol laws, an inner map trivial (t(x,y) = x) or two maps equal.
4. Generalisation of one hypothesis axiom: one subterm replaced by a fresh variable.

Weaker goals:

5. Instances of the goal: two goal variables identified, or one set to `e` (Korovin's grouping of Skolem
   constants).

Down moves (refinement):

6. Replace an assumption by its instances that the sketch proof used. That is weaker but still enough, and each
   instance is a conjecture to prove in the real theory.
7. Drop an assumption (the old move).
8. Undo one grouping or filtering.

Conjectures between the chain and the target:

9. Deductions from the goal: the goal's two sides normalised by a deep run's final rules, then decomposed
   (f(ū) = f(v̄) is implied by uᵢ = vᵢ). The parts are sufficient subgoals, true or not.
10. The generator (gen.py), anti-unification of the goal with the chain's statements, and instances of proven
    siblings' statements on the goal's terms.

**The semantic filter: Mace4** (Prover9-new's mace4.src, linked to /project/bin/mace4 at 20:24; problems
converted with Prover9-new/bin/tptp_to_ladr).
* A move is rejected without any twee run when:
  * the strengthened theory has no model of size 2 to 8 (it collapses), or
  * it has no non-associative model of size 2 to 12 ('group': it probably forces a group, where these goals
    become trivial). 12 is the smallest non-associative Moufang loop.
  * **Correction (20:30):** I first also rejected a strengthening under which the goal has a countermodel. That
    check is vacuous: the goal is true in T, so it is true in every T+S. And a 2-element model alone proves
    nothing, since the 2-element group satisfies every loop law.
* A conjecture is rejected when the real theory has a countermodel to it.
* Measured on KK_Kcom_to_aK1 (19 axioms): commutativity and associativity are refuted by 6-element models in 0.13
  and 0.44 s. The true goal 299 has no countermodel up to 16 elements in 20 s, as it must.
* Absence of a countermodel up to size N is no proof. It only keeps a conjecture as a candidate.

**Stage 1: is there a lattice with small steps around the hard goals?** On exp3's 47 late unsolved goals
(exp/sets/exp3_goals47; their deep runs at 320 s are the baseline):
1. Generate moves 1–5 for each goal's theory. Filter them with Mace4.
2. For the survivors, run a short twee sketch: the strengthened theory or weaker goal, with production's context.
3. Record per move: survives Mace4, sketch proved, proof size, and which instances of the assumption the proof
   used.
4. Check those instances with Mace4 in the real theory. The plausible ones are the intermediate lemmas.

Outcome measures:
* how many goals have a move whose sketch proves;
* the step sizes, i.e. whether some sketches are long, not just the trivial last steps;
* how many used instances survive Mace4.

Stage 2 proves those lemmas (chain-guided deep runs) and then the goal with them as lemmas and the sketch steps as
hints. Stage 2 is designed after stage 1's numbers. Scripts will be hints/exp/exp4_*.

**Tools** (in /project/hintwork/exp4, copies in hints/exp as exp4_*):
* moves.py GOAL: generates moves 1–3 and 5 from the problem (converted to LADR), and screens them. Takes 73 s per
  goal with the bound of 12 (4 s with 8).
* sketch.py MOVES OUT: runs the kept moves. Each sketch is the goal's captured production command (exp3/tb) at
  5 abstract s, with the proof printed. It extracts the used instances of S from the proof: at each step
  `by axiom k (assume_S)`, the terms before and after differ at exactly one position, the redex. The goal's
  constants are arbitrary, so they generalise to variables. Each instance is screened with Mace4 in T.
* stage1.sh: both, over the 47 goals, 2 CPUs.

**First goal** (KK_Kcom_to_aK1 299, 20:30; it fails at 320 s in all four exp3 arms). Of 52 generated moves, 18
collapse, 12 force a group and 23 are kept (17 strengthenings, 6 weaker goals).

| moves kept | proved at 5 s | proof lemmas | used instances of S | refuted by Mace4 |
|---|---:|---|---|---|
| 4 groupings | 3 (ld≡m, ld≡rd, m≡rd) | 127–155 | 15–29 | 13–24 |
| 3 filterings (k or t ignores an argument) | 3 | 33–56 | 1–2 | all |
| 10 laws | 6 (commutativity, flexible, RIP, right Bol, t trivial, k = e; not the alternative laws, LIP, left Bol) | 30–157 | 1–6 | 1–3 each |
| 6 weaker goals | 1 (the third variable set to e: 30 lemmas in 0.7 s, S not needed) | 30 | | |

* **Steps exist, and they are not trivial:** sketches of 30–157 lemmas, against a goal that fails at 320 s.
* **But no sketch concretises as it stands:** every proved sketch used at least one instance of its assumption
  that is false in T.
* So the next step is the refinement: give only the plausible used instances, as separate assumptions, and run
  the sketch again. If it still proves, the rung is that handful of conjectures, each a subgoal. If it does not,
  combine the plausible instances of several moves.

**Launch** (stage 1, 20:33): `cd /project/hintwork/exp4; nohup bash stage1.sh > stage1.out 2>&1 &`.

**Resources.** exp3 holds 12 workers until about midnight. Stage 1 starts with Mace4 (cheap, 1–2 CPUs) and tries
single goals. The sketch runs wait for free CPUs.

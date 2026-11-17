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

**Refinement on the first goal** (refine.py, 20:36). The plausible used instances were given as separate assumptions
(fof(assume_i, ...)), 5 s, once for each of the 6 proved sketches that had any (2–9 instances), and once with all 24
together. **None proves.**
* Every sketch depended on consequences of its assumption that are false in T. The assumption changes the
  theory, not just the search.
* Only the universally quantified instance can be a lemma. A used instance holds the goal's constants, but the
  goal is true in T, so "the goal or the instance" holds trivially and says nothing.
* So on this goal the steps exist but are not small.
* Down steps still to try on all 47: the refinement at 20 s, and Veroff's sketch hints (the real goal, no
  assumptions, with the proved sketches' steps as hints, false ones included, at 80 s against exp3's 320 s).

**Stage 1 results** (all 47 goals, finished 21:53). 2,586 moves were generated, and 1,031 survived the screen and
were sketched at 5 s.

| kind | sketched | proved at 5 s | proof lemmas (quartiles) |
|---|---:|---:|---|
| weaker goals (instances of the goal) | 377 | 178, in all 47 goals | 3 / 16 / 26 / 41 / 231 |
| groupings | 149 | 77 | |
| filterings | 126 | 118 | |
| laws | 379 | 187 | |
| all strengthenings | 654 | 382, in 45 goals | 3 / 24 / 39 / 82 / 439 |

* No strengthening's proof went without S, so none is a proof of the goal itself.
* The proofs used 1,653 instances of S, and Mace4 (5 s, up to size 8) refuted 1,336.
* 21 sketches in 15 goals used only instances it did not refute. But many of those are S itself in its full
  generality (k(A,B) = e, i.e. commutativity, in 7 goals), which is no step down.
* **The 5 s screen is too lenient.** Commutativity in R1dist_to_aa1 and aK2_eq_aK3_q has a countermodel of size 8.
  Mace4 finds it in 11–17 s, after the 5 s limit. l = r in aK2_eq_aK3_e has one of size 9 (9 s).
  * rescreen.py screens the 317 surviving (goal, instance) pairs again: sizes up to 12, 30 s each, 3 CPUs.
    Launched 21:56, output rescreen47.tsv.
* **Weaker goals are real steps down.** In every goal some instance of the goal (two variables identified, or one
  set to e) proves in 5 s, with proofs of median 26 lemmas. These are true lemmas.

**Fault in the instance extraction** (found 22:15; the stage 1 instance counts above are affected).
* sketch.py took the innermost position where the terms before and after an S step differ. For an argument
  filtering f(..X..) = f(..Y..) that position is inside the redex, so every filtering "instance" came out as a
  false x = y. The table's "all refuted" for filterings is that fault.
* Steps into a bare variable were also skipped.
* reinst.py extracts again from the saved proofs. The instance is the deepest position on the differing path where
  (before, after) matches S, either orientation, with one substitution.
* It screens the new instances at sizes up to 12, 30 s each, and reuses every countermodel already found (sketch.py's
  5 s and rescreen.py's). 502 instances need screening.
* The faulty re-screen (rescreen.py, 146 of 317 done) was stopped at 22:15, and its countermodels are reused.
* Launched 22:16: `python3 reinst.py sketch47.tsv sketch47b.tsv -j 2 --cache rescreen47.tsv`.
* refine.py now drops instances that are S itself up to renaming and orientation.

**Down step with sketch hints** (downhints.py, launched 21:57).
`python3 downhints.py sketch47.tsv down80.tsv -j 2 --time 80 --arms I,U`
* The real goal, with no assumptions, runs with the goal's production command (exp3/tb) at 80 abstract s.
* Hints: the pool, plus the steps of the goal's proved sketches, as in Veroff's proof sketches.
* Arm I takes the weaker goals' proofs, which are all true. Arm U takes the strengthened theories' proofs, which
  include steps false in T.
* 47 goals × 2 arms. exp3 lowered to 8 workers for it.
* Control without a run: exp3's C@320 runs the same command, and abstract time is deterministic. So C proves
  within 80 s iff its proof took at most 160,000 critical pairs. None of its 4 proofs did (230k–529k).
* **Stopped at 22:35, after 20 of 94 runs (10 goals in I, 10 in U), no proofs.**
  * The sketch steps were 7–470 hints against pools of 2,500–14,000, at the pool's own factor.
  * Hint matches were about the same in I and U (for example 955/966 and 2,016/2,015). So the runs could only
    repeat the control, which proves none of these goals within 80 s.
* **Relaunched with the sketch hints boosted** (hints file column 3 = 0.001, ten times the pool's default 0.01;
  score = size × factor, lower is better). Arms U then I, 80 s, 2 CPUs:
  `python3 downhints.py sketch47.tsv down80f.tsv -j 2 --time 80 --arms U,I --factor 0.001`
  * **Stopped at 22:53, after 10 goals in both arms (20 runs): no proofs.** Hint matches again about equal to the
    plain runs (for example 920/966, 1,329/1,307, 1,626/1,553). The sketch steps the pool lacks are few (7–473),
    and even at ten times the boost they do not change the search's course within 80 s.
  * Its CPUs went to exp5, long runs (notes/2026-11-17-long-runs-late-goals.md).

**Deductions from the goal** (nf.py, launched 22:02, 1 CPU). Move 9, conjectures by deduction from the goal.
`python3 nf.py /project/hintwork/exp3/goals47 nf20.tsv -j 1 --time 20`
* twee-e56 (e55 plus `--print-goal-nf N`) runs the goal's production command for 20 abstract s, with
  `--no-flatten-goal`. With flattening, the goal's normal forms are just the constants that name its sides. On
  failure it prints the 3 smallest normal forms of each side.
* Each pair of normal forms is decomposed where the heads agree: f(u..) = f(v..) follows from the uᵢ = vᵢ that
  differ. Every cut of that tree is a sufficient set of subgoals.
* A set is kept when Mace4 refutes none of its subgoals (sizes up to 12, 10 s each).
* Goal 299: the normal forms are m(m(x1,x0), k(x2,m(x0,x1))) and m(k(x0,x1), t(m(x0,x1),x2)). Their one
  decomposition needs m(x0,x1) = k(x1,x0), which is false.
* **Result (finished 23:06, all 47 goals; none proved in the 20 s run).**
  * 78 distinct subgoal sets: 58 of size 1, 18 of size 2 and 2 of size 3.
  * Mace4 kept 49 sets. But all except 2 are a pair of the goal's own normal forms, which is equivalent to the
    goal, not a step (nf2moves.py drops those).
  * The 3 remaining subgoals:
    * mbol_lem1 387 splits into `k(X0,X1) = a(X2,X3,k(X0,X1))` and `ld(l(k(X0,X1),X2,X3),X4) = X4`. The first
      has a countermodel of size 8, found by a 30 s screen.
    * nslm_to_aa1 1003 reduces to `rd(m(t(X0,X1),X1),t(X0,X1)) = ld(k(X1,X0),X1)`.
  * The two survivors do not prove as goals in 20 s (sketch.py, nfsketch20.tsv).
  * So the goals' normal forms almost never share a head below the top. Decomposition gives no steps here.

**Generalisations of the goal** (genmoves.py, 22:05). Korovin's generalisation, applied to the goal itself (Polya's
inventor's paradox).
* Every occurrence of one proper subterm of the goal is replaced by a fresh variable. The result implies the goal,
  so if it is true it gives the goal at once, and it has fewer symbols.
* Mace4 screen: sizes up to 12, 10 s each. Of 214 generalisations, 178 are refuted, most by size 2, i.e. Z2: a
  variable that occurs only once is free. 36 survive, in 20 goals; for example
  `l(X0,X1,k(X2,X3)) = X0` for aK2_eq_aK3_gen 522.
* The survivors are run as goals (sketch.py, kind gen, 20 s, 1 CPU, launched 22:13):
  `python3 sketch.py gen47.tsv gsketch20.tsv -j 1 --time 20`.
* **Result (22:33): none of the 36 proves in 20 s.** Where true, they are no easier than the goal.

**A model-based conjecturer** (conj.py, launched 23:12, 1 CPU). The user's "generating intermediate lemmas that
might be useful for the goal by some conjecturer". The idea is QuickSpec's (whose prover is twee), and also how
Kinyon and Veroff found AIM lemmas, from finite models.
* Mace4 collects models of the goal's theory:
  * non-associative ones, up to 25 per size from 2 to 12, 15 s per size. The smallest exist at 6–8 elements,
    found in 0.3–2.7 s on 6 goals;
  * any models (groups among them), up to 10 per size from 2 to 8.
* Candidate terms: the subterms of the goal's sides and of their normal forms (nf.py's outputs), plus the
  variables and e.
* Conjectures: the equations between two candidates that hold in every model, evaluated with numpy over all
  assignments. The goal and its normal-form pairs are excluded.
* `python3 conj.py /project/hintwork/exp3/goals47 conj47.tsv -j 1 --nf nf20.tsv`
* First goal (R1dist_to_aa1 619): 52 models, 148 candidate equations, 5 kept. They are basic identities among the
  goal's subterms, such as `ld(rd(e,X0),e) = X0` (the right inverse of the left inverse). No left-to-right bridge.

**Launch** (stage 1, 20:33): `cd /project/hintwork/exp4; nohup bash stage1.sh > stage1.out 2>&1 &`.

**Resources.** exp3 holds 12 workers until about midnight. Stage 1 starts with Mace4 (cheap, 1–2 CPUs) and tries
single goals. The sketch runs wait for free CPUs.

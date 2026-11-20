# Unsound Prover9 proofs: a negation bug in p9twee.py, and re-verifying production (20 Nov)

Written 20 Nov 2026, 10:32 UTC, while the re-verification runs.

## How it was found

* exp/joincheck.py (09:30) asks whether unsolved goals follow by ordered ground rewriting with the proof steps of
  proven unit goals in weaker theories (a feasibility check for cross-run joining). The first version also took the
  steps of conditional goals' proofs. Those use the goal's hypotheses, so steps like `e = k(X0,X1)` are not valid
  in general. It "joined" 11 of the first 28 unsolved goals. With unit goals only: 1 of 60.
* That one, aK2_eq_aK3_s__goal_497, used `m(X0,X1) = m(X1,X0)` and, through it, `ld(X0,e) = X0`: commutativity and
  x·x = 1, neither valid in that theory (loop axioms, the AIM axioms, the anti-automorphic inverse property). Both
  came from the hints of aK2_eq_aK3_s__goal_450, proved on 18 Nov 17:40 by the Prover9 side worker (loops/P9C).
* Its Prover9 input had the lemma `(- m(t(X0,X1),X2) = m(X0,rd(X1,X0)) | rd(X1,t(X0,X1)) = X2).` That is a
  conditional sibling goal, `~ m(...) = m(...) | ...` in TPTP. **p9twee.ladr replaced `~` with `-`.** In TPTP, `=`
  binds tighter than `~`, so `~ a = b` is ~(a = b). In LADR, prefix `-` binds tighter than `=`, so `- a = b` is
  the equation (-a) = b with `-` an uninterpreted function symbol. So every conditional sibling lemma became a false
  axiom. From it Prover9 derived `A = B | A = C | C = B` (at most 2 elements), then `ld(A,e) = A`, and the goal.
* Fixed at 09:45: `_neg` writes `-(A)` around the atom. Checked with Prover9: `-(m(A,B) = e)` reads as
  `m(A,B) != e`.

## Scope

* Prover9 ran through p9twee.py only. That covers:
  * P9T: the 72 stalled goals at 60 s, 15 Nov;
  * P9L: the live side worker from 15 Nov 08:56;
  * exp16: the walls, 18 Nov;
  * P9C: the chain side worker, 18 Nov 16:46–19:38;
  * production's `p9` variant: 28 runs, 0 proofs.
* From-zero arms never ran a p9 variant (no p9var dirs).
* **Prover9 proofs that used a false clause** (a `-f(` term in the proof):
  * P9C: 9 of 10;
  * P9L: 3 of 9;
  * P9T: 1 of 1;
  * exp16: all 6 (5 goals).
  * 16 of these goals were in production's solved list on Prover9's proof.
  * The 7 sound Prover9 proofs had none of the 16 in their inputs.
* **The statements are true.** AIM60k's goals are steps of real Prover9 proofs. Only our proofs are void, and with
  them every later proof that used one of these goals as a lemma axiom.
* **REPORT claims that fall:**
  * 2ad/2af (15 Nov): "the first hit is aK2_eq_aK3_r__goal_241 … Prover9 proved it in 44 s". That proof is unsound.
  * 2az (18 Nov): "Prover9 with the chain is the cheapest member (2.3 per CPU hour)", and exp16's 4 walls. Those
    proofs are unsound (P9C 9 of 10, exp16 6 of 6).
  * The p9 member's yields per CPU hour are void.

## Which proofs depend on them

* exp/unsound.py computes the closure of the 16 over the lemma records:
  * kept twee outputs: since twee-e31 (14 Nov 16:12) the `USEDAXIOMS` line names each used lemma, `lemma_goal_J`
    or `lemma_knn_I_<goal>`;
  * the climbers' used.tsv;
  * the transfer loops' source columns.
  * First pass (13 goals): 145 in the closure.
* Quarantine at 10:07, Q = 1,130 goals:
  * the closure (145);
  * the 226 proofs since 15 Nov 08:56 without a record;
  * the live loop's 42 proofs: its `skax_` lemma axioms carry no goal names;
  * 717 transfer proofs since T0: the transfer loops kept no outputs, and their sibling, kNN and source lemmas
    are not recorded.
* Production went from 48,187 solved to 47,057. Hints went to loops/UNSOUND/qhints; the old list is
  loops/UNSOUND/UL_solved.tsv.bak.
* exp16's 3 goals were found after that (10:15). The closure with all 16 added 11 more dependents. And a
  quarantined goal is itself an unproved lemma for whatever used it. So the closure is the wrong tool.
* **exp/trust.py** (10:30) makes it a fixpoint. A proof is trusted if:
  * it is older than T0 (15 Nov 08:56, the first unsound proof in production); or
  * a record names every lemma it used, and each of those lemmas is a trusted proven goal.
  Anything else is untrusted.
  * At 10:32: 44,063 trusted (43,497 before T0, 566 later) and 3,947 untrusted.
  * Of the untrusted, 570 are roots: 504 have no record and 66 an unresolved lemma name (srclem_, skax_, …). The
    other 3,377 used an untrusted or unsolved lemma.
* **exp/rever2.py** re-proves the roots and the quarantined unsolved goals, in passes:
  * the lemma context is trusted proofs only;
  * each goal's last proof serves as its hints (hints do not affect soundness);
  * production's transfer options at 60 s, with `--keep-out`, so the new proofs carry records;
  * after each pass, trust.py again; a re-proved root makes the proofs that used it trusted when their records
    are complete.
  * Passes run until one proves nothing new, then one more at 300 s. Whatever stays untrusted at the end leaves
    production's solved list.
* From 10:35, the transfer loop and the live loop run with `--keep-out` (abs/xfrlive2k.sh, abs/gmlive2k.sh), and
  transfer.py names source lemmas `srclem_<i>_<goal>`, so their proofs carry records too.

## Lessons

* **Hints may be wrong; axioms may not.** Every path that turns text into an axiom needs a check: TPTP to LADR,
  hints to lemmas, given logs to `.ax`. A second prover's input converter is part of the trusted base.
* **Every proof should record its lemmas by name at write time.** The kept outputs did this for production's own
  runs, by accident of --keep-out. The side workers did not, and that made most of this re-verification necessary.
* **An independent check** (here, rewriting with the union of proof steps) finds invalid "facts" that no single run
  shows. Worth running now and then over all hints: a join of an unsolved goal is either a cheap proof or a wrong
  step.

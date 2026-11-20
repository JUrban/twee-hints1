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
* **The exposed theories (10:36).** Every lemma mechanism takes lemmas from theories within the target's:
  siblings, kNN with subsets, the proof-dependency sets, transfer's srclem guard and `.ax` (from runs of weaker
  theories), the climber's true lemmas, and the base lemmas. So a proof can rest on one of the 16 only if its theory
  contains that goal's theory. That holds for 43 of the 129 originals (loops/UNSOUND/exposed.txt), and every proof
  outside them is trusted, record or not (`trust.py --exposed`).
  * The 84 quarantined goals outside the exposed originals that were still unsolved went back at 10:36, with their
    old proofs (loops/UNSOUND/restored_1036.txt).
  * Trust at 10:37: 47,570 trusted and 529 untrusted (101 without a record, 29 with an unresolved lemma name, 399
    using an untrusted or unsolved lemma).
  * rever2 pass 1: 130 roots plus 91 quarantined unsolved goals, 221 in all, at 60 s. **161 proved** (2.36 CPU h,
    10:37-11:13).
* **trust.py fixes (11:21):**
  * It missed rever2's own outputs (loops/REVER2/p1/r1/out, one level down), so pass 2 had 137 of pass 1's 161
    proofs as roots again. Stopped after 31 of 50 runs.
  * It took a goal's record from any matching output. The side loops' hints dirs are symlinks to production's, so
    an old unresolved proof of a re-proved goal also "matched" and kept it untrusted. Now each goal's record comes
    from its newest matching output.
  * With both fixes at 11:21: 48,168 solved, 230 untrusted (6 without a record, 6 with an unresolved lemma name, 218
    using an untrusted or unsolved lemma).
  * rever2 continues in loops/REVER3 from 11:24. Pass 1: 11 of 53 (the roots were then mostly hard quarantined
    goals).
* **Circular proofs (12:08).** At 12:07, 96 proofs were untrusted: 4 without a record, 5 with an unresolved name, and
  87 with complete records whose lemmas were not trusted.
  * Of those 87, 20 formed 8 cycles of 2-4 goals, and 67 waited on a cycle or on unsolved lemmas. In a cycle,
    production had re-proved a quarantined goal B from a lemma A whose own (older) proof used B. Production takes
    lemmas from its whole solved list, untrusted proofs included.
  * The fixpoint never breaks such a cycle, and rever2 only re-proves proofs without a complete record, so
    neither would.
  * Fix: the 96 were quarantined (exp/quarantine2.py, 12:09: 119 rows; hints to loops/UNSOUND/qhints2) and added
    to Q. No writer can use them as lemmas now, and rever2 (loops/REVER4, 2 workers until exp42 ends) re-proves Q's
    unsolved goals with trusted lemmas only.
* **12:10: 48,108 solved, all trusted.** Holdout 5,320 of 5,880. REVER4: 125 quarantined goals to re-prove.
* Still open: the 5 bad goals not yet re-proved (aK2_eq_aK3_s 450, 470, 474, 476; mbol_lem1 387). The other 11
  have new sound twee proofs.
* From 10:35, the transfer loop and the live loop run with `--keep-out` (abs/xfrlive2k.sh, abs/gmlive2k.sh), and
  transfer.py names source lemmas `srclem_<i>_<goal>`, so their proofs carry records too.

## Lessons

* **Hints may be wrong; axioms may not.** Every path that turns text into an axiom needs a check: TPTP to LADR,
  hints to lemmas, given logs to `.ax`. A second prover's input converter is part of the trusted base.
* **Every proof should record its lemmas by name at write time.** The kept outputs did this for production's own
  runs, by accident of --keep-out. The side workers did not, and that made most of this re-verification necessary.
* **A quarantine must cover the dependents at once.** Production kept the untrusted dependents as lemma sources,
  and re-proved quarantined goals from them. That made 8 circular pairs and triples, which a trust fixpoint cannot
  resolve. Quarantine everything untrusted together, then re-prove with trusted lemmas only.
* **An independent check** (here, rewriting with the union of proof steps) finds invalid "facts" that no single run
  shows. Worth running now and then over all hints: a join of an unsolved goal is either a cheap proof or a wrong
  step.

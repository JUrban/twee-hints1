# False hints from conditional goals, and abstract time

*Reconstructed on 17 Nov from REPORT 2j–2k and the session's commands (13 Nov 08:00–09:40).*

**Question.** Veroff makes proofs strictly forward and demodulation-free (SFDF) so that hints are
skolem-free. Do twee's generalised hints need the same, and are any of them false? And, separately: our
comparisons depend on machine load. Can runs be made deterministic?

**Setup.**
* **Are hints true?** 40 random solved problems; all 814 of their pool hints posed as conjectures from the
  problem's axioms, twee at 15 s, then 90 s for the rest.
* **Conditional goals:** goals `A = B → C = D`, 9,052 of the 51,784 public problems (17%). Counted in 300
  solved conditional problems: how many hints depend on the hypothesis.
* **Fix (twee-e14):** `--print-hints` traces each lemma's derivation, and lemmas and goals that use a
  hypothesis go into a `HINTS-HYP` section. Pools skip it; rule-model labels still count those lemmas as
  proof lemmas. cleanpool.py cleans old pools.
* **Test:** the 310 conditional holdout problems that plain twee does not solve in 4 s.
  * rm4 + kNN 30:100 hints from train_pool + tr30_g1_pool, old against cleaned pools.
  * First at 4 CPU s on a loaded machine, then again at 8,000 critical pairs (`--abstract-time 2000
    --max-time 4`, twee-e15).
* **Abstract time (twee-e15):** `--abstract-time N` makes twee's clock count critical pairs considered, N
  per second. `--max-time` and the housekeeping tasks (hint normalisation, requeue, interreduction) follow
  it.
  * Calibrated on 60 holdout problems: a median of 1,800 pairs per CPU second (quartiles 1,700 and
    2,300), so N = 2000 keeps old budgets comparable.
  * Twee prints `WORK considered=N rules=M`; run.py stores it as a fourth column.
  * `--wall-factor` lets the wall-clock safety limit be exceeded.

**Results.**
* Of the 814 hints, 807 were proved within 15 s and one more within 90 s; 6 are false (e.g.
  `m(X0,X1) = m(X2,X3)`). All 6 came from conditional problems, where the hypothesis is a ground clause
  with skolems and generalising lemmas derived from it is wrong.
* In the 300 conditional problems, 27% of the hints depended on the hypothesis.
* cleanpool.py removed 19% of the hints of conditional problems in train_pool (2,965 hints) and 3% in
  tr30_g1_pool.
* On the 310:

  | setting | 4 CPU s, loaded | 8,000 pairs |
  |---|---:|---:|
  | rm4 alone | | 11 |
  | rm4 + old pools | 20 | 17 |
  | rm4 + cleaned pools | 18 | 17 (the same 17) |

  The two extra in the CPU-time run finished at 4.0–4.1 s: load noise.
* **Determinism:** two problems, 6 runs each with abstract time, gave identical results and counts.

**Reading.**
* **Proofs stayed sound throughout.** Hints only steer, and lemma import takes only unit-equation goals. The
  false hints were noise in the pools, not harm at this budget.
* **Twee needs no SFDF pass.** Completion draws no inferences from the negated goal, which is only
  rewritten. So proof lemmas follow from the axioms plus the flattening definitions, which are
  conservative. The exception is conditional goals, now handled by HINTS-HYP.
* **Demodulation-free hints do not fit twee.** Twee normalises every pair before matching, so unnormalised
  steps would never match. Back-demodulated hints and requeue are its counterpart.
* **The Prover9 control did not use SFDF hints** either (p9loop.py drops the denial-side clauses).
  * Of 120 Prover9 proofs, 99 were already strictly forward.
  * 327 of 734 steps used demodulation, so SFDF might have helped Prover9 a little.
* **Abstract time removed the load noise.** It is the standard comparison from here on (feedback: compare
  by inferences, never wall time). Real time is a cost, to be measured on its own: abstract time leaves out
  the overhead of the model and of hint matching.
* The noise figures before 13 Nov 09:30 (±3 on 345, ±20 on 3,052) were load noise. Later noise comes from
  differences in what the loop proved earlier, not from timing.

**Decision and next.** HINTS-HYP in pools; `--abstract-time 2000` in every run from here on. REPORT 2j, 2k.

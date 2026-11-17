# Parental guidance with the sum filter, on 200 hard goals

**Question.** Does a parental prefilter help twee? The user, 17 Nov 15:52: Veroff limits generated clauses by
weight, and E has "parental guidance" (FroCoS 2021), "a quick prefilter throwing out bad generated clauses";
15:54 "go ahead with parental guidance". The cheapest parent score we have needs no training: the rule
model's raw score q of the critical pair each parent rule came from.

**Setup.**
* twee `--pg-threshold P`: no critical pairs of a new rule with an active rule when sigmoid(q1 + q2) < P.
  Rules without a score are always paired: axioms, interreduced rules, rules of a loaded state.
  * Builds: twee-e46 (P 0.047–0.269) and twee-e48 (P 0.4–0.95). The freezer (from e47) acts only when the
    queue empties, which 5 s runs never reach. From e51 the check sits after the overlap is found, as in E (2026-11-17-pg-learned-dense.md),
    with the same pairs made.
  * The thresholds 0.047, 0.119 and 0.269 are sigmoid(−3), sigmoid(−2) and sigmoid(−1). The first try
    (pg/tm/pgtest.sh) passed logits; the option parser read "−3" as an option, so the flag became a
    probability.
* Testbed: /project/hintwork/pg/tb.
  * The goals (tb/f200 = tb/all.goals): 200 goals drawn at random (seed 5) from those the 2-hour half1 run
    ORD never proved and whose 5 s first runs had failed (17 Nov 14:21).
  * The commands (tb/cmds.all): those goals' twee commands captured by rerunning them in ORD's final
    context: lemmas, hints, rm4t, 5 abstract s, twee-e43 (loop dir RT, `LOOP_PRINT_CMD=1 LOOP_KEEP_TMP=1`).
  * So it is a set chosen because the current system fails it, and any change tends to win a few. Model
    tweaks such as `--rule-threshold` won about +5.
* Runner: pg/tm/var46.py and var48.py (binary set inside); scripts pg/tm/pgtest2.sh (done before 16:54, since
  abs/pg_ab.sh quotes it) and pgtest3.sh (after 17:00), 4 workers. CPU is user + sys of each twee process, under load 20–30.

**Results** (proved of 200; CPU summed over the 200 runs):

| P | CPU s | proved | gained / lost against base |
|---|---:|---:|---:|
| off (base) | 749–843 | 29 | |
| 0.047 | 715 | 40 | +12 −1 |
| 0.119 | 686 | 43 | +16 −2 |
| 0.269 | 737 | **52** | +23 −0 |
| 0.4 | 831 | 49 | +21 −1 |
| 0.6 | 960 | 48 | +21 −2 |
| 0.8 | 1,046 | 45 | +20 −4 |
| 0.95 | 1,067 | 45 | +20 −4 |

* On the 29 runs base proves, the 0.269 filter keeps 32% of the generated overlaps. It keeps 80% of the
  parent pairs of the old proofs' steps (where both parents have a score).
* In pgtest5, run later under different load, the same base and 0.269 runs proved the same 29 and 52
  (abstract time makes runs deterministic). CPU was 933 and 993 s.

**Reading.**
* +23 −0 at 0.269 on 200 goals is far beyond the testbed's noise: tweaks moved it by about 5. But the set is
  biased towards changes winning, so this says "promising", not "better at scale". The scale test is the
  half1 A/B (2026-11-17-pg-ab-half1.md).
* Why it can win at a fixed abstract budget: abstract time counts pairs selected, not pairs made, so the
  filter changes which pairs get selected. The extra proofs are new proofs, not the old ones made cheaper
  (80% of the old proofs' parent pairs survive, yet 23 new goals fall).
* CPU barely moves at 0.269. Skipping pair generation saves time, but the runs then go elsewhere for the same
  abstract budget. At P ≥ 0.6 CPU rises; I have not looked at why.

**Decision and next.** 0.25 for the half1 A/B and production (abs/ul41.sh from 17:25). Learned parental
models: 2026-11-17-pg-learned-dense.md and 2026-11-17-pg-pcat-enigma.md. REPORT 2av.

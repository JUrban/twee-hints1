# Conditional proofs of the unsolved goals: hard steps or blocked ones? (exp: COND1)

Written 23 Nov 2026, 05:00 UTC, at the launch.

## Question

The 3,412 goals not in the trusted list (22 Nov 21:39) sit in the tails of 93 of the 129 originals, mixed with
solved ones (in 90 of the 93 the tail from the first unsolved goal has solved goals too). AIM60k's goals are steps of
Prover9's proofs, so each is true and follows from the steps before it. Is an unsolved goal hard in itself (twee
cannot bridge it even from its predecessors), or only blocked (it falls once some unsolved predecessors are given)?
If most are blocked by a few, those few are where long runs should go, ranked by how many goals they unblock; if most
are hard steps, the frontier has no such keystones.

## Setup

* exp/condprove.py, run by abs/cond1.sh (exp/cond1.sh), 6 threads, into /project/hintwork/cond/COND1, outside
  loops/: no loop, proofq, trust.py or the packer reads it, so no conditional proof reaches production or the totals.
* Each unsolved goal (sets/all minus loops/TRUSTNOW/t2139.trusted) with its 10 nearest earlier goals of its original
  as axioms lemma_goal_J, proved or not (lemmas.lemma_problem with every goal counted), and the 30 nearest trusted
  goals by kNN (lemmas.LemmaIndex, subsets) as lemma_knn_I_<goal>.
* One plain twee run: /project/bin/twee-pg61 with TWEE_PG_ARGS unset, so twee-e61 without production's PG threshold
  and ground-joining branch limit; --max-time 5 --abstract-time 2000 --no-resume-requeue --no-eqhint-consider,
  --quiet --no-proof; no rule model, no hints. A proved run is rerun with the proof printed (COND1/proofs/<goal>); its
  used lemma_goal_J split into unproved and proved.
* Smoke (12 random unsolved goals, 05:00): 3 proved, each using unproved siblings (goal_524; goal_272; 468, 473, 475).

## Readings

* Hard steps: no proof even with the predecessors assumed (at 5 s, plain).
* Blocked: proved using unproved siblings; the blockers, and a goal's reach through the blocking graph.
* Unconditional: proved using no unproved sibling (a new proof; checked by hand before anything uses it).

## Result (05:26; COND1 ran 05:00:45-05:23:10)

exp/condgraph.py cond/COND1 (exp/condgraph.py adds the Prover9 proof-line gap from abs/goal_lines.tsv):

* **3,412 unsolved goals: 2,826 hard (83%), 585 blocked (17%), 1 unconditional.** Most unsolved goals
  are hard steps: even with their 10 earlier siblings given, a plain 5 s run does not bridge them.
* The blocked goals' blockers, by class: hard 843, blocked 285. Unproved siblings used per blocked goal: 1: 293, 2: 143, 3: 89, 4+: 60.
  354 blocked goals have only hard blockers.
* **No keystones.** Reach (blocked goals that fall, to a fixpoint, once one goal is proved): hard goals >=1 184, >=5 5, >=20 0; the top 10: [10, 7, 6, 5, 5, 4, 4, 4, 4, 4];
  blocked goals >=1 58, >=5 3, >=20 0; the top 10: [7, 6, 5, 4, 3, 2, 2, 2, 2, 2]. All hard goals proved would free the 585 blocked ones, and no single goal frees more than 10.
* **The hard steps are the long ones.** AIM60k samples each Prover9 proof every 3 lines at first, then every 5, 8,
  13, 21, 34 and 55 (REPORT 2z); every unsolved goal is 8 or more proof lines after the previous goal. Proved
  (blocked or unconditional) by lines from the previous goal: 0-1: 0/0; 2-3: 0/0; 4-7: 0/0; 8-15: 58/177 (33%); 16-31: 107/451 (24%); 32-: 421/2784 (15%).
* Hard goals by original, the top 10: nslm_to_aa1 354, nsmr_to_aa1 168, R1dist_to_aa1 111, aK2_eq_aK3_a 82, aK2_eq_aK3_gen 82, aK2_eq_aK3_d 75, com_Ralt 74, ns_to_aa1_b 74, nsmr_to_aK1 73, aK2_eq_aK3_b 68.

| goal | class | reach | blockers |
|---|---|---:|---|
| com_Ralt__goal_254 | hard | 10 | - |
| com_Ralt__goal_338 | blocked | 7 | 331,335 |
| im2_24_to_25__goal_471 | hard | 7 | - |
| com_Ralt__goal_261 | blocked | 6 | 254 |
| nsmr_to_aa1__goal_738 | hard | 6 | - |
| aK2_eq_aK3_j__goal_430 | hard | 5 | - |
| nil3_1K_e__goal_466 | hard | 5 | - |
| nil3_23_32_to_26__goal_502 | blocked | 5 | 495,496 |
| aK2_eq_aK3_h__goal_316 | hard | 4 | - |
| aK2_eq_aK3_j__goal_457 | hard | 4 | - |
| nil3_23_32_to_26__goal_510 | blocked | 4 | 502 |
| nil3_32__goal_466 | hard | 4 | - |
| nslm_to_aa1__goal_1013 | hard | 4 | - |
| nslm_to_aa1__goal_964 | hard | 4 | - |
| nsmr_to_aa1__goal_706 | hard | 4 | - |
| KK_Kcom_to_aK1__goal_284 | hard | 3 | - |
| aK2_eq_aK3_1243b__goal_588 | hard | 3 | - |
| aK2_eq_aK3_gen__goal_539 | hard | 3 | - |
| aK2_eq_aK3_gen__goal_616 | hard | 3 | - |
| aK2_eq_aK3_o__goal_493 | hard | 3 | - |

* **The one unconditional proof**, nil3_30__goal_473 (2.05 s; siblings 464 and 468, both trusted, and 9 kNN lemmas of
  trusted goals; cond/COND1/proofs/nil3_30__goal_473), is a goal production never proved. loop.py does not reproduce
  it: abs/cu2.sh (exp/cu2.sh) in the trusted context (loops/ULT.ctx: the 48,372 trusted goals as round 0, hints ->
  loops/UL/hints), the same 10 sibling and 30 kNN lemmas, plain twee, no rule model, 5 s: NO, with 8,504 hints, which
  COND1's run did not have. (abs/cu1.sh took --init loops/UL, which imports only round-0 rows, 33,720 goals; abs/cu3.sh
  with --max-hints 0 ran nothing.) Not entered into production: one goal, and it has no loop record for trust.py.
* A smoke check on 9 of the hard goals at 40 s (instead of 5 s), the same problems: 1 proved.

## Decision

No keystone targeting: the frontier is about 2,800 hard steps, 2,784 of the 3,412 unsolved goals 32 or more Prover9
proof lines after the previous goal, and none frees more than 10 others. "Hard" here is at 5 s, plain twee, without
the rule model, hints or variants; with those some would fall from their siblings, but that does not make keystones
of them. Progress there needs stronger single-step proving (longer runs, better lemmas and hints
for one step), not a different order. COND1's proofs stay in cond/COND1, outside loops/.

## Step test bed (launched 05:28)

COND1's hard goals with their siblings assumed are a fast bed for anything meant to prove long steps: a proof there
is conditional, but a setting that bridges more of them from their predecessors should help production's real
attempts. sets/hardstep300 (exp/sets/hardstep300): 300 of the 2,826 hard goals (seed 23); COND1's setting proved
none. abs/stepbed1.sh (exp/stepbed1.sh) runs exp/condprove.py with one change per arm, 6 threads, one arm at a time:

| arm | change | cost |
|---|---|---|
| KNN29 | 29 kNN lemmas instead of 30: a perturbation control (what any change proves by chance) | 1 |
| SIB30 | 30 earlier siblings | 1 |
| AFT10 | also the 10 nearest later siblings (true as well) | 1 |
| KNN100 | 100 kNN lemmas | 1 |
| SIB3 | 3 earlier siblings | 1 |
| T20 | 20 s instead of 5 | 4 |

Reading: each arm's proofs against KNN29's; an arm is a lead only well above the control.

Batch 1 so far (05:37; parsed from cond/STEP.done): KNN29 1 of 300, SIB30 41, AFT10 51; 0 unconditional among them. 41 of
the 41 SIB30 proofs used a sibling more than 10 goals back: a long step's parents are 11-30 goals earlier, so COND1's
10-sibling window called too many goals hard, and its "no keystones" needs a recheck.

Batch 2 was replaced before it started (05:37): abs/stepbed2.sh (exp/stepbed2.sh) now runs, after batch 1,
* **COND2:** COND1 with 30 earlier siblings (earlier only, so the blocking graph stays well-founded), all unsolved
  goals, cond/COND2; then exp/condgraph.py again;
* batch 2 on SIB30's problems (30 earlier siblings, 30 kNN, 5 s): S30KNN29 (control), S30GH `--goal-heuristic`,
  S30HG `--hint-goal`, S30BG2 `--backwards-goal 2`, S30FGL `--no-flatten-goal --flatten-goal-lightly`, S30KW0
  `--kbo-weight0`, S30FLIP `--flip-ordering`, S30GJB `--ground-joining-branch-limit 100`.

## Walls, and where production's CPU goes (05:38)

A wall here is an unsolved goal whose 30 nearest earlier siblings are all trusted: a run on it with its siblings is a
real attempt, not a conditional one. 99 of the 3,412 unsolved goals are walls (sets/walls30, exp/sets/walls30);
COND1 proved 1 of them (nil3_30__goal_473). The rest have unproved goals among their 30 earlier siblings.

exp/wallcpu.py (loops/UL/r5/results.tsv: the last 30,000 rows; walls 99):

| goals | runs | CPU h (share) | THM | THM per CPU h |
|---|---:|---:|---:|---:|
| unsolved, 6+ of 30 earlier unproved | 24,242 | 68.5 (75%) | 24 | 0.35 |
| unsolved, 1-5 of 30 earlier unproved | 4,645 | 17.6 (19%) | 5 | 0.28 |
| wall | 883 | 4.2 (5%) | 0 | 0.00 |
| trusted at the list's time | 230 | 0.6 (1%) | 14 | 22.21 |

Production's recent proofs come from goals deep in unproved stretches, at the same low rate as the rest, through the
cross-original lemmas (kNN, transfer), not from the walls. Its 40-sibling variant (Vs40@0: 11,911 runs in loops/UL's r*/results.tsv)
already reaches the far parents where they are proved. So extending the chains at the walls is not where production
stands to gain either.

## Step test bed, batch 1 (ended 05:56; parsed from cond/STEP.done)

| arm | change from COND1's setting | proved | per unit of cost | unconditional |
|---|---|---:|---:|---|
| KNN29 | 29 kNN lemmas (control) | 1 of 300 | 1.0 | - |
| SIB30 | 30 earlier siblings | 41 of 300 | 41.0 | - |
| AFT10 | +10 later siblings | 51 of 300 | 51.0 | - |
| KNN100 | 100 kNN lemmas | 12 of 300 | 12.0 | aK2_eq_aK3_c__goal_479 |
| SIB3 | 3 earlier siblings | 4 of 300 | 4.0 | - |
| T20 | 20 s | 47 of 300 | 11.8 | - |

* Siblings matter most: 30 earlier ones (SIB30) or 10 later ones as well (AFT10) prove 40-50 times the control, at
  the same cost; four times the time (T20) about as many as SIB30 at four times the cost. Three siblings (SIB3) are
  within what a perturbation proves. More kNN lemmas (KNN100) help some.
* The one unconditional proof, aK2_eq_aK3_c__goal_479 (KNN100; SIB30 and T20 proved it too, conditionally: unproved siblings 451,476 and 473,475,476), used 12 kNN
  lemmas, 8 of them ranked 30 or beyond, and 0 siblings; production never proved it although it has k100-k1000 members.
  With COND1's nil3_30__goal_473 that is two new proofs from plain runs (no rule model, no hints): see below.

## Plain runs as real attempts: PLN1 (launched 05:58)

Two goals production never proved fell to plain runs here (nil3_30__goal_473 in COND1, aK2_eq_aK3_c__goal_479 in
KNN100): no rule model, no hints, no PG, only lemma axioms. Production's members all carry hints, and its model ones
the rule model too. Is a plain member worth adding? PLN1 (abs/pln1.sh, exp/pln1.sh) runs every unsolved goal once,
5 s, with only trusted siblings (30 earlier and 10 later, exp/condprove.py --proved) and 100 kNN trusted lemmas, so
every proof is a real one. 4 threads, cond/PLN1. Reading: new proofs per CPU hour against production's 0.35 on the
same goals (exp/wallcpu.py). If it pays, the proofs go into production through a loop record (rerun with loop.py's
--print-hints --print-given, USEDAXIOMS, then merge.py), and loop.py gets a plain variant.

PLN1's first proof (06:01), aK2_eq_aK3_a__goal_520 in 0.79 s: a goal production never proved. Its record
(USEDAXIOMS) names 5 trusted siblings (493, 495, 504, 507, 512) and 15 kNN lemmas, 9 of them ranked 30 or
beyond. exp/condimport.py (06:02) reran it into loops/CI1 the way loop.py runs it: kept output r1/out/<goal> with
RESULT and USEDAXIOMS, 73 canonical hints, solved.tsv row, the printed proof. merge.py loops/UL loops/CI1 takes such dirs into
production (UL/hints, UL/out for trust.py, a solved.tsv row that the live loop's --sync reads). The merge waits
for PLN1's end, all its proofs at once.

## loop.py's plain variant (06:14)

loop.py `--variants pl[kN][sM]` (this commit): a plain run, no hints, no rule model, no PG (as nopg), with kN kNN and
sM sibling lemmas as for kNsM. Smoke abs/plsmoke2.sh (exp/plsmoke2.sh; abs/plsmoke.sh first: without a prior the
level never came up in 3 minutes): solve_new.sh on sets/plsmoke (3 goals) in loops/ULT.ctx, 1 worker, 0.05 h,
`--variants plk100s40@0,unf@0 --priors Vplk100s40@0=9,...`; loops/PLS2, no traceback.

| goal | level | result | wall s |
|---|---|---|---:|
| aK2_eq_aK3_a__goal_520 | L0 | NO | 10.22 |
| aK2_eq_aK3_a__goal_616 | L0 | NO | 7.52 |
| nil3_32__goal_490 | L0 | NO | 5.79 |
| aK2_eq_aK3_a__goal_520 | Vplk100s40@0 | THM | 1.26 |
| aK2_eq_aK3_a__goal_616 | Vplk100s40@0 | NO | 3.53 |
| nil3_32__goal_490 | Vplk100s40@0 | NO | 2.78 |

The plain level proves PLN1's goal inside the loop where production's L0 does not, and its failed runs take a third of
L0's wall time (no model, no hints to match).

## From zero: PLZ8 (queued 06:20)

Would a plain member help a from-zero run's late phase? abs/plz8.sh (exp/plz8.sh), after PLN1: PLN1's setting on
2,000 of Z8's unsolved goals (sets/z8un2000, exp/sets/z8un2000, seed 88) in Z8's final context (42,920 goals of
loops/Z8F.ctx as the trusted list), 4 threads, cond/PLZ8. Reading: proofs per CPU hour against Z8's own late 5 s
retries (r1/results.tsv, t= in hours 4-6: L0 535 proofs in 4,759 runs, 6.64 CPU h, 81 per CPU h; all its main-loop runs
635 in 6,232, 55 per CPU h). Well above: a plain level goes into solve_new.sh's
variants, through an A/B.

## COND2: 30 earlier siblings (ran 05:56-06:21; read 06:41)

| | hard | blocked | unconditional |
|---|---:|---:|---:|
| COND1 (10 siblings) | 2,826 | 585 | 1 |
| COND2 (30 siblings) | 2,484 | 925 | 3 |

* Reach (exp/condgraph.py cond/COND2): hard goals >=1 177, >=5 8, >=20 0; the top 10: [11, 10, 9, 9, 8, 7, 6, 6, 4, 4]; blocked >=1 79, >=5 6, >=20 0; the top 10: [8, 8, 6, 6, 6, 5, 4, 3, 3, 3].
* By Prover9 proof lines from the previous goal: 0-1: 0/0; 2-3: 0/0; 4-7: 0/0; 8-15: 78/177 (44%); 16-31: 156/451 (35%); 32-: 694/2784 (25%).
* Still no keystones: with 30 siblings assumed 73% are hard steps, and no single goal frees more than the top of
  the list below. (com_Ralt__goal_254 leads it; production's own com_Ralt streak this morning was about that size.)
* COND2's unconditional proofs: aK2_eq_aK3_a__goal_520, aK2_eq_aK3_j__goal_435, nil3_30__goal_473; 3 of them PLN1 proved too (COND2's problems carry
  unproved siblings, so condimport.py takes only PLN1's).

| goal | class | reach | blockers |
|---|---|---:|---|
| com_Ralt__goal_254 | hard | 11 | - |
| nslm_to_aa1__goal_947 | hard | 10 | - |
| aK2_eq_aK3_j__goal_401 | hard | 9 | - |
| ns_to_aa1_b__goal_617 | hard | 9 | - |
| aK2_eq_aK3_j__goal_411 | blocked | 8 | 401 |
| nslm_to_aa1__goal_950 | blocked | 8 | 947 |
| nsmr_to_aa1__goal_738 | hard | 8 | - |
| ns_to_aK1__goal_514 | hard | 7 | - |
| aK2_eq_aK3_j__goal_430 | blocked | 6 | 411 |
| im2_24_to_25__goal_471 | hard | 6 | - |
| nil3_15to7__goal_420 | hard | 6 | - |
| nil3_23_32_to_26__goal_502 | blocked | 6 | 495,496 |

## Step test bed, batch 2 (ended; read 06:54)

SIB30's problems (30 earlier siblings assumed, 30 kNN, 5 s) with one twee option each:

| arm | option | proved |
|---|---|---:|
| S30KNN29 | 29 kNN lemmas (control) | 41 of 300 |
| S30GH | `--goal-heuristic` | 41 of 300 |
| S30HG | `--hint-goal` | 42 of 300 |
| S30BG2 | `--backwards-goal 2` | 6 of 40 |
| S30FGL | `--no-flatten-goal --flatten-goal-lightly` | 42 of 300 |
| S30KW0 | `--kbo-weight0` | 40 of 300 |
| S30FLIP | `--flip-ordering` | 39 of 300 |
| S30GJB | `--ground-joining-branch-limit 100` | 41 of 300 |

* No option bridges more long steps than the control. S30BG2 has no result: twee with `--backwards-goal 2` ran past
  the abstract-time limit (one run 10 minutes, another killed at 8 minutes and 5.8 GB); condprove.py's subprocess
  timeout then ended the arm after 40 rows (condprove.py now writes TIMEOUT rows instead).
* What bridges long steps is the lemmas (siblings far back, many kNN lemmas), not twee's search options.

## Totals after PLN1 (06:54)

exp/trust.py loops/TRUSTNOW/t0641 (-j 2, --exposed loops/UNSOUND/exposed.txt): **48,466 trusted, 0 untrusted; holdout
5,393 of 5,880**. All 24 goals of loops/CI1 are trusted.

## Plain live loop (started 06:55)

The plain member runs beside production instead of in it (no restart of production): abs/plainlive.sh
(exp/plainlive.sh), started by abs/plainlive_start.sh (exp/plainlive_start.sh, PID in cond/PLNL.pid) once PLN2 has
ended and its proofs are imported (loops/CI2) and merged. Each cycle (at most one every 30 minutes, 3 threads):
* the trusted context: the goals of loops/UL/solved.tsv (production's solved list; trust.py checks it later, as it
  does production's own proofs; 0 untrusted at 06:41);
* exp/condprove.py --proved, PLN1's setting, `--prev` the cycle before: only goals whose problem changed (a new
  sibling or kNN lemma) are run, the rest are SAME rows;
* exp/condimport.py into loops/CI2, then merge.py loops/UL loops/CI2; production's --sync takes the rows in.
Log cond/PLNL/log, one line a cycle. Stop: touch cond/PLNL.stop (it ends after the cycle).

## PLZ8 result (ran 06:40-07:09)

160 of 2,000 of Z8's unsolved goals proved in Z8's final context, 1.88 CPU h of twee runs: **85 per CPU h** (8.0% per
run), against Z8's own L0 retries in hours 4-6 at 81 and all its main-loop runs then at 55. All 160 are goals production has
proved (1,250 of the 2,000 are); none of the others. On goals the from-zero run had tried and failed, a
plain run proves as much per CPU hour as the best late level does on its own picks: exp64 (notes/2026-11-23-plain-level.md).

## Wide plain sweep (armed 07:13)

abs/plw1.sh (exp/plw1.sh): once PLN2 has ended, one sweep of production's unsolved goals with a wider lemma set:
100 earlier and 30 later trusted siblings and 400 kNN lemmas (PLN1/PLN2: 30, 10, 100), plain 5 s, 3 threads,
the context production's solved list at its start (cond/PLW1.trusted). Its proofs go into loops/CI3 and loops/UL
as PLN1's did. Read: its proofs against PLN2's on the same goals, the union, and the proofs per CPU h; the step
bed's SIB30 and AFT10 suggest that more siblings bridge more.

## PLN2 (ran 06:54-07:17; read 07:18)

PLN1's setting in the context of t0641 (48,466), `--prev cond/PLN1`: 1,778 goals had the same problem as in PLN1 and
were not run; 1,540 were run, 5 proved (com_Ralt__goal_387, lra2aa__goal_352, lra2aa__goal_382, ns_to_aa1_c__goal_393, ns_to_aa1_c__goal_394), 1.10 CPU h, 4.5 per CPU h. All 5 imported into loops/CI2
and merged into loops/UL (07:17). The second pass yields about half of the first per CPU h, still more than ten
times production's.

## Hint bed (started 07:20)

Do hints help or hurt plain frontier runs? exp/condprove.py `--hints-lemmas CAP` adds the hints of the problem's
lemma goals (loops/UL/hints/<goal>: their proofs' steps; the siblings nearest first, then the kNN lemmas by rank)
as twee's `--hints-file`, the problem text unchanged.
* Smoke test (cond/HBSMOKE): PLN2's 5 proved goals on PLN2's exact problems with 2,000 such hints: 2 of 5
  proved (plain: 5 of 5).
* abs/hintbed.sh (exp/hintbed.sh): 600 goals plain failed in PLN2 (sets/hintbed600, seed 64), PLN2's problems,
  5 s, 3 threads; arms HBC (a perturbation control: `--abstract-time 1990`), HB200 and HB2000 (`--hints-lemmas`).
  Gains over plain are counted against HBC's.

## What the plain proofs used (read 07:22)

The 29 plain proofs of PLN1 and PLN2, by their proofs' Axiom lines, against production's base lemma set
(`--lemmas 6 --lemma-knn 30`): 23 used an earlier trusted sibling beyond the 6 nearest, 11 a later sibling, 27 a kNN lemma
ranked 30 or beyond; **29 of 29 used at least one of these**. Production's variants widen one of these at a
time (s40@0, s200@0, k100@0, k200s12@0, ...), always with the original's hint pool. The plain runs widen all at
once and have no hints: the hint bed separates the two.

## Two settings (armed 07:48)

PLW1 so far: 14 proofs in its first 1,541 goals, 11 of them not among PLN2's. The settings
complement each other, so the live loop runs both: abs/plainlive2.sh (exp/plainlive2.sh) runs N (30+10 siblings,
100 kNN) and W (100+30, 400 kNN) each cycle, each with its own `--prev` chain (cond/PLNL/c<k>N, c<k>W). Starter
abs/plainlive2_start.sh (PID in cond/PLNL2.starter): after PLW1's import it stops plainlive.sh (cond/PLNL.stop, after its
cycle) and starts plainlive2.sh with PREV_N its last cycle and PREV_W cond/PLW1.

## Sweep queue (armed 07:49)

The live loop runs only changed problems, so it is idle most of each cycle; new proofs also come from new settings.
abs/sweepq.sh (exp/sweepq.sh, PID in cond/SWEEPQ.pid) runs the full plain sweeps of cond/SWEEPQ.txt (copy
exp/sets/SWEEPQ.txt) one after another after the hint bed, 3 threads, each in the context of loops/UL/solved.tsv at
its start, with its proofs into loops/CI3 and loops/UL (merges under flock cond/merge.lock, as plainlive2.sh's):

| sweep | condprove.py arguments |
|---|---|
| PLK1 | `--time 5 --sibs 30 --after 10 --knn 400` |
| PLS1 | `--time 5 --sibs 100 --after 30 --knn 100` |
| PLM1 | `--time 5 --sibs 60 --after 20 --knn 200` |
| PLT1 | `--time 20 --sibs 30 --after 10 --knn 100` |

With N (PLN2) and W (PLW1) they separate the dimensions: kNN alone (PLK1), siblings alone (PLS1), between (PLM1), and
four times the time (PLT1). Read: each sweep's proofs, those no other sweep found, and proofs per CPU h.

## Hint bed result (07:20-07:54; read 07:55)

| arm | proved | CPU h |
|---|---:|---:|
| HBC | 0 of 600 | 0.39 |
| HB200 | 0 of 600 | 0.42 |
| HB2000 | 1 of 600 | 0.87 |

On 600 frontier goals plain runs had failed, the hints of the lemma goals' own proofs add nothing: 0 with 200, 1 with 2,000
at twice the CPU (the control 0). With the smoke test (2,000 hints lost 3 of 5 plain proofs), hints hurt more
than they help on the frontier; **the lemma set is what proves these goals**. HB2000's proof (aa2_to_aa3__goal_267) went
into production through loops/CI4 (condimport.py now reruns a hinted sweep's proof with its hints file).

## Which lemmas the plain proofs used (read 07:56)

| sweep | proofs | sibling lemmas used | kNN lemmas, same original | kNN lemmas, other originals | lemmas per proof (median) |
|---|---:|---:|---:|---:|---:|
| PLN1 | 24 | 86 | 19 | 181 | 10 |
| PLN2 | 5 | 17 | 2 | 20 | 6 |

Most kNN lemmas a proof uses are goals of other originals with the same or weaker axioms: what other Prover9 proofs
established bridges these steps, beside the original's own earlier steps.

Added 07:58: condprove.py `--index kd|kp`, loop.py's other kNN selections (kd: MaSh-style proof dependencies;
kp: similarity weighted by lemma use counts), as PLD1 (after PLK1) and PLP1 in the queue, at N's sizes. Smoke test
on PLN2's 5 proofs: kd replaced most of the 100 kNN lemmas and proved 4, kp about a quarter and proved 5.

## PLW1 result (07:17-08:24; read 08:27)

23 proofs of 3,318 goals in 3.28 CPU h, 7.0 per CPU h; 18 not among PLN2's 5, and all of PLN2's 5 among them
(`exp/condcmp.py cond/PLN2 cond/PLW1`; PLN2's CPU counts only its changed problems). condimport took 23 of 23, merge.py
16 (the others production had by then, from PLN2 and HB2000). On this context the wide setting finds every proof the
narrow one finds and more, at a higher rate. The live loop runs both (plainlive2.sh since 08:27).

Queue changed 08:28: W contains N's proofs, so W is the baseline: PLK1 (N's siblings, W's kNN) and PLS1 (W's siblings, N's
kNN) split it; kd, kp and 20 s run at W's sizes; PLM1 is dropped. PLX1 (200+60 siblings, 1,000 kNN) proved 2 of PLN2's 5
in a smoke test (cond/XSMOKE) at 7.4 s a run, so it comes last.

## PLK1 result (07:54-08:55; read 08:56)

N's siblings (30+10) with W's 400 kNN: 16 proofs of 3,313; condimport took 3 (the rest were PLW1's, already in loops/CI3),
merge.py 2. On the goals both ran (exp/condcmp.py cond/PLW1 cond/PLK1):

3,313 goals in all of cond/PLW1, cond/PLK1
| dir | proved | CPU h | per CPU h | + vs cond/PLW1 | − vs cond/PLW1 | only here |
|---|---:|---:|---:|---:|---:|---:|
| cond/PLW1 | 18 | 3.28 | 5.5 | 0 | 0 | 5 |
| cond/PLK1 | 16 | 2.98 | 5.4 | 3 | 5 | 3 |
union 21

The 400 kNN lemmas give most of W's gain over N; W's wider siblings add the rest, and PLK1 still has proofs of its own.

## Where the used kNN lemmas rank (read 08:56)

The kNN lemmas the 400-kNN sweeps' proofs used, by their rank in the problem's list:

| sweep | proofs | 0-49 | 50-99 | 100-149 | 150-199 | 200-249 | 250-299 | 300-349 | 350-399 | proofs using one ranked 300+ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| PLW1 | 23 | 50 | 63 | 50 | 45 | 43 | 36 | 25 | 24 | 15 |
| PLK1 | 16 | 49 | 57 | 30 | 41 | 29 | 20 | 19 | 19 | 14 |

Almost flat: the similarity ranking (idf-weighted Jaccard of goal features) carries little signal about which lemmas a
proof needs, and most proofs need one from the bottom quarter. A better ranker could bring lemmas now ranked
beyond 400 into the list, which widening cannot (PLX1's 1,000 make twee slower). PLD1 (kd, MaSh-style) and PLP1
(kp, use counts) test the two rankings production has. If either beats W, a learned ranker comes next: positives are the
used lemmas of the plain, conditional and step-bed proofs (cond/*/p and proofs), negatives the unused ones of the same
problems.

Queue held (09:24): PLD1, PLP1, PLT1 and PLX1 are commented out (`#held`) in cond/SWEEPQ.txt. With exp64 in Z9's slot,
production, exp64, the live loop and PLL1 already come to over 20 CPUs. The live loop's W cycles are nearly full
sweeps: c4W reran 1,883 changed problems (206 SAME) for 2 proofs so far, as a few new proofs change most 400-lemma lists.

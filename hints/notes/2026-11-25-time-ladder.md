# The time ladder over all unsolved goals (25 Nov 15:08)

## Why (the user)

* The user: the later goals are harder, so they need more time; if 5 s runs ran out of steam, longer runs are the
  default idea. "just use some common sense".
* The facts (15:00): of the 1,988 unsolved goals, the longest single run each ever had: under 1 min 24, 1-5 min 628,
  5-17 min 1,260, 17-33 min 49, over 33 min 27. All attempts together: median 0.34 CPU h per goal (q90 0.74, max 4.7;
  878 CPU h in all). Production's main loop since 24 Nov 11:23: 5 s fresh runs 22% of its CPU, 5 s members 37%, 40 s
  runs 39%, its 80-320 s levels 17 runs (under 1%): its scheduler ranks run kinds by recent proofs per CPU h, which
  favoured short follow-up runs while proofs came in chains, and kept doing so when they stopped.
* My errors: I called this "stuck" and "out of targets", and stopped exp86's long finals (0.37 per CPU h) by a fixed
  threshold while its CPUs would have stood idle. The right comparison for a CPU is its other use, not a constant.

## Setup

Long runs go through the climbers (they write proofs into loops/UL with hints, so production's follow-ups and every
later run use them); production's scheduler is left as it is. Two rungs on disjoint goal sets, nearest proved goal
below first, sharing the 20-process budget (each starts a run only while fewer than 20 twee processes run):
* **160 abstract s (320,000 pairs):** CLS71 (from 14:58, notes/2026-11-23-climber-restart.md) on every unsolved goal
  with fewer than 2 CLS71 finals (1,465: 893 once climbed, 572 never; the A/B halves climb or final-only), -j 10.
* **640 abstract s (1.28M pairs, --max-cpu 6400):** CLQ83, final only (abs/clq87.sh, exp/prod/side/clq87.sh; climb.py
  4157884 from 15:08:07; log line 2103, climb.tsv row 2093 on) on sets/ladder640.re (exp/sets/ladder640.re, 561 goals:
  512 with two failed 160 s CLS71 finals, 49 exp86 heads that failed 160 s), `--reclimb-max 3` (new climb.py option,
  default 2: the exp86 heads already had two CLQ83 finals), -j 5. First: nslm_to_aa1__goal_1138.
* Next rungs: CLS71's failures of this pass go to 640 s, the 640 s failures to 2,560 s, by restarting with new lists.
* Reading: proofs and CPU h per rung (climb.tsv finals from the rows above), and what the new proofs open (production's
  follow-ups). Memory: 1.28M-pair runs may grow to several GB; watch the total (60 GB).
* 15:09: the 640 s rung got 1 slot (CLS71 held 10 under the 20-process gate), so it was restarted with CPUS=23 (climb.py
  4158240, bash 4158234, from 15:09:11; log line 2106, climb.tsv row 2093 on): 5 finals at once, 22 twee processes in
  all; CLS71's own gate (20) lets it shrink as its climbs end. About 3 CPUs over the usual 20, for climbing.

## The 640 s rung climbs (15:22; the user)

* The user: "since you said that hints do not help with the current hard goals, shouldn't the climbers really be a major
  weapon for those? because the climbers basically do create on-demand hints from the strengthened theory". First a
  correction: I had not shown that hints do not help; the plain live loop (no hints) made the most of the last 52
  proofs, an observation, not an ablation.
* The climbers' record: the final-only A/B says a target's own climb adds little (new targets 19.9% against 17.7%
  proved, 1.44 against 1.57 per CPU h), but the final-only arm still uses the sketch hints and fill lemmas of earlier
  climbs of its original (44,711 sketch hints and 2,832 true lemmas reloaded at 14:58), so it measures one more climb,
  not climbing. Fill lemmas are in 85% (CLQ83) and 94% (CLS71) of the climbers' proofs.
* For the hardest goals, where time alone gave 0.37 per CPU h (exp86), new on-demand hints are what can change the
  outcome, and the climb (20 sketch runs of 5 s, 3 s fills) is cheap next to a 640 s final. So the 640 s rung now climbs:
  abs/clq87b.sh (exp/prod/side/clq87b.sh; abs/clq87.sh with `--runs 20`), CPUS=23, climb.py 4159470 (bash 4159464)
  from 15:22:17; log line 2109, climb.tsv row 2093 on (no final finished before). The 160 s rung (CLS71) keeps its A/B.

## The climbers' hints in the global hint store (15:29-15:35; the user)

* The user: "I hope you are keeping the hints from the strengthened-theory runs in your global hint db?" Checked:
  real proofs' hints all go into loops/UL/hints; production's sketch members (`--climb-hints`) read CLS71's sketches and
  fill lemmas (rescanned every 10 minutes); each climber reloads only its own dir. Gaps: (1) loops/CLQ83 was not in
  production's --climb-hints (it made no sketches of its own until the 640 s rung started climbing at 15:22); (2) the
  climbers did not read each other's hints; (3) hintdata had no records of the climbers after 23 Nov (CLS71, CLQ83,
  CLHL3/4, CLA67/B67, CLK69, K70F/R).
* (2) climb.py `--share DIRS`: also load the sketches/ and fillhints/ of other climber dirs as hints (their true lemmas
  are not taken as axioms). The 640 s rung restarted with `--share loops/CLS71` (abs/clq87c.sh, exp/prod/side/clq87c.sh;
  climb.py 4160478, bash 4160472, from 15:29:21; log line 2112, climb.tsv row 2186 on): 45,123 sketch hints loaded
  instead of 35,824 (CLQ83's own were nearly a subset of CLS71's). CLS71 gets --share loops/CLQ83 at its next restart.
* (1) production ul85 (abs/ul85.sh, exp/prod/ul85.sh): ul84 with loops/CLQ83 in --climb-hints; loop.py 4160713 (bash
  4160707) from 15:30:10, J=4, log loops/UL85.log. Its climb hints rose from 121,325 steps and 6,036 fill lemmas to
  122,371 and 6,078 at the first rescan.
* (3) `exp/hintdata_build.py --climbs` (now skipping exp85's copies P85C/P85D), from 15:35.

## First reading (17:32; climb.tsv rows from 31466 (CLS71) and 2093 (CLQ83))

* 160 s rung (CLS71, climbs or final-only by the A/B): 148 finals, all local heads with no earlier CLS71 final, **3
  proofs** (nil3_23_32_to_30__goal_510, R1dist_to_aa1__goal_599, aK2_eq_aK3_1243b__goal_558), 22.6 CPU h: **0.13 per
  CPU h**; final median 489 CPU s.
* 640 s rung (CLQ83, climbs then the final, CLS71's hints shared from 15:29): 16 finals, **1 proof**
  (aK2_eq_aK3_gen__goal_641), 9.8 CPU h: **0.10 per CPU h**; final median 2,244 CPU s.
* The whole system 15:00-17:32: loops/UL 49,796 to 49,805. Memory: my processes 18.7 GB, the largest twee about 4 GB.
* Reading: about 10 CPU h per proof on both rungs; the counts are small (3 and 1), so the two rates do not differ. The
  ladder's logic stays: CLS71 reaches the 893 goals that already failed a 160 s climb after the remaining ~420 heads
  (about 7 hours); they should then go to 640 s, not repeat 160 s (to do at that restart, with --share loops/CLQ83).

## Do the hints slow the long runs down? (exp88, 25 Nov 17:39-18:31)

**Question.** The user: do we need to speed twee up for the long runs, does it get much slower; and: does having many
hints loaded slow the long runs down?

**Setup.** Replays of exp85's captured production runs (loops/P85C/cap: problem, lemmas, hints file, rule model; the
default precedence), twee-e61, TWEE_PG_ARGS as production. Data in loops/P85C/exp88; scripts exp/rtsrun88.py (one
capture with RTS options, or the profiling build dist-prof2) and exp/hintcost88.py (a capture with or without its
hints file; lemmas, rule model and PG kept). The production hint files here hold 7,500-10,000 hints; the 640 s rung's
finals carry a median 10,000 (5,747-26,510, 20 files).

**Results.**
* GC (nil3_23_32_to_26__goal_557 to 320,000 pairs, 48,662 rules; gc_*.out): default 617 CPU s of which GC 55 (91%
  productive), -A64m 637 (GC 15), -A256m 645 (GC 10); identical work. Not the bottleneck (as 14 Nov found).
* Profile at 160,000 pairs (prof160k.prof, 26,541 rules, inherited time): making critical pairs 59% (overlaps 49%),
  rewriting 49% (they overlap), queue renormalisation 23%, interreduction 19%; hint rewriting of each new pair's terms
  (applyHints) 7.1%, hint lookups and normalisation about 2%, the rule model's scores about 3.5%. This repeats exp80's
  finding (24 Nov: makePassives 80%, simplify 56%; no free speed-up).
* With and without the hints file, 4 goals to 160,000 pairs (hints4.tsv): 3 pairs of runs both reaching 150,000
  pairs: fewer pairs per CPU s with hints by 23%, 26%, 7%. Part is the hints' bookkeeping, part a different search (more
  rules).
* All 22 exp85 dev goals (stalled production goals that some precedence proves in 500-30,000 abstract work; all solved by
  now) without hints to 160,000 pairs (nohints22.tsv), against exp85d's hinted default runs (e85d.tsv, to 320,000):
  within 160,000 pairs **hinted 11, unhinted 10, both 7, union 14**; the unhinted run needed
  fewer pairs on 6 of the 7 both proved. Median pairs per CPU s over runs past 100,000 pairs: hinted
  887 (17 runs), unhinted 1078 (14).

**Reading.** The hints cost about 10% of a long run's CPU directly (the profile) and 10-25% per pair in all; the long
run's slowdown (about 2x per pair from 100,000 to 1.28M pairs) comes from the growing rule set (overlaps, rewriting,
renormalisation, interreduction), not from the hints. On these stalled goals the production hints did not steer
better than no hints: a complementary member, not a loss to drop (union 14 against 11). Caveat: 22 goals
selected as stalled in hinted runs, which biases against hints; but every unsolved goal is such a goal.

**Change (18:28-18:30).** climb.py `--final-nopool-ab`: the finals of targets with bit 3 of crc32 of the name set get
only the sketch hints (their own climb's, their siblings', the shared dirs'), no pool hints; independent of
--final-only-ab (bit 2). CLS71 restarted as abs/cls71g.sh (exp/prod/side/cls71g.sh; cls71f.sh ran 18:28:58-18:30:29
without --share): --final-nopool-ab plus --share loops/CLQ83 (the 47,142 sketch hints became 47,444). climb.py 13715
(bash 13712), from 18:30:29; log line 3064, climb.tsv row 33302 on. Checked on the running finals: no-pool finals
carry 395-568 sketch hints, the others 4,080-7,767 hints. Reading: finals, proofs and CPU h per arm (bit 3), split by
bit 2, from row 33302.

## exp88b: the 10 nearest siblings' proof steps as the hints (25 Nov 18:33-18:46)

**Correction to exp88.** The 22 captures' pool hint files hold 6,939-26,863 hints (median
14,741), not 7,500-10,000 (that was 6 of them).

**Setup.** exp/nearhints88.py: each capture with its hints file replaced by the proof steps (loops/UL/hints) of the 10
solved siblings nearest by goal number, nearest first, deduplicated; only siblings whose hint file is older than the
capture's (solved before it). 320-2,675 hints (median 976). Same 160,000 pairs, lemmas, rule model
and PG. loops/P85C/exp88b/near10.tsv.

**Result.** Within 160,000 pairs: **pool 11, none 10, 10 nearest 12**; pool and none together 14, all three
16. The 10 nearest against the pool: +3 -2; against none: +4 -2; proved by the 10
nearest alone: com_Ralt__goal_411, lra2aa__goal_426. Median pairs per CPU s past 100,000 pairs: 1228 (pool 887, none 1,078).

**Reading.** A small, near hint set is at least as good as the full pool here, and cheaper per pair; the three hint
choices are complementary (16 of 22 together against 11 for the pool). 22 goals: the single-arm differences (12, 11, 10)
are noise; the complementarity is not.

**Change (18:46).** climb.py `--final-hints-ab`: the finals in three arms by (crc32 >> 3) % 3 of the target's name: 0 the
pool hints, 1 the sketch hints only, 2 the sketch hints and the 10 nearest solved siblings' proof steps (near_hints, the
same selection as nearhints88.py, from the loop's current solved set). CLS71 restarted as abs/cls71h.sh
(exp/prod/side/cls71h.sh) in place of cls71g.sh (18:30:29-18:46:16, --final-nopool-ab: 9 finals, no proof): climb.py
16524 (bash 16521) from 18:46:16, log line 3076, climb.tsv row 33404 on. Checked on the running finals: near10 finals
carry 569-3,701 hints, pool finals 4,056-8,939. Reading: exp/hintarms88.py (finals, proofs, final CPU h per arm, split by
--final-only-ab).

## exp89: unsolved siblings as extra goals of a long run (25 Nov from 18:56)

**Question.** The user: Prover9 can search with several goals and does not stop at the first, it only reports each
proved one; would that work in twee and spare us repeating the long runs?

**What exists.** twee has had `--multi-goal` since 13 Nov (e21): several negated conjectures, `SOLVEDGOAL <name>
considered=N` for each as it is proved, on until all are proved or the limit. REPORT 2p (13 Nov): as a replacement for
separate runs (a window of 5 goals, 5 times the budget) it lost, 21 against 28 and 4 against 5, because a separate run
of goal k+1 has goal k as an axiom while in the joint search goal k is only joinable. A multi-goal run's RESULT is
Theorem as soon as any goal is proved, so a loop must credit goals by their SOLVEDGOAL lines; the printed proof has
every proved goal's proof, USEDAXIOMS their union.

**Setup.** The other use: a long run kept as it is, plus its unsolved siblings as extra goals, nearly free (goal
normalisation). exp/multigoal89.py: an exp85 capture (loops/P85C/cap: problem with its lemmas, hints, rule model; 24
goals of the 99 captures with an unsolved sibling within 10, seed 89, exp/sets/exp89.goals) plus the negated,
Skolemised conjectures of up to 8 siblings unsolved now, nearest by goal number within 10, `--multi-goal`, 160 abstract
s (320,000 pairs). 10 of the 24 problems were rejected as non-Horn: a conditional sibling goal became a disjunction
(my parsing); rerun with plain-equation siblings only (one had none left). Data loops/P85C/exp89 (rows.tsv,
rows2.tsv).

**Result.** 23 runs, 117 extra goals, **2 proved**: nslm_to_aa1__goal_1047@135169, lra2aa__goal_427@96080. 18 targets were proved in their runs
(15 within 160,000 pairs, most within 60,000), and their runs went on to 320,000 pairs with the extras.
2.6 CPU h.

**The two proofs in production.** exp/mgcredit89.py reruns the problem with the proof and hints printed to just past
the extra's SOLVEDGOAL (the same pair count both times) and writes a loop record, loops/MG89 (solved.tsv, hints/,
out/, proofs/). Merged with merge.py loops/UL loops/MG89 (records written 19:33:38 and 19:56:02, the hints files' times).
Their lemmas: 95 and 14 sibling and kNN lemmas, all trusted goals in t1934, plus the captures' climber fill lemmas
(true_N); neither original is exposed. trust.py t1956: 49,825 solved, 0 untrusted.

**Reading.** As a free add-on of a long run, extra goals give 2 proofs of 117 extras: small but
positive at almost no cost. The better form, a goal proved mid-run added as an axiom of the same run, is what 13 Nov
lacked; the siblings of these targets already get the target as a lemma in their separate runs, so it would repeat
those runs' advantage, not add a new one. Next: listen mode in the ladder's finals (the nearest unsolved plain-equation
siblings as extra goals, credited by SOLVEDGOAL and a proof rerun), as a measured member.

## Listen mode in the ladder (exp89, deployed 25 Nov 20:34)

* **twee-e61l** (branch e61-listen, 82f5b92; /project/bin/twee-e61l, wrapper twee-pg61l): e61 plus listened goals. A
  negated conjecture named `listen_*` prints `SOLVEDGOAL` when proved (also without --multi-goal) and is never a
  solution: it does not stop the run or set RESULT, the proof or the hints. Without listen_ goals the output is
  byte-identical to e61 on 6 captured problems (proofs printed). On lra2aa__goal_426's exp89 problem: the listened 427 at
  96,080 pairs, the run on, GaveUp; renamed to a real goal, the run stops at 96,080 with its proof.
* **loop.py**: `listen_goals[name]` (clauses appended to the run's problem, tmp/<tag>.l.p) and `listen_credit`: each
  listened goal the run proved is rerun as a real goal (the clause renamed lgoal_<goal>, the same flags with the proof
  printed: the same search, which stops at that goal's proof); `listened[name]` gets (goal, output).
* **climb.py `--listen K`** (`--listen-dist`, 10): each final carries up to K of its original's unsolved goals nearest by
  goal number whose conjecture is one plain equation; `listen_record` writes a credited goal's hints (DIR/hints, linked to
  the live dir's), DIR/proofs/<goal>.listen, a used.tsv row (tag listen:<target>, its USEDAXIOMS lemma_/true_ names;
  none with an assume_ name), solved.tsv (round 1) and climb.tsv (tag listen) rows; the live loop then writes the live
  dir's solved.tsv row. climb.py refuses --listen with another twee (a listened goal's proof would count as the
  target's).
* **Test** (loops/LST89: production's solved goals without nil3_26 goals 5-10, hints copied; target goal 10, 20 s final,
  --listen 8): the final proved goal 10 at 1.52 s and, before that, goals 5 and 6 as listened goals; each rerun printed its
  proof (lgoal_ named in it); hints, proofs, used.tsv, solved.tsv and climb.tsv rows as above; production's hints files
  untouched.
* **Deployed:** CLS71 as abs/cls71i.sh (exp/prod/side/cls71i.sh): cls71h.sh plus --listen 8 and twee-pg61l; climb.py
  43358 (bash 43355) from 20:34:08, log line 3181, climb.tsv row 34179 on. Its first finals carried 1-6 listened goals.
  The three-arm hints A/B goes on (listen applies to every arm). CLQ83 as abs/clq87d.sh when its two oldest 640 s finals
  (over 5,000 s in) end.

### The listen bug (20:34-20:49) and its fix

* **What went wrong:** the first deployed CLS71 (climb.py 43358) listened to goals production had already solved and
  recorded 6 of them (nil3_30 goals 549-552 and 575, nil3_31 goal 502; climb.tsv rows 34179-34349, tag listen). A live
  climber's lp.solved lacks the live dir's proofs from its own (re)start until its first refresh, and listen_record
  wrote DIR/hints/<goal>, which is production's file (DIR/hints links to loops/UL/hints): 6 of production's hints files
  were replaced by the listened proofs' hints (1 to 71 lines instead of 5 to 230). No solved.tsv row was added in
  loops/UL (the live loop's check against its own solved set held).
* **Repair:** the 6 files restored from loops/LST89/hints, copied from loops/UL/hints at 20:32:40, before the first
  overwrite at 20:39:11 (their kept outputs in loops/UL/r5/out are from 23-25 Nov, so production had not rewritten them
  since). The overwritten versions are kept in the session scratch. The 6 used.tsv rows (listen:<target>) stay: each is
  a real proof whose premises are listed, so trust.py takes it as one more record of a goal that already has records.
* **Fix** (climb.py, 20:49): live_solved() reads the live dir's solved.tsv afresh (at most once a minute, and afresh
  before each record); listen_lines leaves those goals out; listen_record also refuses any goal that has a hints file.
  CLS71 restarted at 20:49:35 (climb.py 46097, log line 3212, climb.tsv row 34350 on), CLQ83 as clq87d.sh at 20:51:31
  (climb.py 46658, log line 2158, climb.tsv row 2678 on; its two oldest finals had ended at their CPU cap). In the 9
  finals started since, all 22 listened goals were unsolved in production.
* **For counting:** listened proofs are climb.tsv rows tagged listen from row 34350 (CLS71) and row 2678 (CLQ83); the
  6 earlier rows are not new proofs.
* **First listened proof since the fix:** nslm_to_aa1__goal_1256, listened in the 160 s final of nslm_to_aa1__goal_1250
  (CLS71); its proof rerun took 364 s; hints file loops/UL/hints/nslm_to_aa1__goal_1256 (243 lines) at 21:17:32, one
  loops/UL solved.tsv row, a used.tsv row naming its lemma_ and true_ premises. trust.py (loops/TRUSTNOW/t2118): trusted;
  49,828 solved, 0 untrusted.

## exp90: listened goals changed the search (25 Nov 21:10-21:42)

* **Question:** what do a final's listened goals cost? exp/listencost90.sh: CLS71's 160 s final of
  nsmr_to_aa1__goal_893 (8 listened goals; its problem, hints and rule-goal file copied while it ran), run with and
  without the listen_ lines, the same flags.
* **twee-e61l, 320,000 pairs:** with them 69,936 rules, 342 CPU s; without 49,581 rules, 552 CPU s. Not a cost but a
  different search: the target's own final was not the final it would have had.
* **Cause, by elimination** (40,000-pair runs; a bare run without model, hints or parental filter: 13,372 rules
  against 7,676): not the rule model, the hints or the filter. Two fixes left it unchanged: leaving listened goals out of
  the occurrence count behind the precedence, and numbering their own symbols last. The cause is twee's goal
  flattening (`--flatten-goal`, on by default): every negated goal's ground subterms become new definition axioms, the
  listened goals' too.
* **twee-e61m** (e61-listen 0031f9a): listened goals (listen_*) and the credit rerun's goal (lgoal_*, so that the rerun
  is the same search) are not flattened, are left out of the precedence count, and their symbols are numbered last.
  Tests: production flags with and without the 8 listened goals: the same 16,724 lines of given rules; e61m without
  listened goals byte-identical to e61 on 5 problems (proofs printed, with and without hints); nil3_26__goal_10 with
  goals 5 and 6 listened: both reported (pairs 1 and 37), each credit rerun stops at the same pair and prints its
  lgoal_ proof.
* **Deployed:** /project/bin/twee-pg61l execs twee-e61m from 21:41:49 (no climber restart; finals already running
  finish on e61l, and their credit reruns, on e61m, may not replay: then no record). CLS71 and CLQ83 finals started
  20:34-21:41 had a changed search; the three-arm hints A/B rows of that time are mixed.
* **Next:** the cost with e61m (exp/listencost90m.sh), the same final with and without its listened goals.
* **Shared code (25 Nov 22:00):** hintsel.listen_clauses (the choice of listened goals: nearest plain unsolved
  siblings, Skolemised) and loop.output_hints (a proof output's hints rows, run_one's code) are used by climb.py; the
  credit rerun drops `--dump-state` (it must never replace a goal's saved state) and a resumed run (`--load-state`) is
  never credited. Test loops/LST90 (as LST89, twee-pg61l = e61m): goal 10's 20 s final credited goals 5, 7, 8 and 9
  (LST89 with e61l: 5 and 6; e61l flattened the listened goals, which helps some of them, and changed the search);
  goal 5's hints file byte-identical to LST89's.
* **The cost with twee-e61m** (the same final, 320,000 pairs, exp/listencost90m.sh and exp/listencost90all.sh; time's
  user+sys): without listened goals `without cpu 559.12+24.95 wall 581.80 maxrss 1363712`; with its 8 `with cpu 586.56+4.37 wall 589.17 maxrss 1163008`; with all 120 unsolved plain goals of
  nsmr_to_aa1 `all cpu 608.14+2.89 wall 609.08 maxrss 1249920`. The same search in all three (49,581 rules); none of the listened goals proved in this final.
  So 8 cost about 1% and 120 about 5%.
* **Deployed:** CLS71 as abs/cls71j.sh (cls71i.sh plus `--listen 300 --listen-dist 100000`: all the original's unsolved
  plain goals) from 22:03:48, climb.py 60285, log line 3301, climb.tsv row 35134 on; CLQ83 as abs/clq87e.sh when its two
  oldest 640 s finals end.

## Production listening: loop.py --listen (25 Nov, tested, not deployed yet)

* **loop.py `--listen K`** (`--listen-dist`, default 100000; --cascade only; refuses a twee other than e61m/pg61l): each
  twee run carries up to K of its original's unsolved goals of the loop (hintsel.listen_clauses), except Prover9 and
  unfold variants and resumed runs (a loaded state cannot be replayed by the credit rerun). A credited goal (the rerun
  printed its lgoal_ proof) is recorded in the cascade like the loop's own proof: kept output DIR/rN/out/<goal> (its
  USEDAXIOMS: trust.py's record; skipped if it names assume_ or a bare lemma_knn_N), the proof (proof_write), the hints
  file, solved.tsv, a results.tsv row (level `listen`, stats `LISTEN in <run's goal>`; the restart parse skips unknown
  levels) and add_proof (pools, lemmas). The rerun is skipped for a goal solved meanwhile.
* **Test** loops/LSTP90: nil3_26's 506 goals, 475 solved (production's, goals 5-10 left out), cascade 5,40, production's
  main options (no --given-scan, --sync, variants), -j 2, --listen 300, 7 minutes: goal 5's run credited 10 and 7, goal
  6's run 8 and 9, each with a solved row, hints, kept output with USEDAXIOMS, proof and a `listen` results row; goal
  420's run, started earlier, listened to goals solved meanwhile (hence the skip).
* **CLQ83** as abs/clq87e.sh (`--listen 300 --listen-dist 100000`) from 22:26:50, climb.py 66157, log line 2180,
  climb.tsv row 3004 on (4 finals, 206 to 1,576 s in, were cut).

### The listen premise check (25 Nov 22:38)

* **The hole:** a conditional target's hypotheses are axioms of its run (named after its conjecture, `goals`; e.g.
  production's proof of im2_24_to_25__goal_520 uses `goals`). They are ground facts about the target's Skolem
  constants and can make new equations provable, so a listened goal's proof must not use them. climb.py's
  listen_record kept only the lemma_/true_ names of USEDAXIOMS, and trust.py resolves `goals` as the problem's own
  conjecture, so such a proof would have been trusted.
* **Checked:** all 12 listened proofs so far (CLS71 and CLQ83 proofs/*.listen, 20:39-22:26) use only lemma_, true_ and
  `sos` premises: none affected. Production had credited none.
* **Fix** (loop.py listen_bad_premises, in listen_credit, so climb.py and loop.py both): a credit needs every premise to
  be an axiom of the listened goal's own problem, a lemma_/true_ lemma (not a bare lemma_knn_N) or a srclem_/skax_
  lemma of a named goal. Tested on the 12 proofs (all pass) and on crafted premise lists (`goals`, lemma_knn_3,
  assume_goal_7, none: refused).
* **Restarts** (22:38:56 stop, 22:39:15 start): production as abs/ul87.sh (ul86's settings; ul86's log would be
  truncated), loop.py 71405; CLS71 (cls71j.sh) climb.py 71408, log line 3349, climb.tsv row 35490 on; CLQ83 (clq87e.sh)
  climb.py 71407, log line 2184, climb.tsv row 3071 on.

### Production's first listened credits (25 Nov 23:30) and the kept-output race

* ul87's run of nil3_29__goal_474 (a conditional goal; its own proof uses its hypotheses `goals`) credited goals 445
  and 475 as listened goals (neither proof uses `goals`): solved rows, hints, proofs, results rows `listen`. trust.py
  (loops/TRUSTNOW/t2331): 49,861 solved, 0 untrusted, both trusted.
* **Race:** a run of goal 475 itself, started before the credit, failed after it and wrote its kept output over the
  credited one (loops/UL/r5/out/<goal> is per goal name). nil3_29 is not an exposed original, so trust.py did not need
  the record; in an exposed original this would make a false "no record", never a false trust.
* **Fix** (loop.py, from the next production restart): listened kept outputs go to DIR/listen/rN/out/<goal>, which no
  run writes; trust.py scans it as dir DIR/listen, whose hints link to ../hints (its byte comparison then matches).
  Test loops/LSTP91 (as LSTP90): 4 credits, each in listen/r1/out with RESULT Theorem and USEDAXIOMS, hints the same
  bytes through the link.

## The ladder at 23:33: CLS71 reaches goals it already finaled

* The waiter fired: CLS71 started a final on nslm_to_aa1__goal_846, which had a CLS71 final before. Of cls71all.re's
  1,891 unsolved goals, 76 have no CLS71 final, 1,323 one and 492 two.
* **The 640 s rung never reached its list:** a live climber takes production's newly stalled goals before its
  --reclimb list, and CLQ83's 58 finals since row 2093 all went to such goals (11 proofs); none of ladder640.re's 536
  unsolved goals has had a 640 s final. The two rungs did not overlap (none of the 58 had a 160 s final since the
  ladder start).
* **Real proofs since 15:08** (each climber's round-1 solved rows whose production hints file is dated after 15:08,
  less CLS71's 6 recorded by the 20:34 listen bug): CLS71 27 in 63.5 CPU h (0.43 per CPU h; 10 of them listened
  goals), CLQ83 12 in 36.2 CPU h (0.33).
* **Second finals still pay** (CLS71's whole history, 20 s and 160 s finals mixed): first finals 247 of 2,637 proved
  (9.4%, 1.21 per CPU h), second finals 61 of 599 (10.2%, 0.82 per CPU h).
* **Decision:** no change. CLS71 goes on with second 160 s finals (a changed context each time, and every final
  listens to its original's unsolved goals); CLQ83 goes on with the new stalled goals, then its list. The ladder's
  next step (a goal's failures move it to a longer rung) needs a climber that ranks its list above new targets.

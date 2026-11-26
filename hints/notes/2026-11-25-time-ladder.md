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

## The first hours of listening everywhere (25 Nov 23:52 UTC)

* **167 goals** recorded in loops/UL/solved.tsv after its line 50,653 (its length when loops/LST90 copied it at 21:54),
  by the first source that recorded each (production results rows, the climbers' round-1 rows, then the side
  loops' solved.tsv). (26 Nov correction: a cut by line number is not a stable count, since the file has one line per
  recorded proof and its earlier lines changed later; the totals over time are in "Solved over time, by trust run"
  below. By those, loops/UL had 49,828 at 21:18 and 49,982 at 23:51, and 121 of the 154 came after 23:32.)
  * side loops GML/XFL (given-rule retry, transfer): 53
  * production, own runs: 48
  * production, listened: 40
  * CLS71, listened: 10
  * CLS71, own climbs: 9
  * CLQ83, own climbs: 6
  * CLQ83, listened: 1
* **By original** (top): nil3_30 18, nil3_26 16, nil3_27 16, aK2_eq_aK3_l 14, nil3_29 13, nil3_31 10, nil3_25 10, nil3_24 10.
* Listened credits open goals for the follow-ups: production's L0/L1 runs on the goals after each new proof and
  the side loops prove more around them. Before listening everywhere: 49,825 solved at 19:56 and 49,828 at 21:18
  (the trust runs t1956, t2118), 3 in 82 minutes.
* **trust.py** (23:55): CLQ83's listened nil3_23_32_to_27__goal_581 (an exposed original) was the one untrusted goal
  (t2348): its proof used ten fill lemmas true_k that CLQ83's true.tsv has as copies of CLS71's rows (the dir began
  with a copy), with their premise records only in CLS71's fillprem.tsv. A fill lemma without a premise record now
  rests on its formula node (trusted when another fill lemma of the same original and formula is; the fixpoint adds
  a node only once its deps are trusted, so a copy cannot vouch for itself). t2351: 49,982 solved, 0 untrusted; fill
  lemmas trusted 23,620 (3,406 before: the copies).

## Listening across originals (exp91, 26 Nov 00:53)

* **Question:** a run of original A's goal listens to A's unsolved goals. 854 of the 1,671 unsolved goals (loops/UL at
  00:20) have unsolved siblings in other originals with the same axiom lines (68 classes over 129 originals; e.g. the 6
  nil3_23_32_to_* originals share one with 165 unsolved goals, 12 originals of Ka1_eq_Ka2, aK2rev, a_instances, ...
  one with 153). Listening to those too is nearly free with twee-e61m (the search is unchanged), so does it prove more?
* **loop.py `--listen-class K`** (hintsel.listen_clauses gets `start`, so the Skolem names do not collide): after the
  own original's goals, up to K unsolved plain goals of the other originals of the same class (md5 of the sorted
  axiom lines of the original's first problem), nearest by goal number. **Credit rules across originals**
  (listen_bad_premises with the run's name): the problem's axioms, lemma_goal_N, and names that say whose goal they are
  (lemma_knn_K_<goal>, srclem_N_<goal>, skax_N_<goal>); refused: true_k, lemma_fill_N (numbered per original), assume_,
  a bare lemma_knn_N, the target's hypotheses. listen_credit rewrites lemma_goal_N to lemma_knn_0_<A>__goal_N in the
  output (kept output, proof), which trust.py resolves to A's goal N.
* **Tests:** loops/LSTX92 (nil3_23_32_to_25 and _26, goals 5-10 dropped) listened 23 of the other original's goals in
  a run, but those dropped goals are conditional (not listened). loops/LSTX93: dropped nil3_23_32_to_25__goal_44 (the
  same equation as nil3_23_32_to_26__goal_42) and nil3_23_32_to_26__goal_43, -j 1: goal 43's run proved 44 as a
  listened goal, recorded with kept output listen/r1/out (RESULT Theorem, USEDAXIOMS lemma_knn_19_nil3_23_32_to_26__goal_61
  sos), proof, hints and solved row. The translation and the premise lists checked by hand on a made-up USEDAXIOMS
  line (cross refuses true_3, lemma_fill_2, goals, lemma_knn_5).
* **Production ul88** (abs/ul88.sh, exp/prod/ul88.sh; `--listen-class 150`, also the listened-output folder) from
  26 Nov 00:49:32 (ps lstart), loop.py PID 91876; ul87's last results row 366930 (t= resets after it). First runs: nil3_23_32_to_31__goal_549 listened to 135 goals,
  115 from other originals; nil3_24__goal_477 to 50, 46 from others.
* **Reading** (to do): credits whose goal's original differs from the run's (log lines "listen: X proved in a run of
  Y"), per CPU h; L0's CPU per run before and after row 366930 (the listen cost).

## Listening in the plain live loop (exp92, 26 Nov 00:58)

* **Why:** plainlive's cycles run a few hundred to 1,100 plain twee runs (N: 5 s; H, W: 60 s with 100+30 siblings and
  400 kNN lemmas) on the unsolved goals, none listening. Production's listening credited 49 goals in ul87's 2 h 10 min.
* **condprove.py `--listen K`** (twee-e61m; without listened goals its search is twee-e61's, so `--prev`'s SAME check
  and condimport.py's reruns with twee-pg61 still hold): each run also listens to up to K unsolved plain goals of its
  original (hintsel.listen_clauses). A listened goal X proved there gets a run of the run's problem with the
  conjecture line replaced by X's (the same axioms and lemmas, all trusted under --proved; no hypothesis of the run's
  goal, as conditional goals keep theirs inside the conjecture formula); its THM or NO row is written like any other,
  p/<X>.p is that problem, and X's own run in the same sweep is skipped. OUT/listened.tsv: X, the run's goal, result.
  The listened lines live in a temporary p/<goal>.l.p, so p/<goal>.p and the --prev comparison stay as before.
* **Test** (scratchpad cp92; trusted = loops/UL solved without nil3_26 goals 5-10; runs of goals 5 and 6, -j 1, N's
  settings): without --listen 2 rows (both THM); with it the same 2 rows (0.10 and 0.12 s against 0.09 and 0.11) plus
  10 and 7 (in 5's run) and 8 and 9 (in 6's), each THM; condimport.py imported 6 of 6 (USEDAXIOMS: trusted kNN lemmas
  and sos).
* **Deployed** as abs/plainlive7.sh (exp/prod/side/plainlive7.sh; `--listen 300` in N, H and W): plainlive6 was stopped
  after its cycle c53 (cond/PLNL.stop), plainlive7 starts with --prev c53N, c53H, c53W.
* Also: loop.py's axiom_class now calls lemmas.axiom_key (the same partition, one implementation; production's
  running ul88 keeps its loaded copy, which computes the same keys).
* **First cross credit** (ul88, about 10 minutes in): a run of nil3_23_32_to_30__goal_593 proved
  nil3_23_32_to_27__goal_576 (an exposed original); kept output loops/UL/listen/r5/out/<goal> (USEDAXIOMS: kNN lemmas
  naming their goals and sos, no lemma_goal_N), hints, proof, solved row. trust.py t0059: 50,122 solved, 0 untrusted,
  this one trusted.
* **The listen cost in wall time** (results.tsv, failed runs by level, restarts from t= resets; noisy on the shared
  machine): L0 median 9.91 s in ul85 (no listening), 9.27 s in ul87; L1 69.7 s and 75.6 s. No clear cost; exp90's
  +4.6% CPU (120 goals, same search) stays the figure.
* plainlive6's last cycle c53W ended at 01:17:11 (167 runs, 68 THM, 25 imported into loops/CI2, 9 merged into
  loops/UL); plainlive7 (PID 96229) started at 01:17:27 with --prev c53N, c53H, c53W. Its first sweep c54N: 1,625
  unsolved goals (most SAME), twee-e61m with listen lines.
* **plainlive7's first sweep c54N** (650 runs, 01:17-01:35): 40 THM, 4 of them listened goals (aK2_eq_aK3_o 460 in
  410's run, nslm_to_aa1 973 in 1007's, ns_to_aK1 603 in 587's and 636 in 608's), each proved again in its own run and
  imported by condimport.py (40 of 40); 20 merged into loops/UL.
  Of the 4 listened goals, 1 was merged as new (ns_to_aK1 603); the other 3 reached loops/UL during the sweep from
  other producers (hints files dated 01:17:30, 01:22:54, 01:32:49), so the merge skipped them.
* **CLS71 with --listen-class 150** (abs/cls71k.sh, exp/prod/side/cls71k.sh): restarted as climb.py 105364 at 02:19:19
  (ps lstart; log line 3625, climb.tsv row 36903 on), same environment (RECLIMB=sets/cls71all.re,
  EXCLUDE=sets/cls71f.excl). Why: ul88's first 1.5 h made 28 listened credits, 15 across originals. First finals:
  Ka_eq_aK3__goal_457 listened to 134 goals, 114 from other originals; R1dist_to_aa1 (a class of its own) to 113, none.
  CLQ83 keeps clq87e.sh for now (its 640 s finals were 44-56 minutes in).
* **03:48:** CLQ83 stays on clq87e.sh (no --listen-class): its 640 s finals run 1-2.5 hours, so any restart cuts about
  2 CPU h of finals in flight (5 at 23-32 minutes now), and in about 5 hours it credited 1 listened goal. It takes the
  option at its next restart made for another reason. CLS71 since 02:19: 3 listened credits, all from its own
  original. plainlive7: c54W 5 listened rows (all THM), c54H and c55N none.
* **The ladder's next step, re-read (26 Nov 04:50):** CLQ83's 104 finals since row 2093 all went to newly stalled goals
  (production's, taken before its --reclimb list): 34 proved in 52.0 CPU h, **0.65 per CPU h**, above CLS71's 0.43
  (15:08-23:33). Its list (ladder640.re: goals with two failed 160 s finals) never ran. A climber that ranks the list
  first would trade a measured 0.65 for an unmeasured rate on goals that already failed twice, so the ladder stays as
  it is; the list runs when the new stalled goals run out.
* **Since 01:48** (69 production hints files dated after 01:48, by first producer; a re-proof rewrites the file, so
  this is rough): production's own runs 21, plainlive7 14, CLQ83 11, CLS71 12 (7 listened), GML/XFL 5, production
  listened 4, CLQ83 listened 2. loops/UL: 50,228 at 01:48, 50,295 at 04:48.
* **08:18-08:48, a burst:** ul88's listened credits 43 to 62 and loops/UL 50,385 to 50,449. Of the 19 credits, 10
  came from runs of other originals: aK2_eq_aK3_1243 5 (in runs of nil3_15to7), nil3_1K_b 2 (aK2_eq_aK3_gen),
  nil3_1K_c 2, aK2_eq_aK3_gen 1 (nil3_1K_b); the other 9 were aK2_eq_aK3_gen's own. trust.py t0848: 50,449 solved, 0
  untrusted.

## Solved over time, by trust run (26 Nov 11:15)

Each exp/trust.py run counts loops/UL's solved goals the same way (trusted + untrusted, files loops/TRUSTNOW/tHHMM.*);
the health checks' `cut -f1 loops/UL/solved.tsv | sort -u | wc -l` agrees within a few goals at the same minute.

| trust run | solved | change | what ran |
|---|---|---|---|
| 25 Nov 19:56 (t1956) | 49,825 | | before listening in production |
| 21:18 (t2118) | 49,828 | +3 in 82 min | |
| 23:32 (t2331) | 49,861 | +33 | production listening from 22:18 (ul86, ul87) |
| 23:48 (t2348) | 49,972 | +111 in 16 min | listened credits and their follow-ups |
| 23:51 (t2351) | 49,982 | +10 | |
| 26 Nov 00:59 (t0059) | 50,122 | +140 in 68 min | listening across originals from 00:49 (ul88) |
| 01:48 (t0148) | 50,228 | +106 in 49 min | plainlive7 listening from 01:17 |
| 06:48 (t0648) | 50,349 | +121 in 5 h | about 12 per half hour |
| 08:48 (t0848) | 50,449 | +100 in 2 h | the 08:18-08:48 burst (64 in those 30 minutes) |
| 10:56 (t1056) | 50,485 | +36 in 2 h 8 min | about 4 per half hour |

So the fast phase ran from about 23:30 to about 01:50 (49,861 to 50,228, +367 in 2 h 16 min), in two waves (production
listening, then listening across originals), not "the first two hours from 21:54" as first written here; 657 in all
from 21:18 to 10:56.

## Listening to conditional goals (exp93, 26 Nov 11:12)

* **The user (26 Nov):** listen to the conditional goals too. Of 1,294 unsolved goals at 11:00, 1,143 are plain
  equations (listened already) and 151 have one hypothesis and one conclusion (l1 = r1 -> l = r); 135 of these have a
  hypothesis with a variable side (t = X, X not in t), the other 16 terms on both sides.
* **hintsel.listen_equation** (c32871d): such a goal is listened as C[X := t], which is equivalent (the one-point rule:
  for all X, t = X -> C holds iff C[X := t] does). The other 16 stay out: their conclusion alone is a stronger,
  usually false statement, and their hypotheses as axioms would change the search.
* **Test** (scratchpad condeq; 40 of the 6,100 solved such goals, seed 11, twee-e61 at 5 abstract s): the original
  problem proved 29, the equation 30, both 29, the original only 0.
* **Deployed:** production ul89 (abs/ul89.sh, exp/prod/ul89.sh; PID 175279) and CLS71 (cls71k.sh again; climb.py
  175280), both from 11:12:00; CLQ83 as abs/clq87f.sh (also --listen-class 150) once its 1 h 49 min final ends;
  plainlive7's condprove loads hintsel at each sweep (a listened conditional goal's own run there uses its own
  conjecture line). First runs: the 20 newest problem files of production and CLS71 listened to 820 goals, 81 of them conditional.
* A credited conditional goal's kept output and proof are of the equation (named lgoal_<goal>), not of the
  hypothesis form; the two are equivalent, and trust.py checks the premises.
* CLQ83 restarted as abs/clq87f.sh (climb.py 181853, 12:03:00; log line 2350, climb.tsv row 4626 on; CPUS=23) when its
  longest final, nslm_to_aa1__goal_1382, ended (NO, 48,196 s total for that target).
* **First conditional credit** (CLS71, by 12:18): nslm_to_aa1__goal_1133 (conditional) listened as its equation in
  the final of nslm_to_aa1__goal_1405, rerun printed its proof in 67 s; used.tsv record (lemma_goal_1366, 1379, 1392
  and kNN lemmas). trust.py t1218: 50,499 solved, 0 untrusted, this one trusted. ul89 had no listened credit in its
  first 66 minutes.

## Conditional goals as equations, an A/B (exp94, launched 26 Nov 13:00:35)

* **Question:** is an unsolved conditional goal (t = X -> C, X a variable not in t) easier for twee as its equivalent
  equation C[X := t] than as its original problem? This morning's 40-goal check on solved goals at 5 s gave 29
  against 30, with one proved only as the equation.
* **Set:** exp/sets/exp94.goals, every goal of sets/all not in exp/sets/exp94.trusted (loops/UL's solved goals when
  launched, 50,499) whose conjecture is one hypothesis with a variable side and one conclusion: 134 goals of 32
  originals (1,285 unsolved in all). No sampling, no seed.
* **Arms:** O runs each goal's conditional problem as condprove.py builds it; E is the same problem with the
  conjecture line replaced by the equation (condprove.py --equation, new; hintsel.listen_equation). The same trusted
  set, siblings and kNN lemmas in both. Two stages: plainlive's N setting (5 s, 30 siblings, 10 after, 100 kNN), then
  its H setting (60 s, 100 siblings, 30 after, 400 kNN); no listening, no hints. twee-pg61 at --abstract-time 2000,
  -j 4 (4 CPUs).
* **Command** (from /project/hintwork): `J=4 bash /project/twee/hints/exp/exp94.sh cond/EXP94`; arms in order NO, NE,
  HO, HE; cond/EXP94/log has their start and end times.
* **Reading:** proved per arm and stage, +/- and the union, abstract seconds per proof. A THM here is a conditional
  proof (it may use unproved siblings); condprove's results.tsv says which.
* **exp94 5 s stage** (NO 13:00:35-13:04:01, NE 13:04:01-13:06:53): original 0 of 134, equation 1 of 134,
  nslm_to_aa1__goal_1121 (1.47 s, no unproved sibling used, 2 kNN lemmas; its original NO at 5.10 s). Imported via
  condimport.py into loops/CI2 and merged into loops/UL (cond/EXP94/NE.import, NE.merge); trust.py t1318: 50,500
  solved, 0 untrusted, this one trusted. The 60 s stage (HO, HE) runs.
* **exp94 result** (HO 13:06:53-14:06:20, HE 14:06:20-15:00:06; counted from the four results.tsv):

  | stage | original | equation | equation only | original only | run seconds O / E |
  |---|---|---|---|---|---|
  | 5 s (N) | 0 | 1 | 1 | 0 | 786 / 645 |
  | 60 s (H) | 0 | 2 | 2 | 0 | 14,114 / 12,612 |

  The 60 s equation-only goals: nslm_to_aa1__goal_1121 (again, 2.87 s) and ns_to_aa1_c__goal_314 (120.37 s wall, no
  unproved sibling, 16 proved siblings and 74 kNN lemmas; its original NO at 113.89 s). Imported (condimport.py 1 of
  2, the other already solved) and merged; trust.py t1504: 50,512 solved, 0 untrusted, both trusted. Small numbers (2
  of 134), but one-sided: the equation never lost, and its runs took 11-18% less wall time.
* **Deployed:** plainlive8 (abs/plainlive8.sh, exp/prod/side/plainlive8.sh; PID 206709 from 15:06:23, first cycle
  c64 with --prev c63N/H/W): plainlive7 plus condprove.py --equation in N, H and W. A conditional goal's problem text
  changes, so each of them reruns once in N (and in H or W when it is a head). Production's and the climbers' own runs
  of conditional goals still use the conditional form; they listen to them as equations since 11:12.
* **The same in production and the climbers** (15:10:15): lemmas.equation_problem (6234ec7) replaces a conditional
  goal's conjecture line by lemma_form's equation; lemma_problem applies it under TWEE_LEMMA_EQN=1, which covers
  loop.py's and climb.py's runs (both build their problems there; a run without lemmas still reads the original
  file). hintsel.listen_equation had duplicated lemmas.unitize (15 Nov, used for solved conditional siblings as lemmas);
  it now calls lemma_form (the same on all 51,784 goals up to variable names: 40 renamings), and condprove --equation
  calls equation_problem (the same conjectures as exp94's HE on all 134). Production ul90 (abs/ul90.sh,
  exp/prod/ul90.sh; loop.py 207594, results row 377,827 on) and CLS71 as abs/cls71l.sh (climb.py 207596, log line
  4474 on), both from 15:10:15; CLQ83 as abs/clq87g.sh when its longest final (nslm_to_aa1__goal_1254) ends.
* CLQ83 restarted as abs/clq87g.sh (climb.py 215308, 16:08:10; log line 2378, climb.tsv row 4898 on; CPUS=23) when
  nslm_to_aa1__goal_1254's final ended (NO, 14,675 s for that target). Every loop now runs and listens to conditional
  goals with a variable-side hypothesis as their equation.

## The 160 s rung done; CLS71 moves to 640 s (26 Nov 19:20)

* **19:18:** CLS71 ran no twee: all 1,222 unsolved goals of its list (sets/cls71all.re outside sets/cls71f.excl) had two
  CLS71 finals (counted from climb.tsv's final rows), its --reclimb-max is 2, and production's new stalled goals come
  rarely now. CLQ83 (640 s) had 5 finals running, production 4 runs, plainlive8 3.
* **Change:** climb.py `--list-only` (a live climber skips the live loop's new stalled goals and climbs only its
  --reclimb list). CLS71 restarted as abs/cls71m.sh (exp/prod/side/cls71m.sh; climb.py 240359 from 19:20:42, log line
  4702 on): cls71l plus --list-only --reclimb-max 3, 640 s finals, -j 5, EXCLUDE also sets/ladder640.re (CLQ83's list),
  so each goal gets a third final, at 640 s, nearest proved goal below first (the first five: R1dist_to_aa1 goals
  460-475). The CPU gates stay (CLS71 --cpus 20, CLQ83 --cpus 23, counting all twee processes).
* **Why 640 s and not a third 160 s final:** on production's newly stalled goals the 640 s rung made 0.65 proofs per CPU
  h and the 160 s rung 0.43 (sections above), and second finals paid about as well as first ones (10.2% against 9.4%).
  The 160 s rung for newly stalled goals ends with this; CLQ83 takes them at 640 s.
* **Memory:** 640 s runs held 2.3-3.6 GB each at 19:18 (CLQ83), so 5 more add about 15 GB (about 40 GB in all); the
  50 GB alert stays armed.
* **Reading:** CLS71's finals from climb.tsv row 44,987 on: proved per CPU h against CLQ83's in the same hours.

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

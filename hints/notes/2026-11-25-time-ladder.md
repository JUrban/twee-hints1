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

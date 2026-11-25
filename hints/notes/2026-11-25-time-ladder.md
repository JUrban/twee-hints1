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

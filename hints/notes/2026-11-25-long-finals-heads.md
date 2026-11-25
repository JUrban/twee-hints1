# exp86: long finals on the local heads (25 Nov 13:34)

## Why

* Production has made no proof since about 10:00 (ul84: 0 in its last 2.2 hours at 12:18, about 680 runs an hour),
  and both climbers had no target: the stalled-goal rule needs a failed L1+ run, and production now runs mostly 5 s
  levels. 2,000 goals are unsolved (loops/UL/solved.tsv at 13:30), and every one has had a climber final.
* 1,424 had a final of CLS71 (160 abstract s, the median 425 CPU s). **576 had only CLQ83's quick final** (40 CPU s):
  all are local heads (sets/localheads71: unsolved, the previous goal proved), which CLS71 excludes only to split the
  work (notes/2026-11-23-tail-allocation.md). exp83b's 40 s finals proved 23 of 664 heads (3.01 per CPU h).
* exp85e (notes/2026-11-25-precedence-portfolio.md): on 22 goals that failed at 80,000 pairs, the same climber final
  continued to 320,000 pairs proved 16 (11.9 per CPU h; known-provable goals, so an upper bound). The long final is
  the staged final's second stage, never run on these heads.

## Setup

* abs/clq86.sh (exp/prod/side/clq86.sh): abs/clq83.sh with `--reclimb sets/exp86.heads` (exp/sets/exp86.heads, the 576
  heads), `--final-cpu 0` (so the final is CLS71's: `--max-time 160` abstract, `--max-cpu 1600`), -j 10, --cpus 20
  (a climb starts only while fewer than 20 twee processes run). Same loops/CLQ83 and log; --runs 0 (final only).
  `--reclimb` takes goals with fewer than 2 finals, after newly stalled ones, nearest proved goal below first.
* CLQ83 (4013658) stopped 13:34; clq86 bash 4146123, climb.py 4146126, from 13:34:20. Reading from CLQ83.log line 2043
  and climb.tsv row 2038 on (exp/clq83b_read.py with LOG_LINE and TSV_ROW set). The first 10 finals are heads.
* Cost: 576 finals at about 400 CPU s (CLS71's failed finals: median 409 s) is about 64 CPU h, 6-7 hours at -j 10.
* **Rule (pre-registered):** keep while at 1 proof per CPU h or more after 8 CPU h (exp83b's rule); else stop and
  restore abs/clq83.sh. The comparison: CLQ83's 40 s finals on the same heads (3.01, but on the easier ones first) and
  CLS71's re-climbs (final-only 0.86 per CPU h).

## Result (14:27; loops/CLQ83/climb.tsv from row 2038, figures from the rows)

* **3 proofs in 52 finals, 8.13 CPU h: 0.37 per CPU h**, below the rule's 1. Stopped 14:28 (the 10 running finals
  killed); abs/clq83.sh restored (EXCLUDE=sets/clq83b.excl, 40 s finals, -j 3, --cpus 23; climb.py 4153356 from
  14:28:10, log from line 2099).
* Proved: nslm_to_aa1__goal_1073 and 1067 (about 340 CPU s each), aK2_eq_aK3_a__goal_550; all three in loops/UL with
  hints. 49 failed; final CPU median 529 s, max 1,602 s (the 1,600 s cap).
* The queue put the heads nearest a proved goal first, so the rest of the 576 would likely do worse.
* **Reading.** On real unsolved heads that failed the 40 s final, continuing to 160 abstract s yields 0.37 per CPU h,
  against 11.9 on exp85e's known-provable goals: that figure was the selection, not the method. The 40 s stage already
  took most of what a longer run of the same setting can find; the unsolved tail needs other inputs (new hints,
  lemmas, or a different search), not more time with the same ones. Kept as a negative.

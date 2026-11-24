# exp83: a quick climber final ahead of the climber (24 Nov 15:35 UTC)

**Question.** The climber's 160 s finals (CLS71) prove about a quarter of its targets, but half their proofs come early
and a failed final is costly. Does a second live climber with no climbs and a **40 CPU s** final, on the same stalled
queue in the same order (nearest a proved goal first), prove goals at a much higher rate per CPU h, and so move the
chains sooner?

## Why (exp/quickfinal_stats.py, CLS71 since the 08:59 instance, log line 1047 on)

```
finished 506, proved 130; proved by the final 126
proving finals CPU s: q25 19, median 40, q75 134, q90 266; under 40 s: 63
failed finals 376, median CPU s 409
distance 20-40 lines: finished 61, proved 27 (44%)
distance 40-80 lines: finished 99, proved 34 (34%)
distance 80-160 lines: finished 87, proved 29 (33%)
distance 160-more lines: finished 259, proved 40 (15%)
production before: failed runs per proved goal median 57, max 106; CPU h 16.4; runs beyond the 5 s level 0
  labels [('L0', 1785), ('Vk60@0', 1030), ('Vunf@0', 890), ('Vk100@0', 843), ('Vk200@0', 653), ('Vk400@0', 558)]
all finals CPU h 47.4; the same finals capped at 40 s 5.2
```

* So a final capped at 40 CPU s would have kept about half of the proving finals at about a tenth of a failed final's
  cost. Over the same finals: 5.2 CPU h capped at 40 s, against the 47.4 CPU h they took (last line above).
* Production had run only 5 s runs on these goals (no run beyond level 0, a median of 57 per goal): the climber's
  final is the only long run they get. Production's own long fresh member, k400s30@3:0 (exp79, the same lemma lists
  at 160 s), ran 14 times in its last 20,000 runs (0 proofs) and the scheduler dropped it; skk400s30@1:0 (40 s) had
  51 runs and 0 proofs by exp79. In the climber the same run, on goals near a proved one, proves a quarter of them:
  the order makes the yield.
* The distance order already favours the near targets (44% proved at 20-40 proof lines, 15% beyond 160).
* Not exp49 (21 Nov, notes/2026-11-21-quick-first.md): its 1 s first pass sorted a failed goal after the whole tail,
  so goals needing 1-5 s waited an hour or more, and it lost 719 at 3 hours. Here the quick final is extra: a goal
  CLQ83 fails keeps its place in CLS71's queue and gets its full final there, unchanged.
* HLS2 (the kNN-slice plain sweep, 0.47 per CPU h, nothing since 13:18) was stopped at 750 of 1,012 heads to free
  its 3 threads (notes/2026-11-24-plain-time.md).

## Setting

* abs/clq83.sh (exp/prod/side/clq83.sh), loops/CLQ83, log loops/CLQ83.log. climb.py --live loops/UL with cls71e.sh's
  options, plus `--runs 0` (no sketch runs: the final only), `--final-cpu 40` (twee's CPU cap for the final in place
  of 10 x 160 s), -j 3, --cpus 23 (a final starts while fewer than 23 other twee processes run). No --reclimb.
* Its record dir started with a copy of CLS71's true.tsv, fillhints/ and sketches/ (2,420 true lemmas, 35,816
  sketch hints of 85 originals), so its finals have the sketch hints CLS71's final-only finals have (the first: 1,020).
* Excluded (sets/clq83.excl, 1,558 goals; exp/sets/clq83.excl): sets/localheads71 and the 618 targets CLS71 finished
  since its 06:05 instance, the first with 160 s finals (log line 921 on): they had the full final already. The first
  start (15:31) excluded only those since 08:59 and took three old targets; restarted at 15:33 with the wider list.
* A proof's 'direct' rerun (after a final that used true lemmas) keeps the 10 x 160 s cap; it counts in the CPU.
* CPU: 3 threads, HLS2's. CLS71 keeps 10, production 4; total about 20-23 twee processes.

## Measures and decision

* Proofs per CPU h of CLQ83 (its climb.tsv seconds) against CLS71's over the same hours (exp/climbab.py --from; both
  arms), and how many of CLS71's proofs in those hours CLQ83 had failed first (the second stage's share).
* After about 3 hours: if CLQ83 makes at least twice CLS71's proofs per CPU h, keep it as a side loop and propose a
  staged final for the climber once the user's final-only A/B is done; if it is at or below CLS71's rate, stop it.
* Caveat: CLQ83 takes the quick targets first, so CLS71's later targets are harder in both A/B arms alike (the arm is
  by crc32 of the target, not by who runs it first). CLS71's readings after 15:33 are not comparable with those before.

## Crash and restart (16:05)

CLQ83 ended at 16:03:37 with a traceback in climb.py's live refresh: `RuntimeError: dictionary changed size during
iteration` in loop.py build_pools (`for n in self.solved`). A worker's --chain proof adds to lp.solved (under the
lock) while the main thread's refresh iterates it; with three quick finals the proofs come often enough to hit it.
CLS71 runs the same code and never did. Fix (climb.py 8733753): refresh holds the lock. Restarted 16:05:19 (climb.py
3952184); it skips the targets of its climb.tsv. Its 30 minutes before the crash (exp/clqread.py 1570 20123): CLQ83
finished 129, proved 5, 1.43 CPU h, 3.49 per CPU h; CLS71 in the same time 37, 11, 4.39 CPU h, 2.50 per CPU h.
The reading at 18:35 counts both instances.

**Second crash (16:37).** My fix was wrong: `lock` is main()'s local, and refresh() is inside live(), so the first
refresh after the 16:05 restart (refreshes come every 30 minutes, none at start) ended CLQ83 at 16:36:00 with
`NameError: name 'lock' is not defined`. I had not checked the scope. Fixed in 78c430a: main passes its lock to
live(); a symtable check now shows every name refresh() uses is defined. Restarted 16:37:21 (climb.py 3956168); a
waiter checks its first refresh. Reading at 16:36 over both instances (about an hour of running): CLQ83 finished
252, proved 8, 2.83 CPU h, 2.83 per CPU h; CLS71 73, 19, 9.04 CPU h, 2.10 per CPU h. The 3-hour reading moves to
about 18:40.

**Fix verified (17:08):** the first refresh after the 16:37 restart ran at 17:08:13 ("live: refreshed with 53 new proofs
of loops/UL in 7s"); CLQ83 is alive, with no new traceback.

## Result and decision (24 Nov 18:40, exp/clqread.py 1570 20123, both instances)

| | finished | proved | CPU h | per CPU h |
|---|---:|---:|---:|---:|
| CLQ83 (40 s finals, no climbs, -j 3) | 765 | 40 | 8.76 | 4.57 |
| CLS71 (since 15:33, -j 10) | 223 | 44 | 29.63 | 1.49 |

**By the rule (twice CLS71's rate or more): kept.** The ratio is 3.07. A critical look at the rule: CLQ83 runs ahead
on the same queue, so it could skim CLS71's easy targets, and the two rates would then not show what CLQ83 adds. The
overlap says it mostly does not (counted at 18:41):
* CLS71 finished 223 targets since 15:33; 63 of them CLQ83 had failed first, and CLS71 proved 9 of those (14%; their
  proofs need more than 40 s), against 35 of its other 160 (22%).
* Of CLQ83's 42 proofs, 3 were on targets CLS71 also finished since 08:59. CLQ83 ran 768 targets in about 3 hours,
  CLS71 about 70 an hour: most of CLQ83's targets CLS71 would have reached many hours later.
* So CLQ83's proofs are mostly additional and come sooner, at 4.57 per CPU h, against about 1.5 for CLS71's threads now.
  The two together made 86 proofs in 38.4 CPU h (2.24 per CPU h), close to CLS71 alone before 15:33 (about 2.5,
  falling through the day as the near targets go): no controlled gain in the total rate is shown.
* As CLQ83 gets ahead, more of CLS71's targets are ones CLQ83 failed (the second stage: full finals on goals that
  need more than 40 s). 545 unsolved, not excluded goals are left that CLQ83 has not finished; after them it takes only
  newly stalled goals, so its threads will idle.
* Next: the staged final inside the climber (40 s for every new target first, the full final later) is the clean form
  of this; proposed to the user after the final-only A/B, which keeps running unchanged.

**Ran dry (about 21:00).** At 21:25: 1,301 targets finished, 55 proved since 15:31; 3 targets finished in the half hour
before 21:18. It stays on: it takes newly stalled goals as production's fresh runs fail on them, and its threads
are free otherwise.

## exp83b: the quick finals on the local heads (24 Nov 23:49)

**Why.** sets/localheads71 (940 goals: unsolved, the previous goal proved, at 23 Nov 23:30) was left out of both
climbers only to split the work: HLW1's plain 60 s sweep took them, CLS71 the other holes (notes/2026-11-23-
tail-allocation.md, "Changes"). HLW1 ended 24 Nov 08:48 and HLS2 (their second kNN slice) was stopped at 15:30, so they
get only the plain live loop's 60 s W runs (no hints) and production's 5 s runs. 672 of them are still unsolved; none
ever had a climber final (production's hints, 30 siblings and 400 kNN, fill lemmas, sketch hints). CLQ83 had run dry.
**Change.** CLQ83 restarted at 23:49:34 (climb.py 4013658) with EXCLUDE=sets/clq83b.excl (exp/sets/clq83b.excl): only
CLS71's 1,226 targets finished since its 06:05 instance, so the local heads are now open to it; CLS71 still excludes
them, so the final-only A/B is untouched. Its first three targets: nslm_to_aa1 852, R1dist_to_aa1 464 and 460, all
local heads. Reading from CLQ83.log line 1355 and climb.tsv row 1354 on: proofs per CPU h, against its 3.69 before and
the plain W cycles on the same heads (HLW1 0.90 per CPU h). Keep at 1 per CPU h or more; else go back to sets/clq83.excl.

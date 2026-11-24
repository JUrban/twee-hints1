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

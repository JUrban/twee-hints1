# exp52 (candidate): floors for the late classes only when they can compete (`--floor-ratio K`) (21 Nov 13:30)

**Question.** The late-phase classes q (retries of failed goals, --retry-class) and h (heads at the 40 s chain
level, --head-class) each keep a floor of one running job whenever they have waiting goals. Early from zero they
prove about 1% as much per run-hour as the first runs. Does withholding their floors until their yield is within a
factor K of the best class keep the first pass's speed and still give their late gains?

## Why

* Z7 at 30 minutes (notes/2026-11-21-z7-pair.md): 2,196 behind Z7C, with 21,100 runs against 23,100. Its mix line,
  proofs per run-hour over each class's last 300 runs: r 6,885, q 77, h 12, d 44. The q and h floors held about half a
  worker of six.
* On half2, P2O (with q and h) was 650 behind P2N at 30 minutes and caught up by 2 hours. Its gain came later, from
  the head class (notes/2026-11-21-late-combo.md).
* In P2R (P2O's set) between 90 and 180 minutes, first runs proved about 390 per CPU hour, retries 137 and head runs
  about 28. With K = 20, both floors would be back by then; at 30 minutes in Z7 they would be off (20 × 77 < 6,885).

* exp48's first hour (exp/quickstat.py, CPU hours per 15-minute window; "deep" holds class h's 40 s runs):

  | window | P2O first | P2O retry | P2O deep | P2N first | P2N retry | P2N deep |
  |---|---|---|---|---|---|---|
  | 15-30 min | 2,018 / 0.7 h | 30 / 0.2 h | 25 / 0.5 h | 2,243 / 0.9 h | 33 / 0.2 h | 24 / 0.2 h |
  | 30-45 min | 1,074 / 0.7 h | 27 / 0.2 h | 18 / 0.5 h | 907 / 0.9 h | 46 / 0.2 h | 7 / 0.3 h |
  | 45-60 min | 577 / 0.7 h | 32 / 0.2 h | 23 / 0.5 h | 612 / 0.9 h | 54 / 0.2 h | 12 / 0.2 h |

  (proofs / CPU hours.) P2O's deeper runs took 0.2-0.3 CPU h more per window and proved 23 more in 15-60 minutes than
  P2N's; the 0.2 CPU h less of first runs was worth about 165 proofs per window at 45-60 minutes (824 per CPU hour).
  P2O was 422 behind P2N at 60 minutes and 62 ahead at 120. What the A/B has to show is whether the head runs' early
  proofs matter later (their following goals), or only their late ones.

## Change

loop.py `--floor-ratio K` (default off) and `--floor-classes CLS` (default qh). With --mix, a class in CLS is among the
floor classes only while K × yld(class) ≥ the best waiting class's yld, with yld as in the mix line: proofs per
run-second over the class's last 300 runs, with prior 0.5 proofs per 5 s, and running jobs' time so far counted as
spent. Without its floor a class still gets a slot when it has the best yld. A class with no runs is estimated at its
prior (360 an hour), so it gets its floor once the first runs' yield falls below 7,200 an hour at K = 20.

A class without runs keeps its estimate, so the floor comes back only as the first runs' yield falls; the first runs'
own estimate falls steadily during the first pass, so this cannot starve a class for long.

## Smoke test

loops/FRT (13:22, smoke487, 4 workers, 6 minutes, the LATE default plus `--floor-ratio 20`; config.json: floor_ratio
20, floor_classes qh): no errors, 402 solved. Mix lines: q 0 and h 0 runs to 36 s (r at 7,634-12,029 an hour), q 8 and
h 1 at 64 s (r 5,243), q 48 and h 8 at 265 s (r 1,925). On 487 goals the first runs' yield falls within a minute, so the
smoke test shows that the option runs, not what it gains.

## Plan

The floors are the mix's exploration: they keep every class measured. --floor-ratio withholds them where a class
looks poor, so the A/B is judged also by what the h and q classes give: their proofs and the goals after a proved
head, + and − goals and the union per worker-hour, not only the totals.

An A/B after the Z7 pair (about 20:50), when the CPU is free: the LATE default against the LATE default plus
`--floor-ratio 20`. Most of the effect should be in the first two hours, so on all goals from zero, 6 workers each,
3 hours, against the same control. Decision: +260 at 3 hours, or a curve clearly ahead throughout with no loss at 3
hours (the measure is goals solved at each point in time).

## Launch (21 Nov 16:52)

With the user's CPU split (about 10 CPUs for this test, about 10 for the unsolved goals), the A/B is on half2 at 4
workers each, not on all goals at 6. abs/after_z7.sh (exp/after_z7.sh, PID 997587) waits for loops/Z7.done (about
20:50) and starts P2T (control: solve_new.sh's defaults, LATE) and P2U (the same plus `--floor-ratio 20`), half2 from
zero, 3 hours, PIDs in loops/AFTERZ7.pids. Identical half2 runs differ by about 185, so the decision line is +185 at 3
hours, or a curve clearly ahead throughout with no loss at 3 hours, judged also by the h and q classes' proofs.

## Started (21 Nov 20:49)

Z7 ended at 20:49:29; after_z7.sh started both arms at 20:49:57: P2T loop.py 1115326, P2U loop.py 1115327, each with its
transfer loop (-j 2) and derived-rule loop. loops/P2T/config.json has floor_ratio 0, loops/P2U/config.json 20.0;
otherwise the same (retry_class, head_class, knn_ctx 10, yield_discount 2000, reexplore 12:0.25, j 4). They end at
about 23:50.

## Interim at 30 minutes (21 Nov 21:20): P2U +1,006

abs/setcurve.py sets/half2 (goals by minutes after the start); P2O and P2N are earlier half2 arms at 6 workers:

| min | 5 | 10 | 20 | 30 |
|---|---|---|---|---|
| P2T (control, 4 workers) | 4,988 | 9,152 | 13,101 | 14,568 |
| P2U (+ `--floor-ratio 20`) | 5,182 | 9,627 | 13,604 | 15,574 |
| P2U − P2T | +194 | +475 | +503 | **+1,006** |
| P2O (6 workers, 21 Nov) | 6,073 | 11,260 | 14,795 | 16,453 |

The runs by level (loops/<arm>/r1/results.tsv, proofs / runs / CPU hours):

| arm | L0 (5 s) | L1 (40 s) | Vunf@0 | other |
|---|---|---|---|---|
| P2T | 12,142 / 12,283 / 1.18 | 12 / 20 / 0.32 | 19 / 97 / 0.21 | 5 / 24 / 0.09 |
| P2U | 13,294 / 13,482 / 1.45 | 1 / 2 / 0.03 | 29 / 109 / 0.21 | 9 / 33 / 0.09 |

The control's head class ran 20 L1 runs (40 s) for 12 proofs in 0.32 CPU hours; P2U ran 2 and gave that CPU to 5 s
runs (+1,199 runs, +0.27 CPU hours), which proved +1,152. As expected, the floors cost more at 4 workers than at 6:
one worker of four held by each of q, h and d leaves the first runs fewer workers. The decision is at 3 hours,
where LATE's gains come.

## Interim at 1 hour (21 Nov 21:50): P2U +910

| min | 10 | 30 | 45 | 60 |
|---|---|---|---|---|
| P2T (control) | 9,152 | 14,568 | 16,028 | 16,786 |
| P2U (+ `--floor-ratio 20`) | 9,627 | 15,574 | 16,931 | 17,696 |
| P2U − P2T | +475 | +1,006 | +903 | **+910** |

exp/quickstat.py, 30-60 min (proofs / runs / CPU hours): first runs P2T 1,599 / 1,776 / 0.6, P2U 1,610 / 1,961 / 0.9;
retries 27 / 205 / 0.3 and 44 / 325 / 0.4; deep 39 / 320 / 1.0 and 34 / 280 / 0.5. In the second half hour the arms
proved about the same (P2T 2,218, P2U 2,122 by the curve), so the lead is the first half hour's.

The mix lines at 60 min: P2T r 1,324/h, q 100/h (281 runs), h 26/h (45 runs); P2U r 1,085/h, q 92/h (378 runs), h
44/h (2 runs). In P2U the q floor is on again (20 × 92 ≥ 1,085), the h floor still off (20 × 44 < 1,085); it comes
back when the first runs' yield falls below 20 times the head class's.

## Interim at 2 hours (21 Nov 22:50): P2U +1,040

| min | 30 | 60 | 90 | 120 |
|---|---|---|---|---|
| P2T (control) | 14,568 | 16,786 | 17,944 | 18,618 |
| P2U (+ `--floor-ratio 20`) | 15,574 | 17,696 | 18,795 | 19,658 |
| P2U − P2T | +1,006 | +910 | +851 | **+1,040** |
| P2O (6 workers, 21 Nov) | 16,453 | 18,792 | 20,084 | 20,934 |

exp/quickstat.py, 60-120 min (proofs / runs / CPU hours):

| arm | first | retry | deep |
|---|---|---|---|
| P2T | 1,302 / 1,737 / 1.0 | 81 / 684 / 0.9 | 58 / 594 / 2.0 |
| P2U | 1,320 / 2,318 / 1.8 | 122 / 806 / 1.0 | 60 / 561 / 1.0 |

From 1 to 2 hours P2U gained 1,962 and P2T 1,832. P2U spends half the control's CPU on deep runs (1.0 against 2.0
CPU hours, mostly the head class's L1 runs) for the same proofs, and puts it into first runs and retries. The mix lines
at 120 min: P2T h 90 runs at 17/h, q 973 at 59/h, r 802/h; P2U h 3 runs at 25/h, q 1,188 at 108/h, r 530/h. P2U's h
floor is still off (20 × 25 < 530), close to coming back on.

## Result at 3 hours (21 Nov 23:50): P2U +789, accepted

| min | 30 | 60 | 120 | 150 | 180 |
|---|---|---|---|---|---|
| P2T (control) | 14,568 | 16,786 | 18,618 | 19,269 | 20,087 |
| P2U (+ `--floor-ratio 20`) | 15,574 | 17,696 | 19,658 | 20,402 | 20,876 |
| P2U − P2T | +1,006 | +910 | +1,040 | +1,133 | **+789** |
| P2O (6 workers, 21 Nov) | 16,453 | 18,792 | 20,934 | 21,286 | 21,524 |

* exp/quickstat.py, 120-180 min (proofs / runs / CPU hours): first runs P2T 849 / 1,310 / 0.9, P2U 616 / 1,586 / 1.6;
  retries 159 / 838 / 1.0 and 116 / 793 / 1.0; deep 66 / 512 / 2.0 and 62 / 442 / 1.3. In the third hour the
  control gained 1,469 and P2U 1,218: P2U had used up more of the easy goals, so its first runs proved 39% against the
  control's 65%. The lead narrowed by 251 but stayed four times the decision line.
* The floors come back on their own: at the end P2U's mix line had r 204/h, q 72/h (1,974 runs), h 18/h (22 runs),
  so 20 × 18 ≥ 204 and the head class has its floor again.
* Portfolio at 3 hours: P2U-only 1,077, P2T-only 288, union 21,164 on 8 workers (24 worker-hours, 882 per
  worker-hour) against P2U's 20,876 on 4 (12 worker-hours, 1,740 per worker-hour). The control adds nothing a
  second worker set would not.

**Decision: accepted.** solve_new.sh's LATE now ends with `--floor-ratio 20` (0e6996b, 21 Nov 23:52). The test ran 3
hours; the narrowing in the third hour is a reason to watch the next long from-zero run (all goals, 8 hours), where
the late classes matter most.

exp53 (notes/2026-11-21-renorm-zero.md) started at 23:51:52 with the new default in both arms.

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

An A/B after the Z7 pair (about 20:50), when the CPU is free: the LATE default against the LATE default plus
`--floor-ratio 20`. Most of the effect should be in the first two hours, so on all goals from zero, 6 workers each,
3 hours, against the same control. Decision: +260 at 3 hours, or a curve clearly ahead throughout with no loss at 3
hours (the measure is goals solved at each point in time).

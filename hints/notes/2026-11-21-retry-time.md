# exp50: shorter L0 retries (`--retry-time T`) (21 Nov 06:50)

**Question.** After the first pass, most of the CPU goes to fresh L0 retries of goals that failed before, now in a
new context, and 90–95% of them fail. Retry proofs come later than first-run proofs, but most still come well
within 5 s. Does a 3 s limit for these retries give more proofs per CPU hour, with few of their proofs lost?

## Why

The L0 retries of four from-zero runs (results rows at L0 of goals already run, quick rows left out; dt is the run's
CPU time, near its abstract time). The T columns replay each retry at a T s limit: a proof counts if it came within
T s, and a failed run costs T/5 of its time.

| run | retries | proved | CPU h | proofs per CPU h | T=2: kept, CPU, per CPU h | T=3 | T=4 |
|---|---:|---:|---:|---:|---|---|---|
| P2J (half2, 5 h) | 4,920 | 859 | 6.8 | 127 | 60%, 42%, 179 | 79%, 62%, 162 | 89%, 81%, 139 |
| P2K (half2, 5 h) | 4,980 | 442 | 7.5 | 59 | 52%, 41%, 75 | 73%, 61%, 71 | 84%, 80%, 62 |
| P2H (half2, 5 h) | 4,880 | 567 | 7.3 | 78 | 59%, 41%, 111 | 76%, 61%, 97 | 85%, 81%, 83 |
| Z6 (all, 12 workers, 8 h) | 24,100 | 2,149 | 30.8 | 70 | 70%, 41%, 119 | 84%, 61%, 96 | 93%, 81%, 80 |

* In Z6, failed L0 retries after 3 hours took 28.6 of its 96 CPU hours and proved 1,078 of 22,164 (5%).
* By phase, the share of retry proofs within 1 / 2 / 3 s: P2J early 21% / 71% / 86%, late 13% / 51% / 74%; Z6 early
  48% / 82% / 91%, late 26% / 59% / 78%. (First runs: 86–89% within 1 s, so exp49 uses 1 s there.)
* At T = 3 a retry proves 1.2–1.4 times as much per CPU hour and keeps 73–84% of the proofs. At T = 2 it is 1.3–1.7
  times as much but keeps only 52–70%. T = 3 is the safer test.
* The replay is static. A retry that would have needed 3–5 s now fails, counts as a failure (it sorts later under
  --fail-order) and waits for its next context change or a deeper level. The CPU it frees goes to other retries
  only while retries wait for workers. Late in Z6 the variants at level 0 (V@0) held more workers than the
  retries, at 13 proofs per CPU hour, against 35 for the retries' 2–5 s part. Only the A/B can tell the net.
* With --no-fresh-states (solve_new.sh's default) a fresh L0 run keeps no state, so a deeper level starts over
  in either case: the shorter retry loses no resumable work.

## Change

loop.py `--retry-time T` (default off):
* A fresh L0 run of a goal that failed a fresh L0 run before (nf > 0, the --fail-order count) runs at T seconds
  instead of T0. Everything else stays: a failure counts in nf, and the deeper levels and variants are unchanged.
* With --quick, the T0 run that follows a failed quick run is still at T0, since a failed quick run is not counted.
* Its results row gets a column `r=1`.

## Smoke test

loops/RTT (06:44, sets/smoke487, 2 workers, 12 minutes, `LOOPARGS="--retry-time 3"`), against QKC (04:46, the same
setting without the option; run at another time, so a check for errors and r=1 rows, not a comparison).

## Plan

A third arm beside exp49, on the same base B and against the same control P2R:
* **P2S:** B + `--retry-time 3`, half2 from zero, 6 workers, 5 hours.
* It starts together with P2Q and P2R: abs/after48b.sh waits for P2R's line in loops/AFTER48.pids (written by
  abs/after48.sh when it starts exp49) and starts P2S with P2R's LOOPARGS plus `--retry-time 3` (a non-empty
  loops/P2S.args replaces them).
* CPU: three arms at about 7 each, the proof worker 2, the sweep 1. stepjlive3 was stopped at 06:45, since its last
  three cycles joined nothing.

## Measures

* `abs/setcurve.py sets/half2 P2R P2Q P2S --at 30,60,120,180,240,300`; one-arm goals (+/−, union, unique per CPU
  hour against P2R).
* The r=1 rows: runs, proofs, CPU hours by half hour, against P2R's L0 retries; exp/quickstat.py on all three.
* Decision: P2S ≥ P2R + 185 at 5 hours makes `--retry-time 3` a default for Z7.

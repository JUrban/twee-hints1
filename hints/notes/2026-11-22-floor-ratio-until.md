# Floors that wait, only early: `--floor-ratio-until 120` (exp60)

Written 22 Nov 2026, 15:34 UTC.

## Why

* `--floor-ratio 20` (exp52, 21 Nov): the retry (q) and head (h) classes keep their worker floor only while 20 times
  their yield reaches the best class's. Side by side on half2 from zero it gave +789 at 3 hours (P2U against P2T),
  and it went into solve_new.sh's LATE default.
* Z8 (the defaults with it, on all goals, 22 Nov) against Z7 (the day before, without it): +2,275 at 30 minutes,
  +1,820 at 1 hour, level by 3 hours, then −408 to −471 from 4 to 6 hours. That is across times (noise up to about
  400), but the shape fits: the floors that wait help while the first runs pay hugely, and may cost later.
* exp59 (notes/2026-11-22-hub-roots.md) saw the same mechanism: in Z8 the head class got 171 runs in 6 hours, as
  the 5 s retries out-yielded it.
* loop.py `--floor-ratio-until MIN` (22 Nov 07:06; smoke FRS clean) applies the rule only in the first MIN minutes.

## Design

abs/exp60.sh (exp/exp60.sh): P3A (control: solve_new.sh's defaults, `--floor-ratio 20` throughout) and P3B (the same
with `LOOPARGS="--floor-ratio-until 120"`), sets/half2 from zero, 4 workers each, 6 hours, abs/or_test2.sh. Both have
solve_new.sh's new `--lemma-ax` default. abs/after_exp55.sh (exp/ copy, PID 2235753, 15:34) starts it 10 minutes after
exp55 ends (about 20:24) unless loops/EXP60.skip appears.

**A third arm (18:29):** P3C = the same with `LOOPARGS="--knn-drift 5 --knn-drift-after 60"` (loop.py 1b4d930; smokes
KDA, KDB). exp55's drift retries cost 216 at 30 minutes and 149 at 60, and gave +109 to +122 from 2 to 4 hours
(notes/2026-11-22-knn-drift.md); the drift count now admits goals only after the first hour. P3C shares P3A as its
control; with exp55 it also gives a second reading of the drift retries (not an exact replica: they start later).
(20:40) Closer to a replica than meant: the count admitted only 54 goals in P2Z's first hour, and the sort of the
retry class by the count, the likelier cause of the early cost, still starts at once (notes/2026-11-22-knn-drift.md,
"Correction").
Three arms of 4 workers and production's 6 are about 20 CPUs.

## Measures

* abs/setcurve.py sets/half2 P3A P3B --at 30,60,120,180,240,300,360; exp/armdiff.py P3B P3A (only-goals, union).
* The mix lines: class h and q runs per hour before and after minute 120.
* Decision (each test arm against P3A): ≥ +200 at 6 hours (half2 replicas differed by up to about 185). Within ±200, a replica first.

## Early readings, and a measured A/A (22 Nov 21:08)

`--floor-ratio-until 120` changes nothing before minute 120, so **P3B is the control's twin for the first two
hours**: their difference until then is the noise of a side-by-side half2 pair.

| | 10 min | 20 min | 30 min |
|---|---:|---:|---:|
| P3A (control) | 9,649 | 13,268 | 15,203 |
| P3B (= P3A until 120 min) | 9,268 | 12,955 | 14,838 |
| P3C (`--knn-drift-after 60`) | 9,294 | 12,972 | 14,981 |
| P3B − P3A | −381 | −313 | −365 |
| P3C − P3A | −355 | −296 | −222 |

* The twins' 30-minute gap is throughput: in its first 30 minutes P3A completed 13,154 runs against P3B's 12,530,
  with nearly equal run seconds (5,985 against 6,014). At equal abstract work (exp/abscurve.py) the gap at P3A's
  20 minutes is −166 (P3B) and −219 (P3C).
* The machine is busier than during exp55: 1.21 CPU s per abstract second, against 0.92-0.97 for P2X and P2Z.
* So early gaps of 200-400 between side-by-side half2 arms are noise. exp55's early "cost" (−216 at 30 minutes)
  is within it, and at equal abstract work P2Z against P2X was +118 at 10 minutes, +50 at 20, −175 at 30, −75 at
  60, +169 at 120 and +201 at 360. The test of `--knn-drift-order-after` is not needed unless P3C falls further
  behind than P3B does.

60-minute reading (21:36): wall minutes (setcurve) P3A 17,541, P3B 17,196 (−345), P3C 17,312 (−229). At equal abstract
work (abscurve, at P3A's 55 minutes): P3A 17,277, P3B 17,162 (−115), P3C 17,317 (+40). In the second half hour
P3A's runs took 1.07 CPU s per abstract second, P3B's 1.18 and P3C's 1.20: the control's processes ran faster.
The cause is not known: a sample of the running twee processes' CPUs (2 sockets, 28 cores each, 2 threads per core)
shows each arm spread over the machine, not clustered; other users' load on shared cores is a guess. Wall-time readings
then favour P3A, so the 6-hour decision is read both ways, and a test arm must clear +200 at equal abstract work
too.

## 120 minutes: the end of the twin window, and the sockets (22:39)

| | 60 min | 90 min | 120 min |
|---|---:|---:|---:|
| P3A (control) | 17,541 | 18,582 | 19,520 |
| P3B (= P3A until here) | 17,196 | 18,310 | 19,061 |
| P3C | 17,312 | 18,435 | 19,299 |
| P3B − P3A, wall | −345 | −272 | **−459** |
| P3B − P3A, equal abstract work | −150 (P3A's 60) | **−27** (P3A's 90) | – |
| P3C − P3A, equal abstract work | +15 | **+148** | – |

* By wall time the twins ended their identical first two hours 459 apart; at equal abstract work (exp/abscurve.py)
  27 apart. P3A's runs took 1.02 CPU s per abstract second in hours 2 and 3, P3B's 1.16 and 1.13, P3C's 1.13 and 1.14.
* The cause: sockets. In a 12-second sample at 22:36 the running twee runs were on socket 0 for P3A 28 of 40, for
  P3B 10 of 32, P3C 14 of 38, production 2 of 36 (/proc/cpuinfo: CPUs 0-27 and 56-83 are socket 0, 28-55 and
  84-111 socket 1, CPU i and i+56 share a core). The kernel keeps runs near their loop.py, and three loops shared
  socket 1.
* So wall-time readings of side-by-side arms carry a throughput bias of their own, up to about 10% here, besides
  the dispatch noise. The 6-hour decision is read at equal abstract work, and by wall time as a second view.
* **Fix from 22:37-22:39** (abs/pin_exp60.sh, then abs/pin_exp60b.sh; copies in exp/): CPU affinity per process tree.
  Each arm and production get 14 whole cores, 7 per socket, one logical CPU per core (P3A 0-6,28-34; P3B 7-13,35-41;
  P3C 14-20,42-48; production with its side loops and proofq 21-27,49-55); the hyperthread siblings are left to the
  machine's other users. The same for all arms, from 2 hours 2 minutes on; P3B's change of rule starts at 2 hours.

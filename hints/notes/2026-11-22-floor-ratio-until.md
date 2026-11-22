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

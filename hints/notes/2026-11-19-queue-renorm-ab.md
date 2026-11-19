# Deep runs without queue renormalisation: an A/B test in production (exp26)

Started 19 Nov 2026, 05:53 UTC, with production ul57 (abs/ul57.sh, hints/exp/portfolio_ul57.sh). Follows
notes/2026-11-19-hint-cost.md (exp25).

## Why

* In a hinted 10 s run, renormalising the queue is 27% of the CPU (the profile). Under `--abstract-time` it is free
  in abstract time, so its 5% budget never binds.
* At 20 s, turning it off left the output byte-identical and saved 16% of the CPU.
* **exp25 (05:29-05:49), 6 walls at 80 s**, exp11's chain commands on production's binary and flags:

| wall | base CPU s, proved | `--queue-cost 0.008` | never (`--cp-renormalise-threshold 1000`) |
|---|---|---|---|
| nil3_23_32_to_28 392 | 20.7, yes | 21.2, yes | 21.6, yes (identical output) |
| aa1_14 482 | 96.1, yes | 106.5, yes | 78.6, **no** |
| mbol_nil3_a 476 | 105.0, yes | 98.5, yes | 83.1, yes |
| KK_Kcom_to_aK1 276 | 134.6, no | 132.6, no | 124.1, no |
| aK2_eq_aK3_c 407 | 177.4, no | 195.7, no | 138.6, no |
| aK2_eq_aK3_q 254 | 289.1, no | 236.0, no | 167.4, no |
| all 6 | **822.8** | 790.5 (−4%) | **613.4 (−25%)** |

* Peak RSS was no higher without renormalisation (e.g. 787 against 949 MB on aK2_eq_aK3_q 254).
* At 80 s the outputs differ: renormalising rescores pairs, so the search order changes. So "never" is a cheaper,
  different search, not a free speedup. Whether it proves as much per run needs volume.

## Design

* loop.py `--ab-args ARGS` (516f416). The deep runs of half the goals get ARGS: runs above the first level's
  budget, so L1, L2, L3 and the 80 s variants, but not p9 and not the 5 s levels. The half is fixed by the parity
  of crc32(goal name), so a goal's resumes stay in its arm. Their results rows carry `ab=1`.
* Arm B: `--cp-renormalise-threshold 1000` (the queue is never renormalised). Arm A: production as before.
* The ratio rule's yields pool both arms, as before. A goal's arm does not decide which level it runs next.
* **The population is production's own deep runs:** near-frontier goals in their current context, about 200 80 s
  runs an hour.

## Measures

* Per level and arm (`levyield.py loops/UL/r5/results.tsv ROW`, L1 against L1/B): runs, proofs, CPU h, proofs per
  CPU hour. The question is whether B's proofs per CPU hour are at least A's. A cost 25% lower with a proof rate
  per run at least 80% of A's would favour B.
* Noise: at about 10% per run and about 100 runs per arm per hour, an arm proves about 10 an hour (±3). An hour
  shows the CPU difference clearly; the proof rates need 2-3 hours to separate by 20%.
* Memory: memwatch kills (>7 GB a run) by arm.

## Results

* 06:02: production went on as ul58, with the cascade 5,40,80,160,320 (40 s chain level; abs/ul58.sh). The A/B goes
  on unchanged, and is measured from ul58's first row (103428): L1 (40 s), L2 (the 40 -> 80 s resume), L3 (160 s)
  and the 80 s variants, each by arm. ul57's 10 minutes (rows 102781-103427) are too few to count.

**07:05, ul58's first hour (rows from 103428):**

| level | arm | runs | proofs | CPU h | per CPU h | CPU s a run |
|---|---|---:|---:|---:|---:|---:|
| L1 (40 s) | A | 114 | 6 | 3.01 | 1.99 | 95 |
| L1 (40 s) | B | 97 | 4 | 2.05 | 1.95 | 76 |

* B costs 20% less a run, as exp25 found at 80 s (25%). Its proofs a run are 4.1% against A's 5.3%. With 10 proofs
  in all, that difference is noise (Fisher p about 0.75).
* No L2 (the 40 -> 80 s resume) or 80 s variant rows yet: after the restart most workers ran 5 s levels.

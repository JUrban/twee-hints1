# Tail allocation: CPU by measured yield (23 Nov, exp72)

Written 23 Nov 2026 23:40. Production's tail (3,224 unsolved of 51,784 at 23:33) gets a few proofs an hour from several side loops.
This note compares their yields per CPU hour from their own records and moves CPU accordingly. The climber
changes are in [2026-11-23-climber-restart.md](2026-11-23-climber-restart.md) ("exp71", "CLHL4 stopped").

## Yields

The plain live loop (cond/PLNL/log, every cycle since each setting began; run time is twee's seconds column of the
cycles' results.tsv):

| setting | since | runs | proofs | run time h | per h |
|---|---|---:|---:|---:|---:|
| N | 23 08:46:27 | 6,555 | 4 | 4.5 | 0.88 |
| L | 23 12:38:29 | 20,961 | 4 | 18.0 | 0.22 |
| H | 23 20:56:00 | 59 | 3 | 1.5 | 1.99 |

N: 30+10 siblings, 100 kNN, 5 s. L: 100+30 siblings, 400 kNN ranked by lr2, 5 s. H: the first heads only, 100+30
siblings, 400 kNN, 60 s. HDW1 (H's setting as a one-off sweep on the 92 first heads, 17:00-17:49) proved 4 in 2.25 CPU h.

The climbers (exp/climbread.py; CPU h is the sum of their runs' seconds):

| climber | targets | finished | real proofs | CPU h | per CPU h | proved |
|---|---:|---:|---:|---:|---:|---|
| CLU | 986 | 950 | 22 | 27.90 | 0.79 | aK2_eq_aK3_1243b__goal_445, aK2_eq_aK3_gen__goal_495, aK2_eq_aK3_1243__goal_342, aa1_45_c__goal_323, nil3_18__goal_290, nsmr_to_aa1__goal_732, nsmr_to_aa1__goal_612, Kproperties_1__goal_314, aK2_eq_aK3_r__goal_266, lra2aa__goal_418, aK2_eq_aK3_gen__goal_519, ns_to_aa1_b__goal_610, aip_to_aK1__goal_185, mbol_to_aK1__goal_550, mbol_lem2__goal_512, mbol_to_aK1__goal_552, mbol_to_aK1__goal_554, mbol_nil3_a__goal_494, mbol_nil3_a__goal_342, nil3_1K_f__goal_325, aK2_eq_aK3_r__goal_275, Kproperties_1__goal_310 |
| CLHL3 | 21 | 19 | 0 | 4.24 | 0.00 |  |
| CLHL4 | 23 | 21 | 0 | 4.70 | 0.00 |  |
| CLA67 | 56 | 54 | 2 | 9.05 | 0.22 | aa1_14__goal_533, gbol_to_aK1__goal_460 |
| CLB67 | 61 | 59 | 7 | 9.12 | 0.77 | aK1_to_aK2__goal_76, aK2_eq_aK3_e__goal_326, aK2_eq_aK3_h__goal_279, gbol_to_aK1__goal_460, mbol_lem1__goal_391, mbol_com__goal_71, mbol_to_nil3__goal_623 |
| CLK69 | 9 | 9 | 0 | 1.51 | 0.00 |  |

Production itself: in ul76's 1,800 runs (21:14-23:23) 5 proofs in 11.6 CPU h (0.43 per CPU h); sk@1:0 2 in 7.0.

## Changes (23:30-23:40)

* **The plain live loop without L** (abs/plainlive5.sh, exp/prod/side/plainlive5.sh, PID 3755461 since 23:39): N and H
  every 30 minutes on changed problems. L took 50-60 minutes of each cycle's 3 threads.
* **exp72, a plain 60 s sweep on the local heads** (HLW1 in cond/SWEEPQ.txt; abs/sweepq.sh, bash 3753974, waiting for
  "exp67 done" in loops/EXP67.pids, about 03:00): the 940 unsolved goals whose previous goal is proved, the 88 first
  heads left out (exp/sets/localheads71). H's setting (`--time 60 --sibs 100 --after 30 --knn 400`), 3 threads,
  about 12 hours. Proofs via loops/CI3 into loops/UL.
* **CLS71 excludes them** (restarted 23:33 with `--exclude sets/localheads71`), so the climber takes the other holes.
* **CLHL4 stopped** (23:30): 0 real proofs in 4.7 CPU h, on the heads exp67 climbed at the same time.

## Readings

* HLW1: proofs per CPU h, against HDW1's 1.78 on the first heads.
* CLS71: real proofs per CPU h (exp/climbread.py CLS71) and production's sk proofs in the originals it climbed.
* The plain live loop: N and H per h as above, from cycle 23 on.

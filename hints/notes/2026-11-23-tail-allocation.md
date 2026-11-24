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

## exp73: production's climb-hint member with the long lemma lists (23:45)

sk@1:0 (40 s fresh after L0: the pool plus the original's climb hints, and its fill lemmas as axioms) is production's
top member: 2 of ul76's 5 proofs, 7.0 of its 11.6 CPU h. Its lemma axioms are the default 6 siblings and 30 kNN. On
the frozen heads, exp67's climber with 30 siblings and 400 kNN proved 7 against 2 with 6 and 30 at the same CPU (+6 −1;
sign test p = 0.125 two-sided, so suggestive only), and the plain live loop's best setting (H) also takes 400 kNN.

* loop.py: members skkNsM (sk's hints and fill lemmas with N kNN and M sibling lemmas; `sk` alone is unchanged).
* abs/ul78.sh (exp/prod/ul78.sh): ul77 plus skk400s30@1:0, after sk@1:0. loop.py PID 3756717 since 23:43 (ul77
  stopped 23:43, 2 new proofs in its 150 runs). Explored and ordered by live yield like every member.
* Checked: its first runs are labelled Vskk400s30@1:0; a problem (aa2_12 355) has 400 lemma_knn, 30 lemma_goal and 14
  lemma_fill axioms; 40 abstract s took 76-80 s.
* Reading: exp/memberyield.py over ul78's runs: skk400s30@1:0 against sk@1:0, proofs per CPU h and the goals only one
  of them proved.

## exp72 started, and its proofs go in early (24 Nov 04:05)

* HLW1 started 24 Nov 03:46:52 (cond/SWEEPQ.log, context 48,578), after exp67, in sets/localheads71's order
  (alphabetical by original). At 04:05: 34 runs, 3 proved, 0.81 CPU h.
* Its first 3 proofs (aa1_45_c 365, aa3_45 485, aa_instances_4 384) were new to production. abs/sweepq.sh imports a
  sweep's proofs only at its end, about 12 hours on, and each proved local head gives its later siblings a new lemma.
  So abs/hlwimport.sh (exp/prod/side/hlwimport.sh, bash 3816406) imports them every 30 minutes through loops/CI3
  while the sweep's condprove runs (cond/HLW1.parts); condimport.py skips goals already in loops/CI3, so the sweep's
  own final import adds the rest. The first 3 were imported and merged by hand at 04:03.
* If the rate holds (HDW1 on the first heads: 1.78 per CPU h), plainlive5's H cycle should take the local heads too,
  not only the first heads, so that new local heads get their plain 60 s run as they appear.

### HLW1 resumed with 5 threads (24 Nov 04:50)

* At 04:49: 122 runs, 4 new proofs (aa1_45_c 365, aa3_45 485, aa_instances_4 384, aK2eq_1234 427), 3.03 CPU h, 1.32 per
  CPU h; production's last 1,000 runs 0 in 3.5 CPU h. The 30-minute import merged the fourth at 04:31.
* HLW1's condprove was stopped at 04:50 (123 rows); abs/sweepq.sh then imported (nothing new: all 4 were in) and ended,
  HLW1 being its last line. abs/hlw1b.sh resumes the same dir with 5 threads and the current production context
  (cond/HLW1.trusted2, 48,584 goals) for the other 813 goals; condprove.py skips the done ones. The import loop runs
  again on the new condprove (bash 3828344). The stalled-goal climber gives up the 2 CPUs by its own cap.
* So HLW1's rows are in two contexts: the first 123 in cond/HLW1.trusted, the rest in cond/HLW1.trusted2. For a
  per-CPU-h reading this does not matter; it is a production sweep, not an A/B.

## plainlive6: the local heads in the live loop (prepared 24 Nov 04:53)

* When HLW1 ends, its local heads should keep getting plain 60 s runs as their problems change. plainlive's H reruns
  every changed problem, and with the kNN lists nearly every problem changes every cycle (c29H: 79 of 85 first heads);
  on about 935 local heads that would be 15-20 CPU h a cycle.
* So W reruns a local head only when its axioms or sibling lemmas changed: condprove.py `--prev-ignore-knn` compares
  the problems without their lemma_knn_* lines. A newly proved sibling (the unlock this is for) triggers a rerun; a moved
  kNN list does not. Smoke: 4 HLW1 goals in the 04:50 context all rerun without the flag and are all SAME with it;
  aa1_45_c 368, whose sibling 365 was proved in between, reruns with it.
* condprove.py `--prev DIR,DIR` (the first dir that has the goal decides) and exp/heads.py `--local` were added for it.
* abs/plainlive6.sh (exp/prod/side/): N and H as plainlive5, plus W on `heads.py --local` minus the first heads, first
  --prev cond/HLW1. abs/plainlive6_start.sh (bash 3829136) waits for "HLW1 done" after "HLW1 resumed" in
  cond/SWEEPQ.log, stops plainlive5 after its cycle and starts plainlive6 (PID in cond/PLNL6.pid).
* Reading: W's runs and proofs per cycle (cond/PLNL/log c<k>W), against H's.

## ul82: production with 4 workers (24 Nov 04:57)

Production's last 30,000 runs (loops/UL/r5/results.tsv, several instances), by kind:

| kind | runs | proofs | CPU h | per CPU h |
|---|---:|---:|---:|---:|
| L0 (fresh 5 s) | 2,430 | 22 | 7.8 | 2.81 |
| L1 (40 s) | 868 | 32 | 21.2 | 1.51 |
| L2-L4 | 38 | 0 | 3.5 | 0 |
| the optional variant members | 26,664 | 26 | 101.5 | 0.26 |

The variants fill the workers whenever no fresh level is due, and took 76% of the CPU at 0.26 per CPU h. The plain
side loops measure 0.88 (N) to about 1.8 (HDW1) per CPU h, and HLW1 1.32 so far. ul81's last 1,900 runs (2 hours)
made 0 proofs. So ul82 is ul81 with 4 workers instead of 6 (abs/ul82.sh, exp/prod/ul82.sh; loop.py 3830111, log
loops/UL82.log): the fresh levels still run, somewhat later, and the 2 CPUs go back to the side loops (the stalled-goal
climber takes them by its cap until exp81 starts). Reading: production's proofs per CPU h and per hour against ul81's.

## ul83 (24 Nov 07:34)

ul82 (J=4, 04:57-07:34): 2,501 runs, 9.4 CPU h, **0 proofs**. By member: Vs12 506 runs, Vk1000 439, Vkd 201, Vr2 141,
Vs40 139, Vunf 138, Vk400 138, Vk200 130, Vk60 126, Vnom 125, Vk100 124, L0 122, Vsk 109, L1 63 (2,316 variant runs). Its
cascade did follow HLW1's new proofs: 71 runs on the 3 goals after each, 0 proved. In the same time the stalled-goal
climber, restarted at 06:05 with 160 s finals, proved 5 targets in 7.36 CPU h (0.68 per CPU h;
notes/2026-11-23-climber-restart.md) and HLW1 about 0.6. **ul83 = ul82 with J=2** (abs/ul83.sh, exp/prod/ul83.sh); the
climber starts climbs while fewer than 20 other twee processes run, so it takes the 2 threads. Reading: ul83's
proofs and the climber's per CPU h over the next hours.

## HLW1 done (24 Nov 08:48)

The plain 60 s sweep of the local heads (sets/localheads71; 100 earlier and 30 later siblings, 400 kNN lemmas; 3 threads
03:46-04:50, then 5 with the context cond/HLW1.trusted2) ended at 08:48:11: **936 runs, 20 proofs (915 NO, 1 timeout),
22.29 CPU h, 0.90 per CPU h**, all 20 in loops/UL (imported every 30 minutes by abs/hlwimport.sh and at the end). The
proofs are from 15 originals (nslm_to_aa1 3, ns_to_aa1_c 3, nil3_25 2); median 24.8 s, the longest 122.7 s (wall).
The rate did not fall off: 14 proofs by 07:48, 20 by 08:18 (the later heads alphabetically are the larger originals).
plainlive6 (abs/plainlive6_start.sh) takes over after plainlive5's current cycle; its W cycles run the same setting on
local heads whose siblings changed since HLW1 (`--prev cond/HLW1 --prev-ignore-knn`). HLW1's 5 threads go to the
climber (up to its -j 6) and the experiments.

## plainlive6 started (24 Nov 09:04)

plainlive5 stopped after its cycle c38 (09:03:59); abs/plainlive6_start.sh started abs/plainlive6.sh at 09:04:03, PID
3879710, its first --prev c38N, c38H and cond/HLW1. Cycle c39: 83 heads, 929 other local heads (c39.lheads). Reading:
the W cycles' runs and proofs per CPU h, against HLW1's 0.90.
First cycle c39: N (5 s) 1,459 runs, 0 proofs, 09:04-09:23; H (heads, 60 s) 59 runs, 0 proofs, to 09:53; W from 09:53. W's
first rows: aa1_45_b 370-398 SAME (unchanged since HLW1 apart from kNN lemmas, not rerun), aa1_45_c 343, 350 and 355
rerun: each gained lemma_goal_365 (aa1_45_c 365, proved by HLW1) as a later sibling, the only line that changed.

## ul84 (24 Nov 11:23)

Totals at 11:18 (loops/TRUSTNOW/t1118): 48,947 trusted, holdout 5,476, 353 more than at 07:29. ul83 (2 workers,
07:34-11:23): 2,250 runs, 98 proofs, 95 of them at L0 (1,555 L0 runs, 4.06 CPU h). By hour of the instance: runs/L0/THM
398/75/3, 584/281/1, 703/661/77, 576/538/17. The climber's chains (62 proofs 08:59-11:18) give the goals after each
proof new sibling lemmas, and the cascade's fresh L0 runs prove many of them; GML and XFL also match the new runs'
rules and steps (166 and 23 of the 353 goals have a fresh proof file there). With 94% of its runs at L0 production was
saturated, so **ul84 = ul83 with J=4** (abs/ul84.sh, exp/prod/ul84.sh). Attribution note: the solved.tsv files of GML and
other side loops mirror loops/UL's, so they cannot say who proved a goal; the climber's log, results.tsv THM rows and
fresh proof files can (overlapping).

# exp48: the two late-phase winners together, and with exp46/47's changes (21 Nov 03:37)

**Question.** exp44 (`--retry-class`, P2H) and exp45 (`--yield-discount 2000 --reexplore 12:0.25`, P2J) both lead
the control P2K at 4 hours (+697, +796; notes/2026-11-20-retry-class.md, notes/2026-11-20-yield-discount.md). Do
they stack? And do exp46 (`--knn-ctx 10`, notes/2026-11-21-knn-ctx.md) and exp47 (`--head-class`,
notes/2026-11-21-head-class.md) add on top? Mine.

## Design (changed at 03:37 from separate exp46/exp47 arms on --retry-class)

Two arms on sets/half2 from zero, abs/or_test2.sh, 6 workers, 5 hours, when exp44/45 end (about 04:40):
* **P2N:** `--retry-class --yield-discount 2000 --reexplore 12:0.25`. Against P2H and P2J: do the two stack?
* **P2O:** P2N + `--knn-ctx 10 --head-class`. Against P2N: do the two new late-phase changes add?

Why not one arm per change: three arms (about 30 CPUs plus the rest) against two (about 24 with production paused),
after a night above the 20-CPU target. If P2O wins, one more arm separates exp46 from exp47 (or Z7 takes both).

Launch: abs/after4445e.sh (replaces abs/after4445d.sh) waits for loops/exp4445.done, then up to 20 minutes for
loops/GO48 (written after the 5-hour result), then starts the arms with LOOPARGS from loops/<ARM>.args if present,
else the options above; and abs/stepjlive3.sh. Production stays paused: its own loop proved 2 in its last 2,000 runs.

## Measures

* `abs/setcurve.py sets/half2 P2K P2H P2J P2N P2O --at 30,60,120,180,240,300`; one-arm goals.
* windows.py by label (L1 runs; class h's yield in P2O's mix line); P2O's knn_ctx.tsv runs and proofs;
  exp/latency.py.
* Decision: P2N ≥ max(P2H, P2J) + 185 at 5 hours makes the pair solve_new.sh's default; P2O ≥ P2N + 185 adds the
  exp46/47 options. Then Z7 on sets/all against Z6.

## Launch (21 Nov 04:36)

exp44/45 ended 04:35: P2K 21,147, P2H 21,597, P2J 21,706 (both over the +185 rule). loops/GO48 written 04:36 with no
.args files, so the arms run the options above: P2N loop.py PID 66396, P2O 66394 (loops/AFTERZ6.pids); stepjlive3
66377. They end at about 09:40. The bar for P2N is P2J's 21,706 + 185 = 21,891 (the union P2H ∪ P2J was 21,924).

## Interim at 1 hour (21 Nov 05:37)

| arm | 15 min | 30 min | 45 min | 60 min |
|---|---:|---:|---:|---:|
| P2K (exp44/45 control) | 13,737 | 17,103 | 18,242 | 19,009 |
| P2H | 13,653 | 16,748 | 17,944 | 18,745 |
| P2J | 13,360 | 16,961 | 18,212 | 19,161 |
| **P2N** | 13,753 | 17,048 | 18,325 | **19,214** |
| P2O | 13,450 | 16,453 | 17,886 | 18,792 |

P2O is 422 behind P2N. It ran about 1,000 fewer L0 runs in the first hour (17,446 against 18,478): class h took a
worker for 49 L1 runs (20 proved, 0.8 CPU hours; P2N's L1 17 runs, 8 proved), the deeper levels 473 runs against 381,
and --knn-ctx flagged 87 goals at the last rebuild (221 waiting). P2H's early cost (−264 at 1 hour) turned into
+1,128 at 3 hours; the 3-hour and 5-hour marks decide.

## Interim at 2 hours (21 Nov 06:37)

| arm | 60 min | 90 min | 120 min |
|---|---:|---:|---:|
| P2K (exp44/45 control) | 19,009 | 19,728 | 20,004 |
| P2H | 18,745 | 20,027 | 20,611 |
| P2J | 19,161 | 19,879 | 20,124 |
| P2N | 19,214 | **20,356** | 20,872 |
| P2O | 18,792 | 20,084 | **20,934** |

P2O made up the 422 and leads by 62; P2N leads P2H by 261 and P2J by 748 at 2 hours (P2H then gained 986 to its 5-hour
21,597, P2J 1,582 to 21,706; the bar is 21,891). By half hour (proved/runs at L0, CPU hours):

| window | P2N L0 | P2O L0 | P2O L1 (class h) |
|---|---|---|---|
| 60–90 | 833/2,368, 2.4 h | 927/2,037, 1.9 h | 11/28, 0.5 h |
| 90–120 | 246/1,854, 2.4 h | **528**/1,671, 1.9 h | 3/24, 0.5 h |

In 90–120 P2O proved twice P2N's L0 goals with fewer runs. The mix lines say where: P2O's retry class q yields 165
an hour against P2N's 50 (the retries --knn-ctx flags have a new lemma in their kNN context). Its kNN-only retries
so far: 240 dispatched, 48 proved (20%), none waiting. Class h costs about 1 CPU hour an hour for 14 proofs since 60
minutes. The machine: load about 26 CPUs of mine (2 × 6 workers, the side loops, stepjlive3's join checks), 10 GB.

## A correction: compare across time by abstract work, not wall minutes (21 Nov 07:20)

P2N's bar (P2J + 185 at 5 hours) compares arms run at different times. The curves are by wall minutes, and the
machine's speed per abstract second follows its load: failed plain 5 s L0 runs took on average 5.6-6.0 CPU s in
P2K, P2H and P2J (three arms at night) and 4.7-5.0 s in P2N and P2O. By 120 minutes P2N had made 23,738 runs, P2J
22,082. Only P2O against P2N (side by side) is fair by wall time.

exp/abscurve.py turns each run's CPU time into abstract seconds with its arm's CPU per abstract second in the same
15-minute window (the median over that window's failed plain 5 s L0 runs), and compares arms at equal abstract
worker time. At P2N's 60, 120 and 150 minutes (5.6, 11.6 and 14.5 abstract worker hours):

| arm | 5.6 h | 11.6 h | 14.5 h |
|---|---:|---:|---:|
| P2K | 19,408 (70 min) | 20,071 (145) | 20,256 (182) |
| P2H | 19,326 (70) | **21,021** (143) | **21,354** (178) |
| P2J | 19,512 (70) | 20,275 (146) | 20,860 (182) |
| P2N | 19,214 (60) | 20,872 (120) | 21,148 (150) |
| P2O | 18,847 (61) | 20,961 (122) | 21,297 (152) |

At equal work P2N is 597 ahead of P2J at 11.6 hours but 149 behind P2H, which then led because its first hour
cost less per run. The calibration is coarse (the main thread's share of a run is not scaled; a first mean-based
version was thrown off by Z6's first window, 17 failed runs of which four took 50-73 s). It is still fairer than
wall minutes across nights.

**The decision, restated:** at P2J's abstract work at 300 minutes, P2N against the better of P2H and P2J
(`abscurve.py sets/half2 P2J P2H P2N P2O --at 300`). If P2N reaches that work before its own end, the comparison is
at that wall time, else at its end (which then favours P2J and P2H). P2O against P2N stays by wall time. Z7 against
Z6 needs the same correction.

## Interim at 3 hours (21 Nov 07:37)

By wall minutes (side by side, fair for P2O against P2N):

| arm | 120 min | 150 min | 180 min |
|---|---:|---:|---:|
| P2K | 20,004 | 20,075 | 20,224 |
| P2H | 20,611 | 21,086 | 21,355 |
| P2J | 20,124 | 20,282 | 20,770 |
| P2N | 20,872 | 21,148 | 21,271 |
| **P2O** | 20,934 | 21,286 | **21,524** |

At equal abstract work (abscurve, P2N's 180 minutes = 17.4 abstract worker hours): P2N 21,266, P2H 21,457 (at 213
minutes), P2J 21,462 (216), P2K 20,580 (217); P2O had 21,524 with a little less work.

* **P2O leads P2N by 253**, above the +185 rule. P2N has nearly stalled: +123 in 150–180 minutes, its mix line's
  yields r 19, d 12 and q 1 an hour (P2O: r 62, d 43, q 62, h 17). In 150–180 minutes P2N's L0 runs proved 43 of
  1,638, P2O's 142 of 1,461.
* **At equal work the pair alone (P2N) is about 190 behind each of its options alone.** The two do not stack; with
  --knn-ctx and --head-class added (P2O) the set leads.
* Where P2O's lead comes from: not mainly the kNN-only retries (274, 48 proved, 43 of them in the first hour; 5 of
  71 since). Its L1 runs: 152, 48 proved (class h), against P2N's 34 and 16. A proved head gives the goals after it
  a new nearest sibling, so their L0 retries follow; P2O's L0 runs proved 352 in 120–180 minutes against 190.

## Interim at 4 hours (21 Nov 08:37)

| arm | 180 min | 210 min | 240 min |
|---|---:|---:|---:|
| P2K | 20,224 | 20,546 | 20,828 |
| P2H | 21,355 | 21,444 | 21,525 |
| P2J | 20,770 | 21,374 | 21,624 |
| P2N | 21,271 | 21,317 | 21,370 |
| **P2O** | 21,524 | 21,615 | **21,686** |

At equal abstract work (P2N's 210 and 240 minutes = 20.5 and 23.6 abstract worker hours): P2H 21,531 and 21,590
(at 248 and 282 minutes), P2J 21,636 and 21,683 (250, 283), P2N 21,317 and 21,370, P2O 21,618 at 20.5 hours and
21,686 now with a little less than 23.6.

* P2O leads P2N by 316 side by side. At equal work it ties P2J and leads P2H by about 100; P2N trails both by
  220-310. The two options together are worse than either alone, and --knn-ctx with --head-class win that back.
* Both arms are flattening: P2O +71 in 210-240 minutes (L1 0 of 22, V@0 1 of 300), P2N +53. On half2 the late phase
  is short of the other half's lemmas (notes/2026-11-21-roots.md), so the sets/all run (Z7) decides what the late
  options are worth.

## Result at 5 hours (21 Nov 09:38)

| arm | 240 min | 270 min | 300 min |
|---|---:|---:|---:|
| P2K, the control | 20,828 | 21,066 | 21,142 |
| P2H, --retry-class | 21,525 | 21,571 | 21,597 |
| P2J, --yield-discount 2000 --reexplore 12:0.25 | 21,624 | 21,673 | 21,706 |
| P2N, both | 21,370 | 21,446 | 21,698 |
| **P2O, both + --knn-ctx 10 --head-class** | 21,686 | 21,736 | **21,939** |

At P2J's abstract work at 240 and 300 minutes (19.6 and 25.1 abstract worker hours; abscurve.py, reference P2J):
P2J 21,624 and 21,706; P2H 21,522 (238 min) and 21,597 (299); P2N 21,309 (201) and 21,381 (255); **P2O 21,593
(202) and 21,706 (255)**. P2N and P2O reached P2J's 5 hours of work at 255 minutes: the machine was about 15% faster
per abstract second than during exp44/45.

* **P2O against P2N (side by side): +241** (+384 / −146, union 22,086). Over the +185 rule: `--knn-ctx 10
  --head-class` add to the pair. abs/after48.sh starts exp49/50 on P2O's options.
* **P2N against the better of P2H and P2J at equal work: −325.** The pair alone fails its rule; the two late-phase
  options do not stack by themselves.
* **P2O against P2J at equal work: a tie** (21,706 each); +362 / −128 by the end, union 22,068. All five arms'
  union 22,211.
* Both arms had a late burst in 270–300 minutes (P2N +252, P2O +203; L0 154 and 174, L1 20 and 8).
* Mix lines at the end: P2O r 45, d 14, q 131, h 13 an hour (301 head runs); P2N r 43, d 22, q 9.

**Decision.** solve_new.sh's late-phase default is P2O's set (`--retry-class --yield-discount 2000 --reexplore
12:0.25 --knn-ctx 10 --head-class`): best side by side, and tied with the best single option at equal work. Half2
lacks the other half's lemmas, which caps its late phase, so Z7 on all goals is the real test. The defaults change
after exp49/50, together with their winners, before Z7.

## Installed as the default (21 Nov 12:20)

solve_new.sh has a new variable LATE, default `--retry-class --yield-discount 2000 --reexplore 12:0.25 --knn-ctx 10
--head-class` (P2O's set), passed to loop.py before LOOPARGS; `LATE=` gives the 20 Nov system. Running arms use their
own copies of the script (or_test2.sh copies it at launch), so exp49/50 is unaffected. Smoke test loops/LTD (12:19,
smoke487, 2 workers, 3 minutes, LOOPARGS `--head-class --retry-time 3`, so one option given twice): no errors, 351
solved, the mix line with classes q and h. exp49/50's winners join LATE at about 14:50.

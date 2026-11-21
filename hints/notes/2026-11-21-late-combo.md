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

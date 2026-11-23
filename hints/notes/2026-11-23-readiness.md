# How long a ready goal waits, and whether kNN readiness should order the first runs

Written 23 Nov 2026, 04:54 UTC (offline, on Z8's rows; no twee runs).

## Question

Late in a from-zero run most of the CPU goes to goals that fail (notes/2026-11-23-z9.md, "Context"). Do goals sit
ready (their proof's lemmas already proved) for long before the run that proves them? If so, a faster trigger or
another order for the queue would move proofs earlier, and earlier proofs feed others.

## Setup

* exp/triglag.py Z8 --from 120: Z8's main-loop proofs found at 120 minutes or later (r1/results.tsv). For each, the
  goals its printed proof uses as lemma axioms (loops/Z8/proofs/<goal>, names ending in a goal of sets/all), and the
  latest of their proof times (the first THM row's t=, or else the hints file's mtime against config.json): the
  trigger. The lag is the proving run's time minus the trigger.
* exp/fresh_ready.py Z8 --from 60 --to 360: every goal's first main-loop run in minutes 60-360, against the goals of
  its axiom key proved before the run. Signals: s1 and s10, the highest and the 10th highest kNN similarity
  (lemmas.LemmaIndex's idf-weighted Jaccard of goal features, idf fixed over all the key's goals); n30, how many goals
  proved in the 30 minutes before score above the 10th highest of those before (--knn-ctx's test, for a goal never
  run); gap, the places after the nearest goal proved below it in its original (the loop's order for first runs).
  AUC of each for the run's success, and the success of the top quarter of the hour's first runs by each.

## Result

**Retries are prompt.** Of 3,348 proofs at 120 minutes or later, 2,243 came at the goal's first run; 593 used a lemma
proved after the goal's last failed run, 473 used only lemmas proved before it, 39 no proved goal at all. In the
593, the proving run came 3/8/16/30/50 minutes after the trigger (deciles 10/25/50/75/90), and in 593 of 593 it was the first
run on the goal after the trigger. Up to 10 minutes of that is the kNN rebuild (--knn-refresh 600), the rest the
queue; there is little to gain from a faster trigger. (Proof times from hints mtimes are those of a goal's latest
proof, so a few lags come out negative: 3 of the Vk200@0 ones.)

**First runs wait longer:** for 2,190 first-run proofs with a proved-goal lemma the deciles are 6/16/40/98/147 minutes after the
trigger. But readiness by kNN does not pick them out:

| hour | runs | proved | AUC s1 | AUC s10 | AUC n30 | AUC -gap | AUC s10+n30 | top 25% by s1 | top 25% by s10 | top 25% by n30 | top 25% by -gap | top 25% by s10+n30 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 4,111 | 2,555 (62%) | 0.551 | 0.505 | 0.552 | 0.567 | 0.532 | 69% | 64% | 68% | 67% | 67% |
| 2 | 2,800 | 1,379 (49%) | 0.600 | 0.563 | 0.590 | 0.613 | 0.588 | 63% | 60% | 61% | 62% | 62% |
| 3 | 1,505 | 425 (28%) | 0.527 | 0.464 | 0.597 | 0.633 | 0.514 | 33% | 25% | 42% | 35% | 31% |
| 4 | 1,872 | 314 (17%) | 0.592 | 0.556 | 0.576 | 0.729 | 0.574 | 24% | 22% | 32% | 32% | 23% |
| 5 | 1,223 | 77 (6%) | 0.554 | 0.501 | 0.554 | 0.735 | 0.510 | 9% | 6% | 9% | 13% | 6% |
| all | 11,511 | 4,750 (41%) | 0.575 | 0.523 | 0.658 | 0.730 | 0.591 | 51% | 47% | 62% | 58% | 54% |

* The gap order has the highest AUC in every hour (0.567-0.735), and 0.730 over all hours. The best kNN signal, n30,
  has 0.658 over all hours (its top quarter proves 62% against the gap order's 58%, because n30 is large in hour 1,
  when most first runs prove), and within an hour 0.552-0.597. n30's top quarter beats the gap order's only in
  hour 3 (42% against 35%); in hours 4 and 5 it ties or trails (32% and 32%, 9% and 13%).
* s1 and s10 are near chance (0.46-0.60 within an hour). Why the similarity of the goals proved so far says so
  little is open.

## Decision

No change: the first-run order stays the gap order, and --knn-refresh stays at 600 s. A combined order (gap, then
n30) would move a few points of precision in hours 3-4 on about 3,400 runs, tens of proofs, below what an A/B can see.

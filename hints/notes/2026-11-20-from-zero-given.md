# From zero with the derived-rule transfer (exp40)

Written 20 Nov 2026, 07:10 UTC.

## Why

* The user's goal is a system that solves as many problems as possible in as little time as possible. The last
  measurement from zero is exp29's PGD: sets/half1 from loops/EMPTY with solve_new.sh's defaults (since 19 Nov
  12:41), on 6 workers. It proved **19,309 at 2 hours**. Identical runs differ by about 185.
* Since then the tail methods were all developed on production:
  * exp38's derived-rule transfer (notes/2026-11-20-given-transfer.md): unsolved goals that are variants of rules
    other runs derived, from successful runs' logs and, via loop.py `--given-scan`, from failed runs' given rules,
    run by givenmatch.py live with the rule's ancestry as hints;
  * the same-statement finder (2ar redone).
* On production the live loop proved 27 of 49 in its first 75 minutes (0.38 CPU h). Then the hit stream thinned: 19
  new goals in production's failed runs from 04:15 to 05:00, 17 from 05:00 to 06:00, 1 from 06:00 to 07:00.
* A bound from PGC's logs (19 Nov, from zero): of the 7,020 goals it left unsolved, 109 were variants of rules its
  successful runs had derived, 89 of them from another original. Failed runs add more. Proofs then cascade through
  the pools and the transfer.
* So: does the transfer help from zero, where failed runs of weak theories are many and early?

## Set and setting

* **PGE (the arm):** exp29's PGD exactly (abs/exp29.sh options through abs/or_test.sh; solve_new.sh unchanged since
  PGD), plus the following.
  * `--given-scan /project/hintwork/loops/PGE_GF` (about 6% more twee time on failed runs).
  * `givenmatch.py live loops/PGE_GML --dst PGE --dirs PGE,PGE.xfer --gfail PGE_GF --set sets/half1 --every 300 -j 2`,
    with production's transfer options (rm4t, 6 + 30 lemmas, the original's pool, twee-pg61).
  * Script abs/exp40.sh (hints/exp/exp40.sh).
* **Control:** PGD as it ran on 19 Nov (no new control, to save 8 CPUs).
* **CPUs:** PGE 6 workers, its transfer 2 at times, its live loop 1 plus 2 at times. Production goes to 4 workers
  meanwhile (ul74 at J=4), next to the climber's 4, the transfer loop's 2 and the live loop's 2.
* **Caveat:** loop.py has changed since PGD only by options that are off here (--reexplore, sk, pw, hl, mX,
  --given-scan). The machine's load differs from 19 Nov.

## Measures

* `abs/setcurve.py sets/half1 PGD PGE --at 10,30,60,90,120`.
* The live loop's proofs and CPU (loops/PGE_GML/transfer.tsv) and the scan's hits (loops/PGE_GF/hits.tsv).
* One-arm goals against PGD.
* If PGE gains clearly (say 300 or more at 2 hours), --given-scan and the live loop go into solve_new.sh's defaults.

## Run

* Started 07:06:01 (loops/PGE, loop PID 3156431 with `--given-scan`, its live loop 3156433). Production went to J=4
  at 07:06 (ul74, rows from 216,723; the J=12 log is loops/UL74a.log).
* The live loop's first cycle: 19,249 target keys (half1's unsolved unit goals at the start).
* **07:15, the live loop's 2nd cycle: 4,086 new logs, 4,827 failed-run hit rows, 3,975 goals hit.** From zero,
  most unsolved goals are steps or derived rules of other runs, and the loop would prove nearly all of them at its
  first level anyway. At 20 s on 2 workers, the cycle would have taken 11 hours. Stopped at 07:16 before any run.
* **The fix** (givenmatch.py live, installed 07:20):
  * a hit waits in a pending queue until the loop has a failed run of its goal (a NO row in its results, read
    incrementally);
  * at most 60 goals run per cycle (`--cap`), oldest first;
  * `--no-inst` skips the instance scan, which found nothing new on production and doubled the scan's time.
  Production's unsolved goals have all failed and its hits are few, so it is unchanged there.
* Restarted at 07:20 (abs/exp40live.sh, which ends with the arm). The scan hit file is read again from the start, and
  so are the logs since 07:06.
* So far PGE differs from PGD only by `--given-scan` and the live loop's scans. No live-loop run went into the loop
  before 07:20.
* **07:17-07:21, the restarted loop's 1st cycle:** 10,643 logs rescanned since 07:06, and 888 goals hit, of which 0
  had failed in PGE (it had 83 failed runs then), so 888 pending. But the same-statement finder had no such filter:
  808 free candidates, and it ran 150 of them (about 130 proved, mostly in under a second) into PGE before I stopped
  it at 07:21. Those proofs are part of PGE, at about minute 12-15.
* The same filter (failed in the loop) and cap now apply to the same-statement candidates. Restarted at 07:22; the
  pending queue is rebuilt from the rescan.

## Interim (60 minutes, 08:07)

| minutes | 10 | 20 | 30 | 45 | 60 |
|---|---:|---:|---:|---:|---:|
| PGC (19 Nov) | 11,704 | 15,080 | 16,980 | 17,934 | 18,545 |
| PGD (control) | 10,314 | 14,300 | 16,540 | 17,976 | 18,713 |
| PGE | 11,695 | 15,293 | 17,003 | 18,070 | **18,849** |

* +136 against PGD and +304 against PGC, at about the noise between identical runs (185 at 2 hours).
* The live loop has proved 413 of its 517 runs in 1.1 CPU h, including the 131 early same-statement proofs. With the
  failed-in-loop filter it runs 60 goals a cycle (the cap binds), and 58 of 60 proved in cycle 7. 141 hits are
  pending. Some of these proofs the loop would have found later by itself; the 2-hour count and the one-arm goals
  will show how many.

## Results (2 hours, ended 09:06)

`abs/setcurve.py sets/half1 PGC PGD PGE --at 10,20,30,45,60,90,120`:

| minutes | 10 | 20 | 30 | 45 | 60 | 90 | 120 |
|---|---:|---:|---:|---:|---:|---:|---:|
| PGC (19 Nov) | 11,704 | 15,080 | 16,980 | 17,934 | 18,545 | 18,834 | 18,917 |
| PGD (control) | 10,314 | 14,300 | 16,540 | 17,976 | 18,713 | 19,216 | 19,309 |
| PGE | 11,695 | 15,293 | 17,003 | 18,070 | 18,849 | 19,425 | **19,591** |

* **+282 against PGD at 2 hours** (+136 at 60 minutes, +209 at 90), and +674 against PGC. Identical runs differ by
  about 185, and exp29's +392 on half1 did not replicate on half2 (exp30: −118). So this one half1 run alone is
  suggestive, not conclusive.
* **More CPU.** PGE had 12 CPU h of loop workers (the scan included), like PGD, plus 2.97 CPU h of live-loop twee time
  (901 runs). At equal CPU, PGE's curve near 96 minutes (about 19,460) is about +150 over PGD at 120.
* **The live loop:** 614 of 901 runs proved, 2.97 CPU h:

  | kind | runs | proved | CPU h | per CPU h |
  |---|---:|---:|---:|---:|
  | the rule's ancestry, 20 s | 478 | 434 | 0.55 | 790 |
  | the log's prefix, 40 s | 44 | 26 | 0.49 | 53 |
  | same statement, stronger theory, 20 s | 379 | 154 | 1.93 | 80 |

* **The live proofs add to the loop's, they do not replace them.** PGE's proofs by half hour, by who proved them:

  | minutes | 0-30 | 30-60 | 60-90 | 90-120 |
  |---|---:|---:|---:|---:|
  | PGE's loop | 16,819 | 1,654 | 412 | 92 |
  | PGE's live loop | 183 | 192 | 165 | 74 |
  | PGD (all) | 16,540 | 2,173 | 503 | 93 |

  In the last half hour the loop made 92 on 3 CPU h, as PGD did (93), and the live loop 74 more on about 0.85 CPU h.
* **One-arm goals:** only PGE 643, only PGD 368, union 19,961 (+370 over PGE alone). 308 of the 643 are live-loop
  proofs; the other 335 are cascades from them (siblings and lemmas). Against PGC and PGD together: 447 PGE-only goals,
  union of the three 20,016.
* **The scan:** 2,023 failed runs derived an unsolved goal; 15,767 hit rows for 3,925 goals, most of them proved by the
  loop itself later (the pending queue held them until a failed run of the goal).
* **The cycles grew long:** 300 s was the plan, but cycles 9-11 took 16-23 minutes, mostly in the same-statement runs
  (20 s each on 2 workers). The ancestry runs are the cheap, productive ones. 51 hits were pending at the end.

## Decision (09:13)

* **solve_new.sh: GIVEN=1 is the default** (the scan plus the live loop, as in PGE). The gain is +282 at 2 hours, and
  the live proofs come at 3 times the loop's late rate per CPU hour.
* `givenmatch.py live --loops DIR` lets the loop dirs be outside /project/hintwork/loops (the hits' loop column is
  relative to it). A 9-minute test on 21 goals (/project/hintwork/sn_test/SNG1) checks the plumbing.
* **Next:** replicate on half2 against exp30's P2D (19,383), as exp41.
* Then: the ancestry runs first, with a higher cap, and the same-statement runs in their own budget.

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

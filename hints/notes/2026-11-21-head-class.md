# exp47: heads at L1 as a class of their own (`--head-class`) (21 Nov 01:40)

**Question.** From zero, the 40 s chain level L1 nearly stops after the first hour (Z6: 16 L1 runs in 8 hours).
Do the heads (the goal right after a proven sibling) fall at L1 when they get it? Mine, from the roots test
(notes/2026-11-21-roots.md).

## Why

* At Z6's end, 7,689 goals were unsolved, 1,120 of them heads; **production proved 875 of those 1,120**. Z6 ran L1
  16 times, 3 of them on these heads.
* Of the 190 roots (production proofs whose recorded lemmas Z6 all had), 138 are heads in Z6's final state.
  loops/ROOTS/t40 runs them fresh at 40 s in Z6's final context: 38 of 61 proved at 01:38 (62%; the roots are
  goals production proved, so this is an upper end, not the heads' base rate).
* With `--ratio-order` a goal's next level is its open level with the best label estimate (loop.py nxt), and the
  deep list is sorted by that estimate. L1's estimate stays near its prior (1.73 per CPU hour with a prior weight of
  2 CPU hours; it ran 0.18 CPU hours, 9 of 16 proved), below the 5 s variants', so a head runs every 5 s variant
  first, and L1 entries come last behind thousands of variant entries. exp45 (P2J: a discounted estimate and
  re-exploration) may not lift it: the discount keeps every label's measured CPU small, so the prior weighs more.

## Change

loop.py `--head-class` (with --mix; default off): at each full pass the goals with gap place 1 (gaps(): the goal
right after the nearest proven goal below) whose next own cascade level is L1 in their current context are taken out
of the deep list into class h, nearest (in proof lines) first, and run at L1 (the chain level). Class h has the
--mix floor (0.1 of the workers while it has goals) and its own yield over its last 300 runs; deep-level runs
(d and h together) keep the --reserve. Also: a light pass now counts rq and hq as waiting work (before, a run with
only rq left forced a full pass at every step).

## Smoke tests

* loops/HCT (01:40, sets/smoke487, 2 workers, 12 minutes, `LOOPARGS=--head-class`): no errors, 395 solved, but class
  h never ran: among the classes with nothing running the first in the list wins, h is last, and with 2 workers r and
  d always had goals. With 6 workers each class gets a slot.
* loops/HCT2 (01:53, the same with 6 workers, 9 minutes): no errors, 408 solved; h ran 20 L1 runs, 12 proved
  (`mix ... h 14 50/h`).

**Launch (02:03):** abs/after4445d.sh starts P2M (LOOPARGS from loops/P2M.args, else `--head-class`) and P2L
together when loops/exp4445.done appears; production at J=4 meanwhile (two arms of about 10 CPUs each).

## Plan

P2M: sets/half2 from zero, abs/or_test2.sh, 6 workers, 5 hours, beside P2L when exp44/45 end, with the same base as
P2L (loops/P2L.args decides: if `--retry-class` holds at 5 hours both arms get it and P2H is the control, else P2K).
Measures: setcurve at 30-300 minutes; windows.py (class h's runs and proofs per half hour); L1 runs and proofs;
the h class's yield in the mix line.

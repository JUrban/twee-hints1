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

# What `--no-proof` saves in a search run (21 Nov 23:58)

**Question.** The loops search with `--quiet --no-proof`, and exp/proofq.py reruns every proved run with the proof
printed (the user, 20 Nov: "running with --no-proof and --quiet is good when we are searching for the proof; but do
re-run with the proof option on when you get the proof"). The reruns now take about 3 CPUs (4,100 jobs an hour at
-j 3) and fall behind: 131,363 jobs were queued at 21:51. How much CPU does `--no-proof` save in the search?

## The code

In twee (executable/SequentialMain.hs), the `proof` flag is read in one place, line 1618: `when (solved state &&
flags_proof) $ later $ do ...`, the presentation of the proof after a successful search. The search itself is the same
code with or without it, and a failed run never reads the flag.

## Measurement

exp/proofcost.py: 42 queued proof jobs, 7 each from loops/Z7, Z7.xfer, Z7_GML, P2T, P2U and P2T.xfer (random, seed 8),
copied out of the queue. Each was run with proofq's command (proof on) and with `--no-proof` added (the search run's
command), one after the other on one CPU, with the CPU time from the child's resource usage. Rows (dir, goal, budget,
CPU with proof, CPU without, proved, proved, same output outside the proof block, proof bytes):
notes/2026-11-21-proof-cost.tsv.

| dir | jobs | CPU s with proof | CPU s with --no-proof |
|---|---:|---:|---:|
| Z7 | 7 | 12.80 | 12.11 |
| Z7.xfer | 7 | 3.94 | 3.84 |
| Z7_GML | 7 | 37.20 | 38.29 |
| P2T | 7 | 1.46 | 1.42 |
| P2U | 7 | 4.05 | 3.88 |
| P2T.xfer | 7 | 1.66 | 1.67 |
| **all** | **42** | **61.1** | **61.2** |

* All 42 proved in both. In all 42 the output outside the proof block was the same, so the search is the same.
* The proofs were up to 69 KB (nsmr_to_aK1__goal_472, a 21.6 s run): presenting a proof costs no measurable CPU,
  even for the largest.
* A first attempt (30 jobs, seed 7) mostly measured nothing: 25 of the commands use paths relative to
  /project/hintwork, which the copy did not rewrite, so twee stopped at once. Its 5 Z7_GML jobs (absolute paths)
  gave 46.7 s with the proof against 47.8 s without.

## Consequence

A search run with the proof on costs the same as with `--no-proof`. The rerun therefore spends a full second run on
every proved job (about 2.6 CPU s on average), which is the whole cost of proofq. Printing the proof in the search
run (dropping `--no-proof` from loop.py's runs and cutting the proof from their output, as proofq does) would keep
the same proofs for no extra CPU and leave the queue only for the jobs already in it.

This changes a method the user set, so the current way (search `--no-proof`, proofq reruns) stays until the user
agrees.

## Prepared, not switched on (22 Nov 01:00)

loop.py `--proof-in-search` (0ae814a, off by default): search runs drop `--no-proof`; a proved run that printed its
proof keeps it at once in DIR/proofs/<goal> (and the live destination's proofs/), cut as proofq.py cuts it, through
a temp file and a rename; a proved run without a printed proof (a Prover9 variant) is still queued for proofq.
transfer.py runs twee through loop.Loop.run_one, so its loops take the option among their loop options too.

Smoke PIS (sets/smoke487 from zero, 2 workers, 6 minutes, LOOPARGS=--proof-in-search, 22 Nov 00:54-01:00): 473
runs, 387 goals proved, 387 proofs kept in loops/PIS/proofs, each ending in the RESULT line, 0 jobs in
loops/PIS/proofq, no keep-proofs errors. Its transfer loops (without the option) queued 5 jobs as before.

Switching on is one line in solve_new.sh (the main and transfer loops' options), once the user agrees.
